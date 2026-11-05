package com.bbyq.personal;
import android.app.Activity;
import android.content.Intent;
import android.widget.*;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.*;
import org.junit.runner.RunWith;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import static org.junit.Assert.*;
@RunWith(AndroidJUnit4.class)
public class PersonalEngineTest {
 @Test public void existingNativeModelsAndPersistence()throws Exception {
  android.content.Context base=InstrumentationRegistry.getInstrumentation().getTargetContext();
  final File testRoot=new File(base.getCacheDir(),"native-engine-"+System.nanoTime());assertTrue(testRoot.mkdirs());
  android.content.Context c=new android.content.ContextWrapper(base){@Override public File getFilesDir(){return testRoot;}};
  PersonalEngine e=new PersonalEngine(c);
  String json;try(InputStream in=c.getAssets().open("engine/chat-fixtures.json");ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] b=new byte[4096];int n;while((n=in.read(b))!=-1)out.write(b,0,n);json=out.toString("UTF-8");}
  JSONArray cases=new JSONArray(json);
  assertTrue(e.chat("calcula 17 + 25").contains("42"));
  assertTrue(e.chat("que es ingreso y que requiere?").contains("importe obtenido"));
  e.chat(cases.getJSONObject(4).getString("input"));
  assertTrue(e.chat("que es prueba movil y que requiere?").contains("una leccion personal de X"));
  assertTrue(e.messages().length()>=8);
  assertTrue(e.exportHistory().contains("prueba movil"));
  String before=e.stateHash();try{e.chat("");fail("Empty input must fail");}catch(IOException expected){}assertEquals(before,e.stateHash());
  JSONObject status=e.quantumStatus();assertEquals(1000,status.getInt("qubits_per_agent"));assertEquals(10000,status.getInt("vqc_episodes"));assertEquals(10000,status.getInt("qrl_episodes"));
  assertTrue(e.quantumAction().length()>0);
  JSONObject trained=e.trainEpisode();assertEquals(10001,trained.getInt("qrl_episodes"));assertEquals(10000,trained.getInt("vqc_episodes"));
  e.close();PersonalEngine reopened=new PersonalEngine(c);assertEquals(before,reopened.stateHash());assertEquals(10001,reopened.quantumStatus().getInt("qrl_episodes"));reopened.close();
 }
 @Test public void realChatScreenSendsToNativeEngine()throws Exception {
  android.app.Instrumentation i=InstrumentationRegistry.getInstrumentation();
  Intent intent=new Intent(i.getTargetContext(),MainActivity.class);intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
  Activity a=i.startActivitySync(intent);i.waitForIdleSync();
  EditText input=(EditText)a.findViewById(R.id.message_input);Button send=(Button)a.findViewById(R.id.send_button);
  long limit=System.currentTimeMillis()+30000;
  while(System.currentTimeMillis()<limit){TextView s=a.findViewById(R.id.engine_status);if(s.getText().toString().contains("Disponible"))break;Thread.sleep(200);}
  i.runOnMainSync(()->{input.setText("calcula 17 + 25");send.performClick();});
  boolean found=false;limit=System.currentTimeMillis()+45000;
  while(System.currentTimeMillis()<limit){
   JSONArray messages=PersonalEngine.get(i.getTargetContext()).messages();
   if(messages.length()>0){JSONObject last=messages.getJSONObject(messages.length()-1);if(last.optString("role").equals("assistant")&&last.optString("text").contains("42")){found=true;break;}}
   Thread.sleep(200);
  }
  assertTrue("UI must display a native arithmetic response",found);i.runOnMainSync(a::finish);
 }
}
