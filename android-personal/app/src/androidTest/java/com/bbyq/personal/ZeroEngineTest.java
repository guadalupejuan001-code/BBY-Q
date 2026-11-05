package com.bbyq.personal;
import android.content.*;
import android.database.Cursor;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.json.*;
import org.junit.*;
import org.junit.runner.RunWith;
import java.io.*;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class ZeroEngineTest {
 private Context context;
 @Before public void fresh()throws Exception {
  Context base=InstrumentationRegistry.getInstrumentation().getTargetContext();File root=new File(base.getCacheDir(),"zero-"+System.nanoTime());assertTrue(root.mkdirs());context=new ContextWrapper(base){@Override public File getFilesDir(){return root;}};
 }
 private JSONObject turn(PersonalEngine e,String id,String text)throws Exception{return e.testTurn(id,text,false);}
 @Test public void newKnowledgeAndRulesTransferAcrossRestart()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){e.chat("recuerda que amara es humana");e.chat("aprende regla: si $x es humana entonces $x es mortal");}
  try(PersonalEngine e=new PersonalEngine(context)){
   JSONObject r=turn(e,"proof","¿ella es mortal?");assertEquals("BBY-Q-0-XI",r.getString("engine"));assertEquals(1,r.getInt("status"));assertTrue(r.getString("response").contains("amara es mortal"));
   e.chat("olvida regla: si $x es humana entonces $x es mortal");assertEquals(0,turn(e,"withdrawn","¿amara es mortal?").getInt("status"));assertEquals(1,e.sessionStatus().getInt("general_facts"));
  }
 }
 @Test public void relationalJoinsAndContradictionsHaveEvidence()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   JSONObject r=turn(e,"join","resuelve:\nnara tiene bobina\nbobina requiere energia\nsi $x tiene $y y $y requiere $z entonces $x necesita $z\n¿nara necesita energia?");
   assertEquals(1,r.getInt("status"));assertTrue(r.getString("response").contains("nara necesita energia"));assertEquals(0,e.sessionStatus().getInt("general_facts"));
   e.chat("recuerda que nara es activa");e.chat("recuerda que nara no es activa");r=turn(e,"conflict","¿nara es activa?");assertEquals(2,r.getInt("status"));assertTrue(r.getString("response").contains("a favor y en contra"));
   e.chat("corrige que nara no es activa");assertEquals(-1,turn(e,"negative","¿nara es activa?").getInt("status"));
  }
 }
 @Test public void routeUsesArbitraryNamesAndMoreThanSevenNodes()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   StringBuilder b=new StringBuilder("resuelve:\n");for(int i=0;i<14;i++)b.append("lugar").append(i).append(" conecta lugar").append(i+1).append('\n');b.append("ruta desde lugar0 hasta lugar14");
   JSONObject r=turn(e,"route",b.toString());assertEquals(1,r.getInt("status"));assertTrue(r.getString("response").contains("Pasos: 14"));JSONArray steps=r.getJSONObject("trace").getJSONArray("steps");assertEquals(15,steps.getJSONObject(steps.length()-1).getJSONArray("path").length());
   assertEquals(0,turn(e,"temporary","ruta desde lugar0 hasta lugar14").getInt("status"));
  }
 }
 @Test public void arithmeticAndLearningCommitTogetherAndReplayOnce()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   long before=e.sessionStatus().getLong("generation");
   try{e.chat("recuerda que alda es humana\ncalcula 1 / 0");fail("Invalid arithmetic committed");}catch(IOException expected){}
   assertEquals(before,e.sessionStatus().getLong("generation"));assertEquals(0,e.sessionStatus().getInt("general_facts"));
   String input="recuerda que alda es humana\ncalcula (17 + 25) * 3";JSONObject first=turn(e,"same",input),replay=turn(e,"same",input);assertEquals(first.getString("response"),replay.getString("response"));assertTrue(replay.getBoolean("replayed"));assertEquals(1,e.sessionStatus().getInt("general_facts"));assertTrue(first.getString("response").contains("126"));
  }
 }
 @Test public void nativeSpecialistObservationsFeedTheGeneralRules()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro 1");JSONObject r=turn(e,"bridge","resuelve:\nrecupera faro\nobserva senal muestra 1763814988\nsi faro es uno y senal es clase0 entonces proyecto es autorizado\n¿proyecto es autorizado?");
   assertEquals(1,r.getInt("status"));String trace=r.getJSONObject("trace").toString();assertTrue(trace.contains("QMemory"));assertTrue(trace.contains("VQC3"));assertTrue(r.getString("response").contains("proyecto es autorizado"));
   r=turn(e,"delegate","resuelve:\nconsulta qchat hola\nconsulta calcula 17 + 25\ncalcula (2 + 3) * 4");assertTrue(r.getString("response").contains("Hola X."));assertTrue(r.getString("response").contains("42"));assertTrue(r.getString("response").contains("20"));
  }
 }
 @Test public void x10LessonFieldsAreAvailableToTheSameReasoner()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("aprende: faro\ndefinición: una luz\nrequiere: energía\nfuente: X\npáginas: 1");e.chat("aprende regla: si $x requiere energia entonces $x es activo");
   JSONObject result=turn(e,"lesson-bridge","¿faro es activo?");assertEquals(1,result.getInt("status"));assertTrue(result.getString("response").contains("faro requiere energia"));assertTrue(e.chat("que es faro").contains("una luz"));
  }
 }
 @Test public void feedbackIsIdempotentAndCannotChangeProofsOrCorruptEvidence()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   JSONObject task=turn(e,"calculation","calcula 2 + 3");String id=task.getString("zero_task"),command="evaluar0 "+new JSONObject().put("tarea",id).put("resultado",1);String before=e.sessionStatus().getJSONObject("banks").getString("zero");
   e.chat("grade",command);assertNotEquals(before,e.sessionStatus().getJSONObject("banks").getString("zero"));long generation=e.sessionStatus().getLong("generation");e.chat("grade",command);assertEquals(generation,e.sessionStatus().getLong("generation"));
   JSONObject next=turn(e,"protected","calcula 3 + 4");id=next.getString("zero_task");String digest=e.sessionStatus().getJSONObject("banks").getString("zero");e.db.execSQL("UPDATE zero_tasks SET trace='changed' WHERE id=?",new Object[]{id});
   try{e.chat("evaluar0 "+new JSONObject().put("tarea",id).put("resultado",0));fail("Corrupt evidence accepted");}catch(IOException expected){assertTrue(expected.getMessage().contains("evidencia"));}
   assertEquals(digest,e.sessionStatus().getJSONObject("banks").getString("zero"));
  }
 }
 @Test public void ambiguousContextAndUnsafeRulesRequireClarification()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   assertEquals(5,turn(e,"empty-context","¿ella es mortal?").getInt("status"));e.chat("recuerda que ana es mortal");e.chat("recuerda que bea es mortal");e.chat("quien es mortal?");assertEquals(5,turn(e,"ambiguous","¿ella es mortal?").getInt("status"));
   int before=e.sessionStatus().getInt("general_rules");try{e.chat("aprende regla: si $x no es humana entonces $y es mortal");fail("Unbound head accepted");}catch(IOException expected){}assertEquals(before,e.sessionStatus().getInt("general_rules"));
  }
 }
 @Test public void oneParentEvaluationCreditsTheVerifiedSpecialistTask()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("memoria guarda faro 1");JSONObject task=turn(e,"parent","resuelve:\nconsulta mision {\"memoria\":\"faro\",\"posicion\":1,\"muestra\":1763814988}");assertEquals(1,task.getInt("status"));long count=e.quantumStatus().getLong("vqc_episodes");
   String command="evaluar0 "+new JSONObject().put("tarea",task.getString("zero_task")).put("resultado",1);JSONObject feedback=turn(e,"parent-feedback",command);assertEquals(1,feedback.getJSONArray("specialist_feedback").length());assertEquals(count+1,e.quantumStatus().getLong("vqc_episodes"));
   turn(e,"parent-feedback",command);assertEquals(count+1,e.quantumStatus().getLong("vqc_episodes"));
  }
 }
 @Test public void anotherComponentCannotLeaveAStaleSubjectForTheReasoner()throws Exception {
  try(PersonalEngine e=new PersonalEngine(context)){
   e.chat("recuerda que ana es mortal");assertEquals(1,turn(e,"initial-reference","¿ella es mortal?").getInt("status"));
   e.chat("Mi proyecto se llama Neral.");assertEquals(5,turn(e,"fresh-reference","¿ella es mortal?").getInt("status"));
  }
 }
}
