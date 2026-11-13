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
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.UUID;
import static org.junit.Assert.*;

/** Runs once inside the actual C18 APK and again after adb install -r of C19. */
@RunWith(AndroidJUnit4.class)
public final class ChatUpgradeTest {
    private Context app(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private JSONObject call(JSONObject args)throws Exception{return U03Runtime.operation(app(),"conversation",args.toString());}
    private JSONObject request(String action)throws Exception{return new JSONObject().put("action",action).put("request_id","upgrade-"+UUID.randomUUID());}
    private JSONObject history(String conversation)throws Exception{
        JSONObject args=new JSONObject().put("action","history");if(conversation!=null)args.put("conversation_id",conversation);return call(args);
    }
    private JSONObject snapshot()throws Exception{return U03Runtime.status(app()).getJSONObject("snapshot");}
    private long version()throws Exception{return app().getPackageManager().getPackageInfo(app().getPackageName(),0).getLongVersionCode();}
    private JSONObject send(String text)throws Exception{return call(request("send").put("text",text));}
    private JSONObject queryResult(JSONObject result)throws Exception{
        JSONObject nativeResult=ConversationProof.result(result,"query");assertEquals(1,nativeResult.getInt("status"));
        assertTrue("The native personal fact has a proof",nativeResult.getJSONArray("proof").length()>0);return nativeResult;
    }
    @Test public void c18JournalSurvivesRealApplicationUpgrade()throws Exception {
        String phase=InstrumentationRegistry.getArguments().getString("chat_upgrade_phase","");
        SharedPreferences saved=app().getSharedPreferences("c19-ci-real-apk-upgrade",Context.MODE_PRIVATE);
        U03Runtime.start(app());
        if("seed".equals(phase)){
            assertEquals("Seed must execute the released C18 application code",4,version());
            JSONObject first=call(request("clear_view"));int firstView=first.getInt("view_id");
            JSONObject taught=send("recuerda que Aurora Legado es robot");
            assertEquals(1,ConversationProof.result(taught,"put").getInt("status"));
            JSONObject replayRequest=request("send").put("text","dime si Aurora Legado es robot");
            JSONObject answer=call(replayRequest);queryResult(answer);
            assertFalse("C18 is genuinely running, not a fabricated old fixture",answer.has("conversation_id"));
            JSONArray firstMessages=history(null).getJSONArray("messages");assertEquals(4,firstMessages.length());
            JSONObject second=call(request("clear_view"));int secondView=second.getInt("view_id");assertNotEquals(firstView,secondView);
            JSONObject math=send("calcula 7 + 3");assertEquals(10,ConversationProof.result(math,"math").getInt("value"));
            JSONArray secondMessages=history(null).getJSONArray("messages");assertEquals(2,secondMessages.length());
            JSONArray all=call(new JSONObject().put("action","history").put("include_archived",true)).getJSONArray("messages");
            assertEquals("Both C18 views are present before the real upgrade",6,all.length());
            JSONObject personal=snapshot();
            assertTrue(saved.edit().putInt("seed_pid",android.os.Process.myPid()).putLong("version_code",version())
                .putInt("first_view",firstView).putInt("second_view",secondView)
                .putString("first_messages",firstMessages.toString()).putString("second_messages",secondMessages.toString())
                .putString("all_messages",all.toString()).putString("personal_snapshot",personal.toString())
                .putString("replay_request",replayRequest.toString()).putString("replay_result",answer.toString()).commit());
            ConversationProof.write(app(),"chat-upgrade-seed.json",new JSONObject().put("passed",true).put("phase","seed")
                .put("version_code",version()).put("pid",android.os.Process.myPid()).put("legacy_views",2)
                .put("first_view_id",firstView).put("second_view_id",secondView)
                .put("first_messages",firstMessages).put("second_messages",secondMessages)
                .put("messages_sha256",ConversationProof.sha(ConversationProof.legacyMessages(all)))
                .put("personal_snapshot",personal).put("replay_result_sha256",ConversationProof.sha(answer)));
        }else if("verify".equals(phase)){
            assertTrue("The seed phase ran in the C18 APK",saved.contains("replay_result"));
            assertEquals(4,saved.getLong("version_code",-1));assertEquals("Verify must execute the updated APK",6,version());
            assertNotEquals("Upgrade must cross a real process boundary",saved.getInt("seed_pid",-1),android.os.Process.myPid());
            JSONObject personal=new JSONObject(saved.getString("personal_snapshot","{}"));ConversationProof.sameSnapshot(personal,snapshot());
            String first="legacy-view-"+saved.getInt("first_view",-1),second="legacy-view-"+saved.getInt("second_view",-1);
            JSONObject listed=call(new JSONObject().put("action","list").put("include_archived",true));
            assertEquals("C18's active view remains the active conversation",second,listed.getString("active_conversation_id"));
            JSONObject oldFirst=ConversationProof.findConversation(listed.getJSONArray("conversations"),first);
            JSONObject oldSecond=ConversationProof.findConversation(listed.getJSONArray("conversations"),second);
            assertFalse("Older C18 views are immediately visible in the ordinary chat list",oldFirst.getBoolean("archived"));assertFalse(oldSecond.getBoolean("archived"));
            JSONArray visible=call(new JSONObject().put("action","list")).getJSONArray("conversations");
            ConversationProof.findConversation(visible,first);ConversationProof.findConversation(visible,second);
            JSONArray expectedFirst=new JSONArray(saved.getString("first_messages","[]")),expectedSecond=new JSONArray(saved.getString("second_messages","[]"));
            JSONArray migratedFirst=history(first).getJSONArray("messages"),migratedSecond=history(second).getJSONArray("messages");
            ConversationProof.sameMessages(expectedFirst,migratedFirst);ConversationProof.sameMessages(expectedSecond,migratedSecond);
            JSONObject oldAnswer=new JSONObject(saved.getString("replay_result","{}"));
            JSONObject replay=call(new JSONObject(saved.getString("replay_request","{}")));queryResult(replay);
            assertEquals("The old complete result is replayed byte-semantically, without new fields",ConversationProof.canonical(oldAnswer),ConversationProof.canonical(replay));
            assertEquals("Replaying another thread's old request does not select it",second,history(null).getString("active_conversation_id"));
            ConversationProof.sameMessages(expectedFirst,history(first).getJSONArray("messages"));
            ConversationProof.sameMessages(expectedSecond,history(second).getJSONArray("messages"));
            call(request("select").put("conversation_id",first));
            JSONObject followup=call(request("send").put("conversation_id",first).put("text","¿y por qué?"));queryResult(followup);
            JSONObject provenance=followup.getJSONArray("messages").getJSONObject(1).getJSONObject("provenance");
            assertTrue("The migrated context explains the originally taught subject",provenance.getString("normalized_prompt").contains("Aurora Legado"));
            JSONArray firstAfter=history(first).getJSONArray("messages");assertEquals(6,firstAfter.length());
            ConversationProof.sameMessages(expectedFirst,ConversationProof.prefix(firstAfter,4));
            ConversationProof.sameMessages(expectedSecond,history(second).getJSONArray("messages"));
            ConversationProof.sameSnapshot(personal,snapshot());
            ConversationProof.write(app(),"chat-upgrade-verify.json",new JSONObject().put("passed",true).put("phase","verify")
                .put("legacy_version_code",saved.getLong("version_code",-1)).put("upgraded_version_code",version())
                .put("seed_pid",saved.getInt("seed_pid",-1)).put("verify_pid",android.os.Process.myPid())
                .put("actual_apk_upgrade",true).put("distinct_process",true).put("personal_snapshot_unchanged",true)
                .put("all_legacy_views_recovered",true).put("all_legacy_messages_preserved",true)
                .put("exact_legacy_request_replayed",true).put("replay_kept_active_conversation",true)
                .put("no_duplicate_messages",true).put("migrated_thread_context_works",true)
                .put("migrated_conversations",listed).put("replay_result_sha256",ConversationProof.sha(replay))
                .put("first_messages",firstAfter).put("second_messages",migratedSecond).put("followup",followup)
                .put("personal_snapshot",snapshot()));
        }else fail("Pass chat_upgrade_phase=seed with the actual C18 APK, then verify after install -r of C19");
    }
}

/** JSON/provenance assertions shared by upgrade and continuity tests, compatible with C18. */
final class ConversationProof {
    private ConversationProof(){}
    static String canonical(Object value)throws Exception {
        if(value==null||value==JSONObject.NULL)return "null";
        if(value instanceof JSONObject){JSONObject object=(JSONObject)value;ArrayList<String> keys=new ArrayList<>();
            Iterator<String> names=object.keys();while(names.hasNext())keys.add(names.next());Collections.sort(keys);
            StringBuilder text=new StringBuilder("{");for(String key:keys){if(text.length()>1)text.append(',');
                text.append(JSONObject.quote(key)).append(':').append(canonical(object.get(key)));}return text.append('}').toString();}
        if(value instanceof JSONArray){JSONArray array=(JSONArray)value;StringBuilder text=new StringBuilder("[");
            for(int i=0;i<array.length();i++){if(i>0)text.append(',');text.append(canonical(array.get(i)));}return text.append(']').toString();}
        if(value instanceof Number)return new BigDecimal(value.toString()).stripTrailingZeros().toPlainString();
        if(value instanceof Boolean)return value.toString();return JSONObject.quote(value.toString());
    }
    static String sha(Object value)throws Exception {
        byte[] digest=MessageDigest.getInstance("SHA-256").digest(canonical(value).getBytes(StandardCharsets.UTF_8));
        StringBuilder text=new StringBuilder();for(byte b:digest)text.append(String.format("%02x",b&255));return text.toString();
    }
    static JSONArray legacyMessages(JSONArray messages)throws Exception {
        JSONArray result=new JSONArray();for(int i=0;i<messages.length();i++){JSONObject source=messages.getJSONObject(i),item=new JSONObject();
            for(String field:new String[]{"id","role","text","request_id","created_at_ms","response_origin","provenance"})
                if(source.has(field))item.put(field,source.get(field));result.put(item);}return result;
    }
    static JSONArray prefix(JSONArray messages,int length)throws Exception {
        assertTrue(messages.length()>=length);JSONArray result=new JSONArray();for(int i=0;i<length;i++)result.put(messages.getJSONObject(i));return result;
    }
    static void sameMessages(JSONArray expected,JSONArray actual)throws Exception {
        assertEquals("No messages disappear or duplicate",expected.length(),actual.length());
        assertEquals("IDs, order, text, timestamps and complete provenance survive",canonical(legacyMessages(expected)),canonical(legacyMessages(actual)));
    }
    static JSONObject findConversation(JSONArray listed,String identifier)throws Exception {
        for(int i=0;i<listed.length();i++){JSONObject item=listed.getJSONObject(i);if(identifier.equals(item.getString("id")))return item;}
        throw new AssertionError("Missing persisted conversation "+identifier+": "+listed);
    }
    static JSONObject result(JSONObject response,String kind)throws Exception {
        assertTrue(response.toString(),response.getBoolean("ok"));assertTrue("Original native inference is used",response.getBoolean("native_XI"));
        JSONObject receipt=response.getJSONObject("receipt");boolean original=false;JSONArray trace=receipt.getJSONArray("trace");
        for(int i=0;i<trace.length();i++)if(trace.getJSONObject(i).optBoolean("native"))original=true;
        assertTrue("Native execution receipt exists",original);JSONArray results=receipt.getJSONArray("results");
        for(int i=0;i<results.length();i++)if(kind.equals(results.getJSONObject(i).optString("kind")))return results.getJSONObject(i);
        throw new AssertionError("Missing native "+kind+" result: "+response);
    }
    static void sameSnapshot(JSONObject expected,JSONObject actual)throws Exception {
        for(String key:new String[]{"revision","metadata_sha256","tasks","feedback"})assertEquals(key,expected.get(key),actual.get(key));
        JSONObject banks=expected.getJSONObject("banks");assertEquals(7,banks.length());assertEquals(7,actual.getJSONObject("banks").length());
        Iterator<String> names=banks.keys();while(names.hasNext()){String name=names.next();assertEquals(name,banks.getString(name),actual.getJSONObject("banks").getString(name));}
    }
    static void write(Context app,String filename,JSONObject value)throws Exception {
        try(FileOutputStream out=new FileOutputStream(new File(app.getFilesDir(),filename))){out.write(value.toString(2).getBytes(StandardCharsets.UTF_8));}
    }
}
