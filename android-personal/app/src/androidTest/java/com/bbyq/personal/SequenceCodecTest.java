package com.bbyq.personal;

import android.content.*;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.json.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import static org.junit.Assert.*;

/** Test-only C1 execution; the product's existing QChat bank stays active. */
@RunWith(AndroidJUnit4.class)
public class SequenceCodecTest {
 private Context base(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
 private Context isolated()throws Exception {Context b=base();File root=new File(b.getCacheDir(),"sequence1-"+System.nanoTime());assertTrue(root.mkdirs());return new ContextWrapper(b){@Override public File getFilesDir(){return root;}};}
 private JSONObject fixture()throws Exception {try(InputStream stream=InstrumentationRegistry.getInstrumentation().getContext().getAssets().open("sequence1-codec.json")){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buffer=new byte[4096];int n;while((n=stream.read(buffer))>=0)out.write(buffer,0,n);return new JSONObject(out.toString("UTF-8"));}}
 private byte[] hex(String value){byte[] out=new byte[value.length()/2];for(int i=0;i<out.length;i++)out[i]=(byte)Integer.parseInt(value.substring(i*2,i*2+2),16);return out;}
 private String source(String body,String library){return "#!reverse-pc-machine-v1\nbudget 100000000\n"+body+"\nhalt\n"+library;}
 private void emit(JSONObject report)throws Exception {android.os.Bundle b=new android.os.Bundle();b.putString("stream","\nBBYQ_C1_CODEC_BASE64="+android.util.Base64.encodeToString(report.toString().getBytes(StandardCharsets.UTF_8),android.util.Base64.NO_WRAP)+"\n");InstrumentationRegistry.getInstrumentation().sendStatus(2,b);}
 @Test public void androidAndPythonRetainTheSameTextAndMeasuredFeatures()throws Exception {
  JSONObject f=fixture();SequenceCodec codec=new SequenceCodec(f.getJSONArray("vocabulary"));JSONArray cases=f.getJSONArray("codec_cases");assertEquals(128,cases.length());
  try(PersonalEngine e=new PersonalEngine(isolated());XiSession xi=new XiSession(e.bankState("qchat"))){
   String library=new String(e.asset("sequence1-codec.xi"),StandardCharsets.UTF_8);
   for(int i=0;i<cases.length();i++){
    JSONObject row=cases.getJSONObject(i);SequenceCodec.Text text=codec.encode(xi,library,row.getString("prompt"),row.getString("previous"));JSONArray expected=row.getJSONArray("tokens");assertEquals("token count "+i,expected.length(),text.tokens.size());
    assertArrayEquals("original UTF-8 "+i,hex(row.getString("raw_hex")),text.raw);assertArrayEquals(text.raw,xi.bytes(SequenceCodec.RAW,text.raw.length));
    for(int j=0;j<expected.length();j++){JSONObject want=expected.getJSONObject(j);SequenceCodec.Token got=text.tokens.get(j);assertEquals(want.getInt("id"),got.id);assertEquals(want.getString("key"),got.key);assertEquals(want.getInt("start"),got.start);assertEquals(want.getInt("length"),got.length);if(want.isNull("numeric"))assertNull(got.number);else assertEquals(want.getDouble("numeric"),got.number.doubleValue(),0);}
    assertEquals(row.getLong("feature_count"),xi.number(SequenceCodec.C+40,8));assertArrayEquals("measured features "+i,hex(row.getString("features_hex")),xi.bytes(SequenceCodec.F,row.getInt("feature_count")*8));
   }
   emit(new JSONObject().put("test","android-python-native-c1-parity").put("cases",cases.length()).put("passed",true));
  }
 }
 @Test public void exactFieldsSurviveTheNativeCircuitAndRejectOverflow()throws Exception {
  JSONArray rows=fixture().getJSONArray("frames");assertEquals(64,rows.length());
  try(PersonalEngine e=new PersonalEngine(isolated());XiSession xi=new XiSession(e.bankState("qchat"))){
   String library=new String(e.asset("sequence1-codec.xi"),StandardCharsets.UTF_8);
   for(int i=0;i<rows.length();i++){
    JSONArray fields=rows.getJSONArray(i);StringBuilder code=new StringBuilder();for(int j=0;j<9;j++)SequenceCodec.put(code,SequenceCodec.FRAME+j*8,fields.getLong(j));
    xi.run(source(code.append("call c1_frame\n").toString(),library));assertEquals(1,xi.number(SequenceCodec.C+184,8));
    for(int j=0;j<9;j++)assertEquals("frame "+i+" field "+j,fields.getLong(j),xi.number(SequenceCodec.MEASURED+j*8,8));
   }
   for(long invalid:new long[]{-1,1<<20}){xi.run(source("store64 "+SequenceCodec.FRAME+" "+invalid+"\ncall c1_frame",library));assertEquals(4,xi.number(SequenceCodec.C+184,8));}
  }
 }
 @Test public void formerlyAliasedWordsCanBeLearnedAndReopened()throws Exception {
  SequenceCodec codec=new SequenceCodec(new JSONArray("[\"<pad>\"]"));String[] prompts={"dato","nos","memoria","no memoria"};byte[] learned;JSONArray dictionary;
  try(PersonalEngine e=new PersonalEngine(isolated())){
   String library=new String(e.asset("sequence1-codec.xi"),StandardCharsets.UTF_8);
   try(XiSession xi=new XiSession(e.bankState("qchat"))){
    xi.run(source("fstore "+(SequenceCodec.C+112)+" .05\nstore64 "+(SequenceCodec.C+56)+" 1\nstore64 "+(SequenceCodec.C+216)+" 11",library));
    for(int i=0;i<4;i++){codec.encode(xi,library,prompts[i],"");xi.run(source("store64 "+(SequenceCodec.C+128)+" "+(SequenceCodec.C+100000000+i*8192)+"\ncall c1_cache_input",library));}
    for(int epoch=0;epoch<100;epoch++){
     StringBuilder code=new StringBuilder();for(int i=0;i<4;i++)code.append("store64 ").append(SequenceCodec.C+128).append(' ').append(SequenceCodec.C+100000000+i*8192).append("\ncall c1_load_input\nstore64 ").append(SequenceCodec.C+88).append(" 0\nstore64 ").append(SequenceCodec.C+96).append(" 0\nstore64 ").append(SequenceCodec.C+104).append(" 0\ncall c1_prefix\nstore64 ").append(SequenceCodec.C+64).append(' ').append(i+1).append("\ncall c1_train\n");xi.run(source(code.toString(),library));
    }
    assertEquals(400,xi.number(SequenceCodec.C+232,8));learned=xi.save();dictionary=codec.dictionary();
   }
   SequenceCodec restored=new SequenceCodec(dictionary);
   try(XiSession xi=new XiSession(learned)){
    for(int i=0;i<4;i++){restored.encode(xi,library,prompts[i],"");xi.run(source("store64 "+(SequenceCodec.C+56)+" 1\nstore64 "+(SequenceCodec.C+88)+" 0\nstore64 "+(SequenceCodec.C+96)+" 0\nstore64 "+(SequenceCodec.C+104)+" 0\ncall c1_prefix\ncall c1_next",library));assertEquals(i+1,xi.number(SequenceCodec.C+72,8));}
   }
  }
 }
 @Test public void capacityIsExplicitAndDictionaryPreservesAccents()throws Exception {
  SequenceCodec c=new SequenceCodec(new JSONArray("[\"<pad>\"]"));SequenceCodec.Text t=c.text("sí si año ano niño nino",256);assertEquals(6,t.tokens.size());Set<Integer> ids=new HashSet<>();for(SequenceCodec.Token token:t.tokens)ids.add(token.id);assertEquals(6,ids.size());
  SequenceCodec restored=new SequenceCodec(c.dictionary());assertEquals(t.tokens.get(0).id,restored.text("sí",256).tokens.get(0).id);
  for(String text:new String[]{String.join(" ",Collections.nCopies(257,"x")),String.join("",Collections.nCopies(16385,"x"))}){
   try{c.text(text,256);fail("Capacity was silently truncated");}catch(IOException expected){}
  }
 }
}
