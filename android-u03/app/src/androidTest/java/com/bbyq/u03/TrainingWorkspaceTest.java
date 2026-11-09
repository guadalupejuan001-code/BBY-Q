package com.bbyq.u03;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.webkit.WebView;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.BeforeClass;
import org.junit.runner.RunWith;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Iterator;
import java.util.UUID;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import static org.junit.Assert.*;

/** End-to-end user training through the same Android/native XI gateway as the UI. */
@RunWith(AndroidJUnit4.class)
public final class TrainingWorkspaceTest {
    @BeforeClass public static void freshEvidence()throws Exception {
        Context app=InstrumentationRegistry.getInstrumentation().getTargetContext();
        try(FileOutputStream out=new FileOutputStream(new File(app.getFilesDir(),"training-test-proof.json"))){
            out.write("{\"schema\":\"BBYQ-C17-Android-training-tests-v1\",\"cases\":{}}".getBytes(StandardCharsets.UTF_8));
        }
    }
    private Instrumentation instrument(){return InstrumentationRegistry.getInstrumentation();}
    private Context app(){return instrument().getTargetContext();}
    private String id(){return "c17-test-"+UUID.randomUUID();}
    private JSONObject request(String action,String session)throws Exception {
        JSONObject r=new JSONObject().put("action",action).put("request_id",id());
        if(session!=null)r.put("session_id",session);
        return r;
    }
    private JSONObject training(JSONObject request)throws Exception {
        return U03Runtime.operation(app(),"training",request.toString());
    }
    private JSONObject personal()throws Exception {
        return U03Runtime.status(app()).getJSONObject("snapshot");
    }
    private String create(String title)throws Exception {
        JSONObject r=training(request("create",null).put("title",title));
        assertTrue(r.toString(),r.getBoolean("ok"));
        assertFalse(r.getString("session_id").isEmpty());return r.getString("session_id");
    }
    private JSONObject state(String session)throws Exception{return training(request("status",session));}
    private JSONObject candidate(String session)throws Exception{return state(session).getJSONObject("candidate_snapshot");}
    private JSONObject receipt(JSONObject r)throws Exception {
        assertTrue(r.toString(),r.getBoolean("ok"));
        JSONObject receipt=r.getJSONObject("receipt");
        assertTrue(receipt.toString(),receipt.getBoolean("ok"));
        boolean nativeCall=false;JSONArray trace=receipt.getJSONArray("trace");
        for(int i=0;i<trace.length();i++){
            JSONObject event=trace.getJSONObject(i);
            if(event.has("native")){assertTrue(event.toString(),event.getBoolean("native"));nativeCall=true;}
        }
        assertTrue("Every user lesson/test must really reach XI",nativeCall);return receipt;
    }
    private JSONObject resultKind(JSONObject receipt,String kind)throws Exception {
        JSONArray results=receipt.getJSONArray("results");
        for(int i=results.length()-1;i>=0;i--){
            JSONObject row=results.getJSONObject(i);if(kind.equals(row.optString("kind")))return row;
        }
        throw new AssertionError("Missing native "+kind+" result: "+receipt);
    }
    private JSONObject query(String session,String text,boolean holdout,int expected)throws Exception {
        JSONObject r=request("query",session).put("text",text).put("split",holdout?"holdout":"practice");
        if(holdout)r.put("expected_status",expected);return training(r);
    }
    private void learnedFactAndRule(String session,String subject)throws Exception {
        receipt(training(request("fact",session).put("subject",subject).put("property","humano")));
        receipt(training(request("rule",session).put("antecedent","humano").put("consequence","mortal")));
    }
    private JSONObject approved(String session)throws Exception {
        JSONObject r=training(request("validate",session));
        assertTrue(r.toString(),r.getBoolean("ok"));JSONObject v=r.getJSONObject("validation");
        assertTrue(v.toString(),v.getBoolean("passed"));assertTrue(v.toString(),v.getBoolean("activation_allowed"));
        assertTrue(v.getInt("training_count")>0);assertTrue(v.getInt("holdout_count")>0);return v;
    }
    private String rejected(JSONObject r)throws Exception {
        try{JSONObject accepted=training(r);throw new AssertionError("Unsafe action accepted: "+accepted);}
        catch(com.chaquo.python.PyException e){
            assertTrue("A validation rejection must not be a runtime crash: "+e,e.toString().contains("ValueError"));
            return e.toString();
        }
    }
    private void restore(String session,String backup)throws Exception {
        JSONObject r=training(request("restore",session).put("backup_id",backup).put("confirm_discard_new_activity",true));
        assertTrue(r.toString(),r.getBoolean("restored"));
    }
    private void sameSnapshot(JSONObject expected,JSONObject actual)throws Exception {
        assertEquals("revision",expected.getLong("revision"),actual.getLong("revision"));
        assertEquals("metadata",expected.getString("metadata_sha256"),actual.getString("metadata_sha256"));
        assertEquals("task count",expected.getInt("tasks"),actual.getInt("tasks"));
        assertEquals("feedback count",expected.getInt("feedback"),actual.getInt("feedback"));
        JSONObject banks=expected.getJSONObject("banks");
        assertEquals(7,banks.length());assertEquals(7,actual.getJSONObject("banks").length());
        Iterator<String> names=banks.keys();
        while(names.hasNext()){
            String name=names.next();
            assertEquals("native bank "+name,banks.getString(name),actual.getJSONObject("banks").getString(name));
        }
    }
    private String hex(byte[] data)throws Exception {
        byte[] digest=MessageDigest.getInstance("SHA-256").digest(data);
        StringBuilder out=new StringBuilder();for(byte b:digest)out.append(String.format("%02x",b&255));
        return out.toString();
    }
    private byte[] bytes(InputStream input)throws Exception {
        try(InputStream in=input;ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);return out.toByteArray();
        }
    }
    private void evidence(String name,JSONObject details)throws Exception {
        File file=new File(app().getFilesDir(),"training-test-proof.json");
        JSONObject proof=new JSONObject(new String(bytes(new FileInputStream(file)),StandardCharsets.UTF_8));
        details.put("passed",true);proof.getJSONObject("cases").put(name,details);
        try(FileOutputStream out=new FileOutputStream(file)){
            out.write(proof.toString(2).getBytes(StandardCharsets.UTF_8));
        }
    }
    private void screenshot(String name)throws Exception {
        Bitmap shot=instrument().getUiAutomation().takeScreenshot();assertNotNull("Android screenshot",shot);
        try(FileOutputStream out=new FileOutputStream(new File(app().getFilesDir(),name))){
            assertTrue(shot.compress(Bitmap.CompressFormat.PNG,100,out));
        }finally{shot.recycle();}
    }
    @Test public void C17_userLessonsAreNativeIsolatedAndReachNormalChat()throws Exception {
        JSONObject original=personal();String session=create("Conocimiento y activación C17");
        String subject="Niebla Taller";
        JSONObject factRequest=request("fact",session).put("subject",subject).put("property","humano");
        JSONObject taught=training(factRequest);receipt(taught);
        JSONObject afterFact=candidate(session);
        assertEquals("Exact retries must return their original response",taught.toString(),training(factRequest).toString());
        sameSnapshot(afterFact,candidate(session));
        JSONObject collision=new JSONObject(factRequest.toString()).put("property","estrella");
        String collisionError=rejected(collision);sameSnapshot(afterFact,candidate(session));
        receipt(training(request("rule",session).put("antecedent","humano").put("consequence","mortal")));
        JSONObject beforeTest=candidate(session);
        JSONObject tested=query(session,"dime si "+subject+" es mortal",true,1);
        JSONObject proof=resultKind(receipt(tested),"query");
        assertEquals(1,proof.getInt("status"));assertTrue(proof.getJSONArray("proof").length()>0);
        sameSnapshot(beforeTest,candidate(session));sameSnapshot(original,personal());
        JSONObject validation=approved(session);sameSnapshot(beforeTest,candidate(session));sameSnapshot(original,personal());
        JSONObject activation=training(request("activate",session));assertTrue(activation.toString(),activation.getBoolean("active"));
        String backup=activation.getString("backup_id");JSONObject normal=null;
        try{
            normal=U03Runtime.turn(app(),id(),"dime si "+subject+" es mortal","");
            assertTrue(normal.toString(),normal.getBoolean("ok"));assertTrue(normal.getBoolean("native_XI"));
            assertEquals(1,resultKind(normal.getJSONObject("receipt"),"query").getInt("status"));
            assertTrue(U03Runtime.status(app()).getJSONObject("memory").getBoolean("C1_synchronized_with_U02"));
        }finally{restore(session,backup);}
        sameSnapshot(original,personal());
        evidence("native_lessons_activation_restore",new JSONObject().put("session_id",session)
            .put("teaching",taught).put("holdout",tested).put("validation",validation).put("ordinary_chat",normal)
            .put("exact_replay_verified",true).put("conflicting_request_rejected",collisionError)
            .put("evaluation_did_not_train",true).put("restored_personal_snapshot",personal()));
    }
    @Test public void C17_jointFeedbackChangesNativeParametersExactlyOnce()throws Exception {
        JSONObject original=personal();String session=create("Aprendizaje conjunto C17");
        JSONObject prepared=training(request("joint_prepare",session).put("seed",2023144612L).put("rule",1).put("position",3));
        JSONObject inferred=receipt(prepared);JSONArray trace=inferred.getJSONArray("trace");
        for(int i=0;i<trace.length();i++){
            String op=trace.getJSONObject(i).optString("operation");
            assertFalse("Labels/gradients must not enter initial inference",op.contains("supervised_update")||op.equals("entity_learn")||op.equals("u2_adam"));
        }
        assertTrue(prepared.has("prediction"));assertTrue(prepared.getJSONObject("teacher").has("class"));
        JSONObject feedbackRequest=request("joint_feedback",session).put("exercise_id",prepared.getString("exercise_id"));
        JSONObject learned=training(feedbackRequest);JSONObject feedback=resultKind(receipt(learned),"feedback");
        JSONObject before=feedback.getJSONObject("parameter_sha256_before"),after=feedback.getJSONObject("parameter_sha256_after");
        assertEquals("All six trained parameter regions must be audited",6,before.length());
        assertEquals(before.length(),after.length());
        int changed=0;Iterator<String> keys=before.keys();
        while(keys.hasNext()){
            String key=keys.next();assertEquals(64,before.getString(key).length());assertEquals(64,after.getString(key).length());
            boolean different=!before.getString(key).equals(after.getString(key));
            assertEquals(key,different,feedback.getJSONObject("changed").getBoolean(key));if(different)changed++;
        }
        assertTrue("Actual native model coefficients must change",changed>0);
        assertEquals(1,feedback.getJSONObject("updates").getInt("vqc"));
        assertEquals(1,feedback.getJSONObject("updates").getInt("perception_readout"));
        assertEquals("independent-labels",feedback.getString("supervision"));
        JSONObject trained=candidate(session);
        assertEquals(learned.toString(),training(feedbackRequest).toString());sameSnapshot(trained,candidate(session));
        String duplicate=rejected(request("joint_feedback",session).put("exercise_id",prepared.getString("exercise_id")));
        sameSnapshot(trained,candidate(session));sameSnapshot(original,personal());
        JSONObject beforeValidation=candidate(session),validation=approved(session);
        sameSnapshot(beforeValidation,candidate(session));
        assertTrue("A trained quantum candidate requires heldout native quantum regression",validation.getJSONObject("candidate").has("joint_regression"));
        JSONObject jointValidation=validation.getJSONObject("candidate").getJSONObject("joint_regression");
        assertTrue("Joint-only training must be validated without artificial fact lessons",jointValidation.getInt("total")>0);
        assertTrue(jointValidation.getBoolean("all_inference_without_teacher"));
        JSONArray heldout=jointValidation.getJSONArray("raw");
        for(int i=0;i<heldout.length();i++)assertNotEquals("Evaluation samples cannot repeat the training seed",2023144612L,heldout.getJSONObject(i).getLong("source_seed"));
        JSONObject activated=training(request("activate",session));assertTrue(activated.getBoolean("active"));
        String backup=activated.getString("backup_id");
        try{sameSnapshot(beforeValidation,personal());}
        finally{restore(session,backup);}
        sameSnapshot(original,personal());
        evidence("joint_native_feedback",new JSONObject().put("session_id",session).put("inference",prepared)
            .put("training",learned).put("independently_counted_changed_regions",changed)
            .put("exact_replay_verified",true).put("duplicate_training_rejected",duplicate)
            .put("validation",validation).put("trained_native_banks_activated_in_live_model",true)
            .put("original_personal_model_restored",true));
    }
    @Test public void C17_staleActivationAndInvalidInputsPreserveState()throws Exception {
        JSONObject original=personal();String session=create("Activación sin pérdida C17");
        JSONObject initial=candidate(session);
        String invalid=rejected(request("fact",session).put("subject","").put("property","humano"));
        sameSnapshot(initial,candidate(session));sameSnapshot(original,personal());
        learnedFactAndRule(session,"Bruma Taller");
        String ungated=rejected(request("activate",session));
        JSONObject beforePractice=candidate(session);
        JSONObject practiced=query(session,"dime si Bruma Taller es humano",false,1);
        assertEquals(1,resultKind(receipt(practiced),"query").getInt("status"));
        String exposed=rejected(request("query",session).put("text","dime si Bruma Taller es humano")
            .put("split","holdout").put("expected_status",1));
        sameSnapshot(beforePractice,candidate(session));
        JSONObject wrong=query(session,"dime si Bruma Taller es mortal",true,0);
        assertFalse("A wrong declared expectation must be visible",wrong.getBoolean("correct"));
        JSONObject refusedValidation=training(request("validate",session)).getJSONObject("validation");
        assertFalse("Zero/equal scores do not qualify an incorrect expectation",refusedValidation.getBoolean("passed"));
        assertFalse(refusedValidation.getBoolean("activation_allowed"));
        String relabel=rejected(request("query",session).put("text","dime si Bruma Taller es mortal")
            .put("split","holdout").put("expected_status",1));
        receipt(training(request("fact",session).put("subject","Nube Taller").put("property","humano")));
        String seenAfterEdit=rejected(request("query",session).put("text","dime si Bruma Taller es mortal")
            .put("split","holdout").put("expected_status",1));
        query(session,"dime si Nube Taller es mortal",true,1);approved(session);
        JSONObject tested=candidate(session);
        JSONObject intervening=U03Runtime.turn(app(),id(),"calcula 14 + 6","");
        assertTrue(intervening.toString(),intervening.getBoolean("ok"));
        JSONObject current=personal();assertTrue(current.getLong("revision")>original.getLong("revision"));
        String stale=rejected(request("activate",session));
        sameSnapshot(current,personal());sameSnapshot(tested,candidate(session));
        evidence("invalid_and_stale_actions",new JSONObject().put("session_id",session)
            .put("invalid_input_rejected",invalid).put("activation_before_validation_rejected",ungated)
            .put("practice_to_holdout_rejected",exposed).put("seen_question_after_edit_rejected",seenAfterEdit)
            .put("incorrect_holdout_rejected",refusedValidation).put("posthoc_relabel_rejected",relabel)
            .put("stale_activation_rejected",stale).put("current_personal_snapshot",current)
            .put("candidate_and_new_personal_activity_preserved",true));
    }
    private String checkpointHash(SQLiteDatabase db,String name,long length)throws Exception {
        // A native bank exceeds Android's CursorWindow. Hash every byte in bounded
        // BLOB slices instead of asking one cursor row to hold the whole checkpoint.
        MessageDigest digest=MessageDigest.getInstance("SHA-256");
        for(long offset=0;offset<length;){
            int count=(int)Math.min(256*1024L,length-offset);
            try(Cursor c=db.rawQuery("SELECT substr(snapshot,?,?) FROM unified_banks WHERE name=?",
                new String[]{Long.toString(offset+1),Integer.toString(count),name})){
                assertTrue("Checkpoint slice exists: "+name,c.moveToFirst());
                byte[] chunk=c.getBlob(0);
                assertEquals("Checkpoint slice is complete: "+name,count,chunk.length);
                digest.update(chunk);
            }
            offset+=count;
        }
        StringBuilder out=new StringBuilder();for(byte b:digest.digest())out.append(String.format("%02x",b&255));
        return out.toString();
    }
    private JSONObject inspectModel(byte[] raw,JSONObject expected)throws Exception {
        File file=new File(app().getCacheDir(),id()+".sqlite");
        try(FileOutputStream out=new FileOutputStream(file)){out.write(raw);}
        JSONObject checked=new JSONObject();
        try(SQLiteDatabase db=SQLiteDatabase.openDatabase(file.getAbsolutePath(),null,SQLiteDatabase.OPEN_READONLY|SQLiteDatabase.NO_LOCALIZED_COLLATORS)){
            try(Cursor c=db.rawQuery("PRAGMA integrity_check",null)){assertTrue(c.moveToFirst());assertEquals("ok",c.getString(0));}
            try(Cursor c=db.rawQuery("SELECT name,length(snapshot),sha FROM unified_banks",null)){
                while(c.moveToNext()){
                    String name=c.getString(0),stored=c.getString(2),actual=checkpointHash(db,name,c.getLong(1));
                    assertEquals("Stored checkpoint bytes "+name,stored,actual);
                    assertEquals("Export matches saved candidate "+name,expected.getJSONObject("banks").getString(name),actual);
                    checked.put(name,actual);
                }
            }
            assertEquals(7,checked.length());
            try(Cursor c=db.rawQuery("SELECT metadata,sha,revision FROM unified_state WHERE id=1",null)){
                assertTrue(c.moveToFirst());assertEquals(c.getString(1),hex(c.getBlob(0)));
                assertEquals(expected.getLong("revision"),c.getLong(2));assertEquals(expected.getString("metadata_sha256"),c.getString(1));
            }
        }finally{file.delete();}
        return checked;
    }
    @Test public void C17_exportCarriesAuditableDataAndAuthenticModel()throws Exception {
        JSONObject original=personal();String session=create("Nara y sus reglas");
        receipt(training(request("fact",session).put("subject","Nara").put("property","robot")));
        receipt(training(request("rule",session).put("antecedent","robot").put("consequence","máquina")));
        JSONObject tutorialQuery=query(session,"es Nara máquina",true,1);
        assertEquals(1,resultKind(receipt(tutorialQuery),"query").getInt("status"));approved(session);
        JSONObject saved=state(session);JSONObject exported=training(request("export",session));
        File archive=new File(exported.getString("path"));
        String archivePath=archive.getCanonicalPath();
        assertTrue(archivePath.startsWith(app().getFilesDir().getCanonicalPath()+File.separator)
            ||archivePath.startsWith(app().getCacheDir().getCanonicalPath()+File.separator));
        assertTrue(archive.isFile());assertEquals("application/zip",exported.getString("mime"));
        JSONObject manifest,report,banks;String modelHash,baselineHash;
        try(ZipFile zip=new ZipFile(archive)){
            for(String name:new String[]{"manifest.json","report.json","candidate.sqlite","baseline.sqlite"})assertNotNull("Portable export entry "+name,zip.getEntry(name));
            byte[] model=bytes(zip.getInputStream(zip.getEntry("candidate.sqlite")));
            byte[] baseline=bytes(zip.getInputStream(zip.getEntry("baseline.sqlite")));
            modelHash=hex(model);baselineHash=hex(baseline);
            manifest=new JSONObject(new String(bytes(zip.getInputStream(zip.getEntry("manifest.json"))),StandardCharsets.UTF_8));
            report=new JSONObject(new String(bytes(zip.getInputStream(zip.getEntry("report.json"))),StandardCharsets.UTF_8));
            assertTrue("Manifest binds candidate bytes",manifest.toString().contains(modelHash));
            assertTrue("Manifest binds baseline bytes",manifest.toString().contains(baselineHash));
            assertTrue("Report identifies the actual session",report.toString().contains(session));
            assertTrue("Report preserves the exact illustrated tutorial example",report.toString().contains("Nara")&&report.toString().contains("máquina"));
            banks=inspectModel(model,saved.getJSONObject("candidate_snapshot"));
            inspectModel(baseline,saved.getJSONObject("baseline_snapshot"));
        }
        sameSnapshot(saved.getJSONObject("candidate_snapshot"),candidate(session));sameSnapshot(original,personal());
        evidence("portable_export",new JSONObject().put("session_id",session).put("filename",exported.getString("filename"))
            .put("manifest",manifest).put("candidate_sha256",modelHash).put("baseline_sha256",baselineHash)
            .put("independently_verified_native_banks",banks).put("sqlite_integrity",true)
            .put("training_data_and_results_present",true).put("illustrated_tutorial_query",tutorialQuery));
    }
    @Test public void C17_trainingScreenAndIllustratedGuideArePackagedAndOpen()throws Exception {
        String html=new String(bytes(app().getAssets().open("training-guide.html")),StandardCharsets.UTF_8);
        assertTrue("Guide must contain authored diagrams",html.contains("<svg"));
        assertFalse("Offline instructions must not load remote scripts",html.toLowerCase().contains("<script"));
        Intent intent=new Intent(app(),TrainingActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        TrainingActivity activity=(TrainingActivity)instrument().startActivitySync(intent);
        try {
            instrument().waitForIdleSync();
            instrument().runOnMainSync(()->{
                assertNotNull("Training status",activity.findViewById(0x5803001));
                assertNotNull("Training session name",activity.findViewById(0x5803010));
                assertNotNull("Create real session",activity.findViewById(0x5803011));
                assertNotNull("Read guide without leaving app",activity.findViewById(0x5803002));
            });
            screenshot("training-workspace-ui.png");
            instrument().runOnMainSync(()->assertTrue(activity.findViewById(0x5803002).performClick()));
            UiEvidence.until("The illustrated guide opens in its actual WebView",10000,()->UiEvidence.ui(()->activity.guideWebViewForTests()!=null));
            WebView web=UiEvidence.ui(activity::guideWebViewForTests);UiEvidence.visualReady(web);screenshot("training-guide-ui.png");
            JSONArray screenshots=new JSONArray().put("training-workspace-ui.png").put("training-guide-ui.png");
            JSONObject guide=UiEvidence.scrollGuideToIllustration(activity,"training-guide-diagram-ui.png");
            screenshots.put("training-guide-diagram-ui.png");
            for(String name:new String[]{"training-guide-diagram-2-ui.png","training-guide-diagram-3-ui.png"}){
                UiEvidence.swipe(web,0.24f);UiEvidence.visualReady(web);
                screenshot(name);screenshots.put(name);
            }
            evidence("training_ui_and_guide",new JSONObject().put("native_activity_opened",true)
                .put("guide_opened_in_webview",true).put("offline_guide_sha256",hex(html.getBytes(StandardCharsets.UTF_8)))
                .put("touch_scroll_and_visible_svg",guide).put("screenshots",screenshots));
        }finally{instrument().runOnMainSync(()->{
            if(activity.guideRootForTests()!=null)activity.guideRootForTests().findViewById(0x5803090).performClick();
            activity.finish();
        });}
    }
}
