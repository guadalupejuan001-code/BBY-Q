package com.bbyq.u03;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.UUID;
import static org.junit.Assert.*;

/** CI must run seed and verify in different Android processes, separated by adb force-stop. */
@RunWith(AndroidJUnit4.class)
public final class TrainingRestartTest {
    private Context app(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private JSONObject call(String action,String session,JSONObject fields)throws Exception {
        JSONObject request=fields==null?new JSONObject():fields;
        request.put("action",action).put("request_id","c17-restart-"+UUID.randomUUID());
        if(session!=null)request.put("session_id",session);
        return U03Runtime.operation(app(),"training",request.toString());
    }
    private JSONObject snapshot()throws Exception{return U03Runtime.status(app()).getJSONObject("snapshot");}
    private void same(JSONObject expected,JSONObject actual)throws Exception {
        for(String field:new String[]{"revision","tasks","feedback"})assertEquals(field,expected.getLong(field),actual.getLong(field));
        assertEquals(expected.getString("metadata_sha256"),actual.getString("metadata_sha256"));
        JSONObject banks=expected.getJSONObject("banks");assertEquals(7,banks.length());
        Iterator<String> names=banks.keys();while(names.hasNext()){
            String key=names.next();assertEquals(key,banks.getString(key),actual.getJSONObject("banks").getString(key));
        }
    }
    private void positive(JSONObject response)throws Exception {
        assertTrue(response.toString(),response.getBoolean("ok"));
        JSONObject receipt=response.getJSONObject("receipt");assertTrue(receipt.toString(),receipt.getBoolean("ok"));
        JSONArray results=receipt.getJSONArray("results");boolean proven=false;
        for(int i=0;i<results.length();i++){
            JSONObject item=results.getJSONObject(i);
            if("query".equals(item.optString("kind"))){assertEquals(1,item.getInt("status"));assertTrue(item.getJSONArray("proof").length()>0);proven=true;}
        }
        assertTrue("A fresh process must execute the taught native fact/rule",proven);
    }
    private void write(String filename,JSONObject report)throws Exception {
        try(FileOutputStream out=new FileOutputStream(new File(app().getFilesDir(),filename))){
            out.write(report.toString(2).getBytes(StandardCharsets.UTF_8));
        }
    }
    private JSONObject conversation(JSONObject request)throws Exception {
        return U03Runtime.operation(app(),"conversation",request.toString());
    }
    /** JSON object order is not part of the durable conversation contract. */
    private String canonical(Object value)throws Exception {
        if(value==null||value==JSONObject.NULL)return "null";
        if(value instanceof JSONObject){
            JSONObject object=(JSONObject)value;ArrayList<String> keys=new ArrayList<>();
            Iterator<String> names=object.keys();while(names.hasNext())keys.add(names.next());Collections.sort(keys);
            StringBuilder text=new StringBuilder("{");for(String key:keys){if(text.length()>1)text.append(',');
                text.append(JSONObject.quote(key)).append(':').append(canonical(object.get(key)));}return text.append('}').toString();
        }
        if(value instanceof JSONArray){
            JSONArray array=(JSONArray)value;StringBuilder text=new StringBuilder("[");
            for(int i=0;i<array.length();i++){if(i>0)text.append(',');text.append(canonical(array.get(i)));}return text.append(']').toString();
        }
        if(value instanceof Number)return new BigDecimal(value.toString()).stripTrailingZeros().toPlainString();
        if(value instanceof Boolean)return value.toString();return JSONObject.quote(value.toString());
    }
    private String canonicalSha(Object value)throws Exception {
        byte[] digest=MessageDigest.getInstance("SHA-256").digest(canonical(value).getBytes(StandardCharsets.UTF_8));
        StringBuilder out=new StringBuilder();for(byte b:digest)out.append(String.format("%02x",b&255));return out.toString();
    }
    @Test public void activeTrainingModelSurvivesExternalProcessRestart()throws Exception {
        String phase=InstrumentationRegistry.getArguments().getString("training_phase","");
        SharedPreferences saved=app().getSharedPreferences("c17-ci-training-restart",Context.MODE_PRIVATE);
        String query="dime si Nube Persistente es mortal";
        U03Runtime.start(app());
        if("seed".equals(phase)){
            JSONObject original=snapshot();
            String session=call("create",null,new JSONObject().put("title","Sesión persistente C17")).getString("session_id");
            assertTrue(call("fact",session,new JSONObject().put("subject","Nube Persistente").put("property","humano")).getBoolean("ok"));
            assertTrue(call("rule",session,new JSONObject().put("antecedent","humano").put("consequence","mortal")).getBoolean("ok"));
            positive(call("query",session,new JSONObject().put("text",query).put("split","holdout").put("expected_status",1)));
            JSONObject validation=call("validate",session,null).getJSONObject("validation");
            assertTrue(validation.toString(),validation.getBoolean("activation_allowed"));
            JSONObject activation=call("activate",session,null);assertTrue(activation.getBoolean("active"));
            String request="c17-live-restart-"+UUID.randomUUID();
            JSONObject live=U03Runtime.turn(app(),request,query,"");positive(live);
            JSONObject activeSnapshot=snapshot();
            assertTrue(conversation(new JSONObject().put("action","clear_view").put("request_id","restart-view-"+UUID.randomUUID())).getBoolean("ok"));
            JSONObject conversationRequest=new JSONObject().put("action","send").put("request_id","restart-conversation-"+UUID.randomUUID()).put("text",query);
            JSONObject conversational=conversation(conversationRequest);positive(conversational);assertTrue(conversational.getBoolean("native_XI"));
            JSONArray messages=conversation(new JSONObject().put("action","history")).getJSONArray("messages");
            assertEquals(2,messages.length());assertEquals("user",messages.getJSONObject(0).getString("role"));
            assertEquals(query,messages.getJSONObject(0).getString("text"));assertEquals("assistant",messages.getJSONObject(1).getString("role"));
            assertEquals(conversational.getString("reply"),messages.getJSONObject(1).getString("text"));
            String conversationReceiptSha=canonicalSha(conversational.getJSONObject("receipt")),historySha=canonicalSha(messages);
            assertEquals(conversationReceiptSha,canonicalSha(messages.getJSONObject(1).getJSONObject("provenance").getJSONObject("receipt")));
            same(activeSnapshot,snapshot());
            assertTrue(saved.edit().putString("session_id",session).putString("backup_id",activation.getString("backup_id"))
                .putString("live_request",request).putString("live_receipt_sha256",live.getString("receipt_sha256"))
                .putString("active_snapshot",activeSnapshot.toString()).putString("original_snapshot",original.toString())
                .putString("conversation_request",conversationRequest.toString()).putString("conversation_history",messages.toString())
                .putString("conversation_history_sha256",historySha).putString("conversation_receipt_sha256",conversationReceiptSha)
                .putString("conversation_result_sha256",canonicalSha(conversational))
                .putInt("pid",android.os.Process.myPid()).commit());
            write("training-restart-seed.json",new JSONObject().put("passed",true).put("phase","seed")
                .put("session_id",session).put("pid",android.os.Process.myPid()).put("validation",validation)
                .put("activation",activation).put("ordinary_chat",live).put("active_snapshot",activeSnapshot)
                .put("conversation_query_was_read_only",true).put("conversation_history",messages)
                .put("conversation_history_sha256",historySha).put("conversation_receipt_sha256",conversationReceiptSha));
        }else if("verify".equals(phase)){
            assertTrue("The seed phase must have completed",saved.contains("session_id"));
            assertNotEquals("A real external process restart is mandatory",saved.getInt("pid",-1),android.os.Process.myPid());
            String session=saved.getString("session_id",null);
            JSONObject active=new JSONObject(saved.getString("active_snapshot","{}"));same(active,snapshot());
            JSONObject status=call("status",session,null);
            assertTrue(status.toString(),status.getJSONObject("session").getBoolean("active"));
            assertTrue(status.getJSONObject("session").getInt("training_count")>=2);
            JSONObject live=U03Runtime.turn(app(),saved.getString("live_request",null),query,"");positive(live);
            assertEquals(saved.getString("live_receipt_sha256",null),live.getString("receipt_sha256"));same(active,snapshot());
            assertTrue(U03Runtime.status(app()).getJSONObject("memory").getBoolean("C1_synchronized_with_U02"));
            assertTrue("Seed saved the personal conversation",saved.contains("conversation_request"));
            JSONArray expectedHistory=new JSONArray(saved.getString("conversation_history","[]"));
            JSONArray reopenedHistory=conversation(new JSONObject().put("action","history")).getJSONArray("messages");
            String historySha=canonicalSha(reopenedHistory);
            assertEquals(saved.getString("conversation_history_sha256",null),historySha);
            assertEquals(canonical(expectedHistory),canonical(reopenedHistory));
            JSONObject retried=conversation(new JSONObject(saved.getString("conversation_request","{}")));positive(retried);assertTrue(retried.getBoolean("native_XI"));
            assertEquals(saved.getString("conversation_result_sha256",null),canonicalSha(retried));
            assertEquals(saved.getString("conversation_receipt_sha256",null),canonicalSha(retried.getJSONObject("receipt")));
            JSONArray afterRetry=conversation(new JSONObject().put("action","history")).getJSONArray("messages");
            assertEquals("Exact retry must not duplicate user/assistant messages",2,afterRetry.length());
            assertEquals(canonical(reopenedHistory),canonical(afterRetry));same(active,snapshot());
            JSONObject restored=call("restore",session,new JSONObject().put("backup_id",saved.getString("backup_id",null))
                .put("confirm_discard_new_activity",true));assertTrue(restored.getBoolean("restored"));
            same(new JSONObject(saved.getString("original_snapshot","{}")),snapshot());
            write("training-restart-verify.json",new JSONObject().put("passed",true).put("phase","verify")
                .put("session_id",session).put("seed_pid",saved.getInt("pid",-1)).put("verify_pid",android.os.Process.myPid())
                .put("real_process_restart",true).put("training_session_preserved",true)
                .put("exact_live_receipt_replayed",true).put("active_model_restored",true)
                .put("ordinary_chat",live).put("restored_personal_snapshot",snapshot())
                .put("conversation_survived_process_restart",true).put("conversation_exact_request_replayed",true)
                .put("conversation_retry_no_duplicate_messages",true).put("conversation_query_was_read_only",true)
                .put("conversation_history_sha256",historySha).put("conversation_receipt_sha256",canonicalSha(retried.getJSONObject("receipt")))
                .put("conversation_history",afterRetry));
        }else fail("Pass training_phase=seed or training_phase=verify; an in-process reset is insufficient");
    }
}
