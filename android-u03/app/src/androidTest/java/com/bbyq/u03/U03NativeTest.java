package com.bbyq.u03;

import android.content.Context;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.json.JSONObject;
import org.json.JSONArray;
import org.junit.Test;
import org.junit.FixMethodOrder;
import org.junit.runners.MethodSorters;
import org.junit.runner.RunWith;
import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;
import java.util.TreeSet;
import java.util.Iterator;
import static org.junit.Assert.*;

/** Each test invokes a real public mobile action; archived sources cannot pass. */
@RunWith(AndroidJUnit4.class)
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class U03NativeTest {
 static final String MISSION="guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3";
 static final String RESTART_ID="mobile-integration-restart-fixed";
 Context app(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
 static String canonical(Object x)throws Exception{
  if(x instanceof JSONObject){JSONObject j=(JSONObject)x;TreeSet<String> keys=new TreeSet<>();Iterator<String> it=j.keys();while(it.hasNext())keys.add(it.next());StringBuilder s=new StringBuilder("{");boolean first=true;for(String k:keys){if(!first)s.append(',');first=false;s.append(JSONObject.quote(k)).append(':').append(canonical(j.get(k)));}return s.append('}').toString();}
  if(x instanceof JSONArray){JSONArray j=(JSONArray)x;StringBuilder s=new StringBuilder("[");for(int i=0;i<j.length();i++){if(i>0)s.append(',');s.append(canonical(j.get(i)));}return s.append(']').toString();}
  if(x==JSONObject.NULL || x==null)return "null";
  if(x instanceof String)return JSONObject.quote((String)x);
  return x.toString();
 }
 String snapshot()throws Exception{return canonical(U03Runtime.status(app()).getJSONObject("snapshot"));}
 JSONObject action(String name)throws Exception{return U03Runtime.action(app(),name,"{}").getJSONObject("result").getJSONObject("data");}
 void proof(String name,JSONObject row)throws Exception{
  File folder=new File(app().getFilesDir(),"test-evidence");assertTrue(folder.isDirectory() || folder.mkdirs());
  Files.write(new File(folder,name+".json").toPath(),row.toString(2).getBytes(StandardCharsets.UTF_8));
 }
 @Test public void test01NativeLoaderAndOriginalCheckpoints()throws Exception{
  JSONObject loader=U03Runtime.diagnostics(app());assertTrue(loader.toString(),loader.getBoolean("loaded"));
  assertTrue(loader.getBoolean("process_64_bit"));
  assertEquals(16384,loader.getJSONObject("runtime").getInt("elf_target_alignment"));
  assertFalse(loader.getJSONObject("runtime").getBoolean("cached_inference"));
  JSONObject start=U03Runtime.start(app());assertTrue(start.getBoolean("ready"));
  assertEquals(7,start.getInt("banks"));assertEquals(159,start.getInt("historical_assets"));
  assertTrue(start.getBoolean("original_C06_C07_C08_checkpoints_loaded"));
  assertFalse(start.getBoolean("model_promoted"));assertFalse(start.getBoolean("gpu_C12_ported"));
  proof("loader",loader);proof("startup",start);
 }
 @Test public void test02MainC03C04C05C06C09ExecuteAndReplay()throws Exception{
  JSONObject first=U03Runtime.turn(app(),"main-math-identity","calcula 7 + 3","");
  assertTrue(first.toString(),first.getBoolean("ok"));assertTrue(first.getBoolean("native_XI"));
  assertTrue(first.getString("reply").contains("10"));
  assertTrue(first.getJSONObject("C03").getLong("validated_input_bytes")>0);
  assertEquals(0,first.getJSONObject("C04").getInt("stateful_xi_circuits_skipped"));
  assertFalse(first.isNull("C05"));assertTrue(first.getJSONObject("C06").getBoolean("native_XI"));
  assertEquals(7,first.getJSONObject("C09").getInt("bank_count"));
  assertTrue(first.getJSONObject("C09").getBoolean("C1_U02_synchronized"));
  assertTrue(first.getJSONObject("C00_C01_C14").getInt("executes")>0);
  JSONObject again=U03Runtime.turn(app(),"main-math-identity","calcula 7 + 3","");
  assertEquals(first.getString("receipt_sha256"),again.getString("receipt_sha256"));
  assertEquals(first.getLong("after_revision"),again.getLong("after_revision"));
  proof("main-modules",first);
 }
 @Test public void test03SixOriginalEnginesAndC09View()throws Exception{
  JSONObject r=U03Runtime.turn(app(),"main-six-engine-mission",MISSION,"");assertTrue(r.toString(),r.getBoolean("ok"));
  String trace=r.getJSONArray("trace").toString();
  for(String op:new String[]{"c1_encode_input","qm_read","vqc_forward","entity_infer","qrl_step","qchat_encode"})assertTrue(trace,trace.contains(op));
  JSONObject memory=action("MEMORY");assertTrue(memory.getBoolean("C1_synchronized_with_U02"));
  assertEquals(7,memory.getJSONObject("bank_sha256").length());
  proof("six-engines",r);proof("memory-C09",memory);
 }
 @Test public void test04C10NativePlanDoesNotPublishSpeculativeState()throws Exception{
  String before=snapshot();
  JSONObject args=new JSONObject().put("observation","Nara").put("association","Faro Azul").put("position",3);
  JSONObject r=U03Runtime.action(app(),"PLAN",args.toString()).getJSONObject("result").getJSONObject("data");
  assertEquals(r.toString(),"native_plan",r.getString("status"));
  assertEquals(before,snapshot());proof("plan-C10",r);
 }
 @Test public void test05C06NativeSemanticOriginalCheckpoint()throws Exception{
  JSONObject args=new JSONObject().put("prompt","no expliques memoria");String before=snapshot();
  JSONObject r=U03Runtime.action(app(),"SEMANTIC",args.toString()).getJSONObject("result").getJSONObject("data");
  assertTrue(r.getBoolean("native_XI"));assertTrue(r.getBoolean("observational"));
  assertEquals("ed0f0067e43fcab74ba81c574bca983d8a497322ae5d7e8218f7a2941aa53018",r.getString("checkpoint_sha256"));
  assertEquals(before,snapshot());proof("semantic-C06",r);
 }
 @Test public void test06C07C08RealEvidenceHeadsDoNotInventWorldTruth()throws Exception{
  String before=snapshot();JSONObject r=action("EVIDENCE_DEMO");
  assertEquals("evaluated",r.getString("status"));assertTrue(r.getBoolean("demo_is_synthetic"));
  JSONObject rows=r.getJSONObject("evaluations");
  for(String key:new String[]{"c07","c08"}){
   assertTrue(rows.getJSONObject(key).getBoolean("native_XI"));
   assertFalse(rows.getJSONObject(key).getBoolean("candidate_promoted"));
   assertEquals("report_conflict",rows.getJSONObject(key).getString("guarded_action"));
  }
  assertFalse(rows.getJSONObject("c08").getString("verification_question").isEmpty());
  assertEquals(0,r.getInt("writes_to_user_memory"));assertEquals(before,snapshot());proof("evidence-C07-C08",r);
 }
 @Test public void test07C01LibraryTransportMatchesOriginalBytes()throws Exception{
  JSONObject r=action("C01");assertTrue(r.getBoolean("exact_output_and_checkpoint"));
  assertTrue(r.getJSONObject("library_transport").getInt("cache_hits")>0);
  assertTrue(r.getJSONObject("library_transport").getLong("jni_source_bytes")<r.getJSONObject("baseline").getLong("jni_source_bytes"));
  proof("transport-C01",r);
 }
 @Test public void test08C02OptimisticPersistenceUsesOriginalReceipts()throws Exception{
  JSONObject r=action("C02");assertTrue(r.getBoolean("receipt_and_checkpoint_equal"));
  assertTrue(r.getBoolean("replay_without_second_update"));assertTrue(r.getBoolean("user_database_unchanged"));proof("persistence-C02",r);
 }
 @Test public void test09C11NativeTrainingActuallyChangesWeightsInCopy()throws Exception{
  String before=snapshot();JSONObject r=action("C11");assertTrue(r.getBoolean("native_XI"));
  assertFalse(r.getBoolean("candidate_promoted"));assertTrue(r.getBoolean("user_database_unchanged"));
  JSONObject arms=r.getJSONObject("arms");assertEquals(0,arms.getJSONObject("frozen").getInt("verified_feedback"));
  assertEquals(1,arms.getJSONObject("joint").getInt("verified_feedback"));
  JSONObject changed=arms.getJSONObject("joint").getJSONObject("changed_regions");boolean any=false;
  Iterator<String> keys=changed.keys();while(keys.hasNext())any|=changed.getBoolean(keys.next());assertTrue(any);
  assertEquals(6,changed.length());assertEquals(before,snapshot());proof("learning-C11",r);
 }
 @Test public void test10C12NativeLearningComparisonAndInterference()throws Exception{
  String before=snapshot();JSONObject r=action("C12");assertFalse(r.getBoolean("candidate_promoted"));
  assertEquals(2,r.getJSONObject("arms").getJSONObject("joint").getInt("verified_feedback"));
  assertTrue(r.getBoolean("labels_unsealed_after_predictions"));
  assertEquals(3,r.getJSONObject("interference").getJSONArray("A_B_A").length());
  assertEquals(before,snapshot());proof("learning-C12",r);
 }
 @Test public void test11C13ActualSerialCacheComparisonNotPromotion()throws Exception{
  JSONObject r=action("C13");assertTrue(r.getBoolean("receipt_and_checkpoint_equal"));
  assertTrue(r.getBoolean("serial_exclusive_scope"));assertFalse(r.getBoolean("cache_promoted"));
  assertFalse(r.getBoolean("performance_advantage_claimed"));
  assertTrue(r.getJSONObject("measurements").getJSONObject("True").getJSONObject("cache_counts").getInt("cache_hits")>0);
  proof("cache-C13",r);
 }
 @Test public void test12C14TenActualAblationsAndDisjointPackets()throws Exception{
  String before=snapshot();JSONObject r=action("C14");assertEquals(10,r.getInt("trial_count"));
  assertTrue(r.getBoolean("failed_ablations_retained"));JSONArray rows=r.getJSONArray("trials");
  int noVoice=0;for(int i=0;i<rows.length();i++){
   JSONObject row=rows.getJSONObject(i);assertTrue(row.getJSONObject("packets").getInt("executes")>0);
   assertTrue(row.getJSONObject("packets").getBoolean("packet_spans_nonoverlapping"));
   if(row.getString("control").equals("voice-ablated")){noVoice++;assertFalse(row.optBoolean("voice_faithful"));}
  }
  assertEquals(2,noVoice);assertEquals(before,snapshot());proof("ablations-C14",r);
 }
 @Test public void test13C15ActualMobileWALConcurrencyRollbackAndReplay()throws Exception{
  String before=snapshot();JSONObject r=action("C15");assertEquals(2,r.getInt("committed_requests"));
  assertEquals(3,r.getInt("rollbacks"));assertTrue(r.getBoolean("post_commit_observed"));
  assertTrue(r.getBoolean("replay_exact"));assertTrue(r.getBoolean("reopen_exact"));
  assertTrue(r.getBoolean("different_payload_collision_rejected"));assertEquals(before,snapshot());proof("stress-C15",r);
 }
 @Test public void test14HistoricalFilesStillIntactAndNoModelPromotion()throws Exception{
  JSONObject audit=action("AUDIT");assertEquals(159,audit.getInt("protected_files"));assertTrue(audit.getBoolean("all_sha256_unchanged"));
  JSONObject status=U03Runtime.status(app());assertEquals(16,status.getJSONObject("capability_modes").length());
  assertTrue(status.getBoolean("C11_C12_unpromoted"));assertTrue(status.getBoolean("C13_cache_disabled"));assertFalse(status.getBoolean("GPU_virtual_compute_ported"));
  proof("complete-status",status);
 }
 @Test public void test15PersistReceiptForIndependentProcessRestart()throws Exception{
  JSONObject r=U03Runtime.turn(app(),RESTART_ID,"calcula 17 + 25","");assertTrue(r.toString(),r.getBoolean("ok"));
  assertTrue(r.getString("reply").contains("42"));
  JSONObject saved=new JSONObject().put("request_id",RESTART_ID).put("prompt","calcula 17 + 25")
     .put("receipt_sha256",r.getString("receipt_sha256")).put("snapshot_canonical",snapshot());
  Files.write(new File(app().getFilesDir(),"restart-test.json").toPath(),saved.toString().getBytes(StandardCharsets.UTF_8));proof("restart-before",saved);
 }
}
