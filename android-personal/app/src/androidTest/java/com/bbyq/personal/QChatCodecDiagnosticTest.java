package com.bbyq.personal;

import android.content.*;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.json.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import static org.junit.Assert.*;

/** Codec parity and every-bit circuit contracts on the frozen product. */
@RunWith(AndroidJUnit4.class)
public class QChatCodecDiagnosticTest {
 private Context base(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
 private JSONObject fixture()throws Exception {try(InputStream stream=InstrumentationRegistry.getInstrumentation().getContext().getAssets().open("qchat-codec-diagnostic.json")){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;while((n=stream.read(buffer))>=0)out.write(buffer,0,n);return new JSONObject(out.toString("UTF-8"));}}
 private JSONArray asset(String name)throws Exception {try(InputStream stream=base().getAssets().open("engine/"+name)){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;while((n=stream.read(buffer))>=0)out.write(buffer,0,n);return new JSONArray(out.toString("UTF-8"));}}
 private byte[] bytes(String raw){byte[] b=new byte[raw.length()];for(int i=0;i<b.length;i++)b[i]=(byte)(raw.charAt(i)-'0');return b;}
 private void emit(JSONObject report)throws Exception {android.os.Bundle b=new android.os.Bundle();b.putString("stream","\nQCHAT_CODEC_DIAGNOSTIC_BASE64="+android.util.Base64.encodeToString(report.toString().getBytes(StandardCharsets.UTF_8),android.util.Base64.NO_WRAP)+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(2,b);}
 @Test public void androidCodecMatchesFrozenPythonInputs()throws Exception {
  JSONObject fixture=fixture();Set<String> input=QuantumText.set(asset("qchat-input-vocabulary.json")),history=QuantumText.set(asset("qchat-history-vocabulary.json"));JSONArray rows=fixture.getJSONArray("codec_cases");assertEquals(128,rows.length());
  for(int i=0;i<rows.length();i++){JSONObject r=rows.getJSONObject(i);List<String> prefix=new ArrayList<>();JSONArray values=r.getJSONArray("prefix");for(int j=0;j<values.length();j++)prefix.add(values.getString(j));int[] actual=QuantumText.bits(r.getString("prompt"),prefix,r.getString("previous"),input,history);byte[] expected=bytes(r.getString("bits"));assertEquals(100,actual.length);for(int j=0;j<100;j++)assertEquals("codec case "+i+" bit "+j,expected[j],actual[j]);}
  emit(new JSONObject().put("test","android-python-codec-parity").put("cases",rows.length()).put("bits_checked",12800).put("passed",true));
 }
 @Test public void nativeCircuitPreservesEveryStagedInputBit()throws Exception {
  Context b=base();File root=new File(b.getCacheDir(),"codec-"+System.nanoTime());assertTrue(root.mkdirs());Context context=new ContextWrapper(b){@Override public File getFilesDir(){return root;}};JSONArray vectors=fixture().getJSONArray("native_vectors");assertEquals(118,vectors.length());
  try(PersonalEngine engine=new PersonalEngine(context);XiSession nativeSession=new XiSession(engine.bankState("qchat"))){
   String library=new String(engine.asset("qchat-model.xi"),StandardCharsets.UTF_8);
   for(int i=0;i<vectors.length();i++){
    byte[] raw=bytes(vectors.getString(i));StringBuilder code=new StringBuilder("#!reverse-pc-machine-v1\nbudget 50000000\n");for(int j=0;j<100;j++)XiPages.put(code,QuantumText.A+1000+j,raw[j],1);code.append("store64 ").append(QuantumText.A+80).append(" 0\ncall qchat_encode\nhalt\n").append(library);nativeSession.run(code.toString());assertArrayEquals("staging "+i,raw,nativeSession.bytes(QuantumText.A+1000,100));
    byte[] actual=nativeSession.bytes(QuantumText.A+2000,868),expected=new byte[868];System.arraycopy(raw,0,expected,0,100);for(int x=0;x<64;x++)for(int y=0;y<12;y++)expected[100+x*12+y]=(byte)(raw[x]*raw[88+y]);assertArrayEquals("native features "+i,expected,actual);
    nativeSession.run("#!reverse-pc-machine-v1\nbudget 50000000\nstore64 "+(QuantumText.A+80)+" 2\ncall qchat_encode\nhalt\n"+library);assertArrayEquals("analytic control "+i,actual,nativeSession.bytes(QuantumText.A+2000,868));
   }
  }
  emit(new JSONObject().put("test","android-native-staging-and-circuit").put("vectors",vectors.length()).put("native_feature_bytes_checked",118*868).put("passed",true));
 }
}
