package com.bbyq.personal;
import android.content.*;
import android.database.Cursor;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.json.*;
import org.junit.*;
import org.junit.runner.RunWith;
import java.io.*;
import java.nio.charset.StandardCharsets;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class EntityCycleTest {
 private Context context;
 @Before public void fresh()throws Exception {
  Context base=InstrumentationRegistry.getInstrumentation().getTargetContext();File root=new File(base.getCacheDir(),"entity-"+System.nanoTime());assertTrue(root.mkdirs());
  context=new ContextWrapper(base){@Override public File getFilesDir(){return root;}};
 }
 private JSONArray cases()throws Exception {
  try(InputStream in=InstrumentationRegistry.getInstrumentation().getContext().getAssets().open("entity-cases.json");ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return new JSONArray(new String(out.toByteArray(),StandardCharsets.UTF_8));}
 }
 private JSONObject mission(PersonalEngine e,String id)throws Exception {return e.testTurn(id,"mision "+cases().getJSONObject(0).getJSONObject("input"),false);}
 private String feedback(String task,int result)throws Exception {return "evaluar "+new JSONObject().put("tarea",task).put("resultado",result);}
 @Test public void allSpecialistsContributeToTheSameVerifiedTask()throws Exception {
  JSONArray fixtures=cases();
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro 0");String chat=e.stateHash();
   for(int i=0;i<fixtures.length();i++){
    JSONObject f=fixtures.getJSONObject(i);e.chat("memoria corrige faro "+f.getInt("bit"));
    JSONObject r=e.testTurn("mission-"+i,"mision "+f.getJSONObject("input"),false);
    assertEquals("E02-Entity-XI",r.getString("engine"));assertEquals(f.getString("response"),r.getString("response"));assertEquals(f.getInt("action"),r.getInt("action"));
    JSONObject trace=r.getJSONObject("trace");assertTrue(trace.getBoolean("voice_verified"));assertEquals(f.getInt("goal"),trace.getJSONObject("reasoning").getInt("goal"));assertTrue(trace.getJSONObject("memory").getBoolean("present"));
   }
   assertEquals(fixtures.length(),e.sessionStatus().getInt("entity_tasks"));assertEquals(chat,e.stateHash());
  }
 }
 @Test public void missingPremisesCauseARefusalBeforePlanning()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   JSONObject input=new JSONObject().put("memoria","ausente").put("posicion",3).put("muestra",620511);
   JSONObject r=e.testTurn("missing-memory","mision "+input,false);assertEquals(-1,r.getInt("action"));assertEquals("Necesito más información.",r.getString("response"));assertFalse(r.getJSONObject("trace").has("plan"));
   e.chat("memoria guarda faro 1");input=new JSONObject().put("memoria","faro").put("posicion",3);
   assertEquals(-1,e.testTurn("missing-data","mision "+input,false).getInt("action"));
  }
 }
 @Test public void replayAndFailurePublishNoExtraTaskOrLearning()throws Exception {
  String task,digest;long before;
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro "+cases().getJSONObject(0).getInt("bit"));JSONObject first=mission(e,"same-mission");task=first.getString("entity_task");
   assertEquals(task,mission(e,"same-mission").getString("entity_task"));assertEquals(1,e.sessionStatus().getInt("entity_tasks"));before=e.sessionStatus().getLong("shared_updates");digest=e.sessionStatus().getJSONObject("banks").getString("entity");
   try{e.testTurn("failed-feedback",feedback(task,1),true);fail("Rollback");}catch(IOException expected){assertEquals("Injected failure before commit",expected.getMessage());}
   assertEquals(digest,e.sessionStatus().getJSONObject("banks").getString("entity"));assertEquals(before,e.sessionStatus().getLong("shared_updates"));
  }
  try(PersonalEngine e=new PersonalEngine(context)){
   JSONObject prior=e.sessionStatus().getJSONObject("banks");long vqc=e.quantumStatus().getLong("vqc_episodes");JSONObject accepted=e.testTurn("accept-feedback",feedback(task,1),false);assertEquals(5,accepted.getJSONArray("learned").length());assertEquals(vqc+1,e.quantumStatus().getLong("vqc_episodes"));
   JSONObject next=e.sessionStatus().getJSONObject("banks");for(String name:new String[]{"entity","quantum","qmemory","entity-voice"})assertNotEquals(name,prior.getString(name),next.getString(name));
   assertEquals(before+1,e.sessionStatus().getLong("shared_updates"));e.chat("accept-feedback",feedback(task,1));assertEquals(before+1,e.sessionStatus().getLong("shared_updates"));
   try{e.chat(feedback(task,0));fail("Conflicting feedback accepted");}catch(IOException expected){}
  }
 }
 @Test public void feedbackForOlderTasksKeepsTheCurrentSharedModel()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro "+cases().getJSONObject(0).getInt("bit"));String a=mission(e,"older").getString("entity_task"),b=mission(e,"newer").getString("entity_task");long n=e.sessionStatus().getLong("shared_updates");
   e.chat(feedback(b,1));e.chat(feedback(a,0));assertEquals(n+2,e.sessionStatus().getLong("shared_updates"));
   try(Cursor c=e.db.rawQuery("SELECT count(*) FROM entity_tasks WHERE feedback IS NOT NULL",null)){assertTrue(c.moveToFirst());assertEquals(2,c.getInt(0));}
  }
 }
 @Test public void missionAndMemorySurviveRestartAndFailedTurns()throws Exception {
  int bit=cases().getJSONObject(0).getInt("bit");
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro "+bit);long generation=e.sessionStatus().getLong("generation");
   try{e.testTurn("failed-mission","mision "+cases().getJSONObject(0).getJSONObject("input"),true);fail("Rollback");}catch(IOException expected){assertEquals("Injected failure before commit",expected.getMessage());}
   assertEquals(generation,e.sessionStatus().getLong("generation"));assertEquals(0,e.sessionStatus().getInt("entity_tasks"));
   mission(e,"committed-mission");
  }
  try(PersonalEngine e=new PersonalEngine(context)){assertEquals(1,e.sessionStatus().getInt("entity_tasks"));assertTrue(e.chat("memoria consulta faro").contains("faro = "+bit));assertNotNull(e.lastEntityTask());}
 }
 @Test public void alteredEvidenceCannotTrainTheEntity()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro "+cases().getJSONObject(0).getInt("bit"));String task=mission(e,"protected-task").getString("entity_task");JSONObject before=e.sessionStatus().getJSONObject("banks");long generation=e.sessionStatus().getLong("generation");
   e.db.execSQL("UPDATE entity_tasks SET workspace=? WHERE id=?",new Object[]{new byte[352],task});
   try{e.chat(feedback(task,1));fail("Corrupt evidence accepted");}catch(IOException expected){assertTrue(expected.getMessage().contains("evidencia"));}
   assertEquals(generation,e.sessionStatus().getLong("generation"));assertEquals(before.toString(),e.sessionStatus().getJSONObject("banks").toString());
  }
 }
}
