package com.bbyq.u03;

import android.app.Activity;
import android.content.Context;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.Rect;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.EditText;
import android.widget.TextView;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.FixMethodOrder;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestWatcher;
import org.junit.runner.Description;
import org.junit.runner.RunWith;
import org.junit.runners.MethodSorters;
import java.io.File;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import static org.junit.Assert.*;

/** User-visible continuity, real thread navigation, contextual XI and the C18 journal. */
@RunWith(AndroidJUnit4.class)
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public final class ChatContinuityTest {
    private String oldFont,oldNavigation;
    @BeforeClass public static void initialize()throws Exception {
        U03Runtime.start(UiEvidence.app());
        UiEvidence.write("chat-continuity-proof.json",new JSONObject().put("schema","BBYQ-C19-chat-continuity-v1")
            .put("android_api",Build.VERSION.SDK_INT).put("cases",new JSONObject()));
    }
    @Before public void prepare()throws Exception {
        oldFont=UiEvidence.shell("settings get system font_scale").trim();
        oldNavigation=UiEvidence.shell("settings get secure navigation_mode").trim();
        UiEvidence.finishActivities();UiEvidence.shell("settings put system font_scale 1.0");UiEvidence.navigation(false);
        assertTrue(UiEvidence.app().getSharedPreferences(UiKit.PREFS,Context.MODE_PRIVATE).edit().putFloat("font_scale",1f).commit());
    }
    @Rule public final TestWatcher evidence=new TestWatcher(){
        @Override protected void failed(Throwable error,Description test){
            try{String path="chat-failure-"+test.getMethodName()+".png";UiEvidence.screenshot(path);
                record(test.getMethodName(),new JSONObject().put("passed",false).put("error",error.toString()).put("screenshot",path));}catch(Exception ignored){}
        }
        @Override protected void finished(Description test){
            try{UiEvidence.finishActivities();
                if(oldFont!=null&&!oldFont.isEmpty()&&!oldFont.equals("null"))UiEvidence.shell("settings put system font_scale "+oldFont);
                else UiEvidence.shell("settings delete system font_scale");
                if("0".equals(oldNavigation))UiEvidence.navigation(false);else if("2".equals(oldNavigation))UiEvidence.navigation(true);
            }catch(Exception error){throw new AssertionError("Restore device configuration",error);}
        }
    };
    private static void record(String name,JSONObject result)throws Exception {
        JSONObject proof=UiEvidence.read("chat-continuity-proof.json");proof.getJSONObject("cases").put(name,result);UiEvidence.write("chat-continuity-proof.json",proof);
    }
    static JSONObject call(JSONObject args)throws Exception{return U03Runtime.operation(UiEvidence.app(),"conversation",args.toString());}
    static JSONObject request(String action)throws Exception{return new JSONObject().put("action",action).put("request_id","chat-ci-"+UUID.randomUUID());}
    static JSONObject history(String id)throws Exception {
        JSONObject args=new JSONObject().put("action","history");if(id!=null)args.put("conversation_id",id);return call(args);
    }
    private static String create(String title)throws Exception{return call(request("create").put("title",title)).getJSONObject("conversation").getString("id");}
    private static JSONObject send(String id,String text)throws Exception{return call(request("send").put("conversation_id",id).put("text",text));}
    private static JSONObject listed(String id)throws Exception {
        return ConversationProof.findConversation(call(new JSONObject().put("action","list").put("include_archived",true)).getJSONArray("conversations"),id);
    }
    static IntegratedActivity home(String id,boolean launch)throws Exception {
        IntegratedActivity activity=launch?UiEvidence.start(IntegratedActivity.class):UiEvidence.awaitActivity(IntegratedActivity.class);
        UiEvidence.until("The selected conversation is actually on screen",15000,()->UiEvidence.ui(()->{
            View transcript=activity.findViewById(0x5802005);return transcript!=null&&("conversation:"+id).equals(transcript.getTag())&&transcript.getWidth()>0;
        }));return activity;
    }
    private static boolean containsExactText(View view,String text){
        if(view instanceof TextView&&text.contentEquals(((TextView)view).getText()))return true;
        if(view instanceof ViewGroup){ViewGroup group=(ViewGroup)view;for(int i=0;i<group.getChildCount();i++)if(containsExactText(group.getChildAt(i),text))return true;}
        return false;
    }
    private static boolean renderedMatches(IntegratedActivity activity,String id,JSONArray expected)throws Exception {
        ViewGroup transcript=activity.findViewById(0x5802005);
        if(transcript==null||!("conversation:"+id).equals(transcript.getTag()))return false;
        int count=0;
        for(int i=0;i<transcript.getChildCount();i++){
            View child=transcript.getChildAt(i);Object tag=child.getTag();
            if(tag==null||!tag.toString().startsWith("message:"))continue;
            if(count>=expected.length())return false;JSONObject message=expected.getJSONObject(count++);
            if(!("message:"+message.getString("id")).equals(tag)||!containsExactText(child,message.getString("text"))
                ||child.getWidth()<=0||child.getHeight()<=0||!child.isShown())return false;
        }
        return count==expected.length();
    }
    static JSONArray assertRendered(IntegratedActivity activity,String id,JSONArray expected)throws Exception {
        UiEvidence.until("Every saved message remains a distinct real bubble before navigation or recreation",15000,
            ()->UiEvidence.ui(()->renderedMatches(activity,id,expected)));
        return UiEvidence.ui(()->{
            ViewGroup transcript=activity.findViewById(0x5802005);JSONArray actual=new JSONArray();Set<String> unique=new HashSet<>();
            for(int i=0;i<transcript.getChildCount();i++){
                View bubble=transcript.getChildAt(i);Object tag=bubble.getTag();if(tag==null||!tag.toString().startsWith("message:"))continue;
                String messageId=tag.toString().substring("message:".length());assertTrue("No duplicate UI bubble",unique.add(messageId));
                assertSame("Message is attached directly to the visible transcript",transcript,bubble.getParent());
                actual.put(new JSONObject().put("id",messageId).put("rendered_text",UiEvidence.textTree(bubble))
                    .put("rect",UiEvidence.rect(UiEvidence.screenRect(bubble))).put("shown",bubble.isShown()));
            }
            assertEquals(expected.length(),actual.length());return actual;
        });
    }
    static JSONObject sendUi(IntegratedActivity activity,String id,String text)throws Exception {
        JSONArray before=history(id).getJSONArray("messages");
        UiEvidence.ui(()->{((EditText)activity.findViewById(0x5802003)).setText(text);return null;});
        UiEvidence.until("Send is ready for this thread",15000,()->UiEvidence.ui(()->activity.findViewById(0x5802004).isEnabled()));
        UiEvidence.assertHomeSafe(UiEvidence.homeBounds(activity,UiEvidence.imeVisible(activity)));
        UiEvidence.tap(UiEvidence.ui(()->activity.findViewById(0x5802004)));
        AtomicReference<JSONArray> completed=new AtomicReference<>();
        UiEvidence.until("A touch submits one complete native turn to the chosen thread",90000,()->{
            JSONArray now=history(id).getJSONArray("messages");if(now.length()!=before.length()+2)return false;
            JSONObject user=now.getJSONObject(before.length()),assistant=now.getJSONObject(before.length()+1);
            if(!text.equals(user.getString("text"))||!"user".equals(user.getString("role"))||!"assistant".equals(assistant.getString("role")))return false;
            completed.set(now);return true;
        });
        JSONArray after=completed.get();ConversationProof.sameMessages(before,ConversationProof.prefix(after,before.length()));
        assertRendered(activity,id,after);return after.getJSONObject(after.length()-1);
    }
    private static JSONObject makeBubbleVisible(IntegratedActivity activity,String messageId)throws Exception {
        View bubble=UiEvidence.ui(()->activity.findViewById(0x5802005).findViewWithTag("message:"+messageId));assertNotNull(bubble);
        UiEvidence.ui(()->{bubble.requestRectangleOnScreen(new Rect(0,0,bubble.getWidth(),bubble.getHeight()),true);return null;});
        UiEvidence.until("The saved message is reachable by scrolling the real transcript",10000,()->UiEvidence.ui(()->{
            Rect visible=new Rect();return bubble.getGlobalVisibleRect(visible)&&visible.equals(UiEvidence.screenRect(bubble));
        }));return UiEvidence.ui(()->new JSONObject().put("id",messageId).put("rect",UiEvidence.rect(UiEvidence.screenRect(bubble))));
    }
    @Test public void C01_threeTurnsKeepSixRealBubbles()throws Exception {
        String id=create("Tres turnos completos");IntegratedActivity activity=home(id,true);
        String[] questions={"calcula 7 + 3","calcula 9 - 4","calcula 6 * 7"};int[] answers={10,5,42};JSONArray receipts=new JSONArray();
        for(int i=0;i<questions.length;i++){
            JSONObject answer=sendUi(activity,id,questions[i]);assertEquals(answers[i],UiEvidence.nativeResult(answer,"math").getInt("value"));receipts.put(answer);
            assertEquals((i+1)*2,assertRendered(activity,id,history(id).getJSONArray("messages")).length());
        }
        JSONArray messages=history(id).getJSONArray("messages");assertEquals(6,messages.length());
        JSONArray bubbles=assertRendered(activity,id,messages);UiEvidence.hideKeyboard(activity);
        JSONObject first=makeBubbleVisible(activity,messages.getJSONObject(0).getString("id"));UiEvidence.screenshot("chat-three-turns-top.png");
        JSONObject last=makeBubbleVisible(activity,messages.getJSONObject(5).getString("id"));UiEvidence.screenshot("chat-three-turns-bottom.png");
        assertEquals("Scrolling does not hide/delete earlier bubble objects",6,assertRendered(activity,id,messages).length());
        JSONObject bounds=UiEvidence.homeBounds(activity,false);UiEvidence.assertHomeSafe(bounds);UiEvidence.write("chat-three-turns-bounds.json",bounds);
        record("C01_threeTurnsKeepSixRealBubbles",new JSONObject().put("passed",true).put("conversation_id",id)
            .put("three_real_ui_sends",true).put("six_bubbles_before_recreation",true).put("all_message_ids_and_text_preserved",true)
            .put("messages",messages).put("real_bubbles",bubbles).put("first_visible",first).put("last_visible",last).put("native_answers",receipts));
    }
    static ChatsActivity chats(IntegratedActivity activity)throws Exception {
        UiEvidence.hideKeyboard(activity);UiEvidence.tap(UiEvidence.ui(()->activity.findViewById(0x5802015)));return UiEvidence.awaitActivity(ChatsActivity.class);
    }
    private static View tagged(Activity activity,String tag)throws Exception {
        UiEvidence.until("Visible chat control exists: "+tag,15000,()->UiEvidence.ui(()->activity.getWindow().getDecorView().findViewWithTag(tag)!=null));
        return UiEvidence.ui(()->activity.getWindow().getDecorView().findViewWithTag(tag));
    }
    static void tapTagged(Activity activity,String tag)throws Exception {
        AtomicReference<View> target=new AtomicReference<>();
        UiEvidence.until("Chat control can be touched without clipping: "+tag,15000,()->UiEvidence.ui(()->{
            // List refreshes replace real rows. Do not retain an obsolete disabled
            // row while waiting for the completed operation to reach the screen.
            View view=activity.getWindow().getDecorView().findViewWithTag(tag);
            if(view==null||!view.isEnabled()||!view.isAttachedToWindow()||view.getHeight()==0)return false;
            view.requestRectangleOnScreen(new Rect(0,0,view.getWidth(),view.getHeight()),true);
            Rect visible=new Rect();boolean ready=view.getGlobalVisibleRect(visible)&&visible.equals(UiEvidence.screenRect(view));
            if(ready)target.set(view);return ready;
        }));UiEvidence.tap(target.get());
    }
    static void draft(IntegratedActivity activity,String text,int cursor)throws Exception {
        UiEvidence.ui(()->{EditText input=activity.findViewById(0x5802003);input.setText(text);input.setSelection(cursor);return null;});
    }
    static void assertDraft(IntegratedActivity activity,String text,int cursor)throws Exception {
        UiEvidence.until("The selected thread restores its own draft and caret",10000,()->UiEvidence.ui(()->{
            EditText input=activity.findViewById(0x5802003);return text.contentEquals(input.getText())&&input.getSelectionStart()==cursor;
        }));
    }
    private static AccessibilityNodeInfo editNode(AccessibilityNodeInfo node){
        if(node==null)return null;
        if(node.isVisibleToUser()&&node.isEnabled()&&String.valueOf(node.getClassName()).contains("EditText"))return AccessibilityNodeInfo.obtain(node);
        for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);if(child!=null){
            AccessibilityNodeInfo found=editNode(child);child.recycle();if(found!=null)return found;}}
        return null;
    }
    private static void dialogText(String text)throws Exception {
        UiEvidence.until("Rename dialog exposes a real editable field",10000,()->{
            AccessibilityNodeInfo root=UiEvidence.instrument().getUiAutomation().getRootInActiveWindow();if(root==null)return false;
            AccessibilityNodeInfo edit=editNode(root);root.recycle();if(edit==null)return false;
            Bundle args=new Bundle();args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,text);
            boolean changed=edit.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT,args);edit.recycle();return changed;
        });
    }
    private static Rect nativeDialogButton(AccessibilityNodeInfo node,String label){
        if(node==null)return null;
        // Android's native AlertDialog exposes its themed, uppercase button text.
        // Locate that visible button; application labels retain their exact checks.
        if(node.isVisibleToUser()&&node.isEnabled()&&String.valueOf(node.getClassName()).contains("Button")
            &&label.equalsIgnoreCase(String.valueOf(node.getText()))){
            Rect bounds=new Rect();node.getBoundsInScreen(bounds);if(bounds.width()>0&&bounds.height()>0)return bounds;
        }
        for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);if(child!=null){
            Rect found=nativeDialogButton(child,label);child.recycle();if(found!=null)return found;}}
        return null;
    }
    private static void tapDialogButton(String label)throws Exception {
        AtomicReference<Rect> target=new AtomicReference<>();
        UiEvidence.until("The native dialog exposes its reachable "+label+" button",10000,()->{
            AccessibilityNodeInfo root=UiEvidence.instrument().getUiAutomation().getRootInActiveWindow();if(root==null)return false;
            Rect found=nativeDialogButton(root,label);root.recycle();target.set(found);return found!=null;
        });UiEvidence.tap(target.get());
    }
    @Test public void C02_threadNavigationDraftsRenameArchiveAndRecreation()throws Exception {
        String first=create("Primer chat de continuidad");IntegratedActivity a=home(first,true);
        sendUi(a,first,"hola");JSONArray firstMessages=history(first).getJSONArray("messages");
        String firstDraft="Mi borrador del primer chat",secondDraft="Una idea diferente en el segundo";
        draft(a,firstDraft,5);ChatsActivity list=chats(a);ChatsActivity firstList=list;
        UiEvidence.until("The loaded chat list enables creation",15000,()->UiEvidence.ui(()->firstList.findViewById(0x5807002).isEnabled()));
        UiEvidence.tap(UiEvidence.ui(()->firstList.findViewById(0x5807002)));
        UiEvidence.until("New chat selects a different persistent thread",15000,()->!first.equals(history(null).getString("active_conversation_id")));
        String second=history(null).getString("active_conversation_id");IntegratedActivity b=home(second,false);
        assertDraft(b,"",0);sendUi(b,second,"calcula 9 - 4");JSONArray secondMessages=history(second).getJSONArray("messages");draft(b,secondDraft,7);
        list=chats(b);tapTagged(list,"conversation:"+first);a=home(first,false);assertDraft(a,firstDraft,5);assertRendered(a,first,firstMessages);
        list=chats(a);tapTagged(list,"conversation_options:"+first);UiEvidence.tapText("Renombrar");
        String title="Mi conversación conservada";dialogText(title);tapDialogButton("Guardar");
        UiEvidence.until("Rename is durable and visible in its real row",15000,()->title.equals(listed(first).getString("title")));
        ChatsActivity renamedList=list;UiEvidence.until("The list actually renders the new title",10000,()->UiEvidence.ui(()->
            containsExactText(renamedList.getWindow().getDecorView().findViewWithTag("conversation:"+first),title)));
        UiEvidence.hideKeyboard(list);JSONObject listBounds=UiEvidence.bounds(list,new int[]{0x5807001,0x5807002,0x5807003,0x5807004,0x5807005,0x5807007},false);
        UiEvidence.assertSafe(listBounds);UiEvidence.write("chat-list-bounds.json",listBounds);
        UiEvidence.screenshot("chat-list-renamed.png");
        tapTagged(list,"conversation_options:"+first);UiEvidence.tapText("Archivar chat");tapDialogButton("Archivar");
        UiEvidence.until("Archive is persisted and no longer active",15000,()->listed(first).getBoolean("archived")&&!first.equals(history(null).getString("active_conversation_id")));
        ChatsActivity archivedList=list;UiEvidence.until("Archived chat leaves the ordinary list",10000,()->UiEvidence.ui(()->
            archivedList.getWindow().getDecorView().findViewWithTag("conversation:"+first)==null));
        UiEvidence.tap(UiEvidence.ui(()->archivedList.findViewById(0x5807005)));tagged(list,"conversation_restore:"+first);UiEvidence.screenshot("chat-list-archived.png");
        tapTagged(list,"conversation_restore:"+first);UiEvidence.until("Restore keeps all saved chat data",15000,()->!listed(first).getBoolean("archived"));
        UiEvidence.tap(UiEvidence.ui(()->archivedList.findViewById(0x5807004)));tapTagged(list,"conversation:"+first);
        a=home(first,false);assertDraft(a,firstDraft,5);assertRendered(a,first,firstMessages);
        IntegratedActivity restored=a;assertEquals(title,UiEvidence.ui(()->((TextView)restored.findViewById(0x5802014)).getText().toString()));
        ConversationProof.sameMessages(firstMessages,history(first).getJSONArray("messages"));UiEvidence.screenshot("chat-restored.png");
        list=chats(a);tapTagged(list,"conversation:"+second);b=home(second,false);assertDraft(b,secondDraft,7);assertRendered(b,second,secondMessages);
        IntegratedActivity old=b;UiEvidence.ui(()->{old.recreate();return null;});
        UiEvidence.until("The selected chat survives a genuinely new Activity instance",15000,()->{
            IntegratedActivity current=UiEvidence.resumed(IntegratedActivity.class);return current!=null&&current!=old;
        });b=home(second,false);assertDraft(b,secondDraft,7);assertRendered(b,second,secondMessages);
        ConversationProof.sameMessages(firstMessages,history(first).getJSONArray("messages"));ConversationProof.sameMessages(secondMessages,history(second).getJSONArray("messages"));
        JSONObject bounds=UiEvidence.homeBounds(b,false);UiEvidence.assertHomeSafe(bounds);UiEvidence.write("chat-restored-draft-bounds.json",bounds);
        UiEvidence.screenshot("chat-draft-recreated.png");
        record("C02_threadNavigationDraftsRenameArchiveAndRecreation",new JSONObject().put("passed",true).put("first_conversation_id",first).put("second_conversation_id",second)
            .put("new_chat_created_through_ui",true).put("drafts_and_carets_are_thread_scoped",true).put("rename_visible_and_durable",true)
            .put("archive_and_restore_preserve_messages",true).put("recreation_preserves_selected_chat",true)
            .put("first_messages",firstMessages).put("second_messages",secondMessages).put("renamed_title",title).put("geometry",bounds).put("chat_list_geometry",listBounds));
    }
    private static JSONObject resolution(JSONObject response,String sourceThread,String sourceRequest)throws Exception {
        JSONObject provenance=response.getJSONArray("messages").getJSONObject(1).getJSONObject("provenance");
        JSONObject resolution=provenance.getJSONObject("context_resolution");
        assertEquals(sourceThread,resolution.getString("source_conversation_id"));assertEquals(sourceRequest,resolution.getString("source_request_id"));
        assertFalse(resolution.getString("expanded_prompt").isEmpty());return resolution;
    }
    private static void clarification(JSONObject response)throws Exception {
        assertTrue(response.getBoolean("ok"));assertFalse("An unresolved reference is not fabricated inference",response.getBoolean("native_XI"));
        assertFalse(response.getBoolean("understood"));assertEquals("interface",response.getString("response_origin"));
        JSONObject provenance=response.getJSONArray("messages").getJSONObject(1).getJSONObject("provenance");assertFalse(provenance.getBoolean("personal_memory_written"));
    }
    @Test public void C03_contextUsesOnlyItsConversation()throws Exception {
        String first=create("Contexto de Lira");
        assertEquals(1,ConversationProof.result(send(first,"recuerda que Lira es robot"),"put").getInt("status"));
        assertEquals(1,ConversationProof.result(send(first,"recuerda que si alguien es robot entonces es máquina"),"rule").getInt("status"));
        JSONObject originalQuestion=send(first,"¿Lira es robot?");assertEquals(1,ConversationProof.result(originalQuestion,"query").getInt("status"));
        JSONObject learned=U03Runtime.status(UiEvidence.app()).getJSONObject("snapshot");
        JSONObject subjectCourtesy=send(first,"gracias");assertTrue(subjectCourtesy.getBoolean("ok"));
        String second=create("Contexto de los cálculos");
        JSONObject isolated=send(second,"¿y es máquina?");clarification(isolated);
        JSONObject related=send(first,"¿y es máquina?");assertEquals(1,ConversationProof.result(related,"query").getInt("status"));
        JSONObject subject=resolution(related,first,originalQuestion.getString("request_id"));assertTrue(subject.getString("expanded_prompt").contains("Lira"));
        assertEquals("Sending to an explicit thread does not silently select it",second,history(null).getString("active_conversation_id"));
        JSONObject why=send(first,"¿y por qué?");assertEquals(1,ConversationProof.result(why,"query").getInt("status"));
        resolution(why,first,related.getString("request_id"));
        assertTrue(why.getJSONArray("messages").getJSONObject(1).getJSONObject("provenance").getJSONArray("proof").length()>0);
        JSONObject sharedFact=send(second,"¿Lira es máquina?");assertEquals("Personal knowledge is shared; conversational references are not",1,ConversationProof.result(sharedFact,"query").getInt("status"));
        JSONObject arithmetic=send(second,"calcula 7 + 3");assertEquals(10,ConversationProof.result(arithmetic,"math").getInt("value"));
        JSONObject numberCourtesy=send(second,"gracias");assertTrue(numberCourtesy.getBoolean("ok"));
        JSONObject continued=send(second,"¿y cuánto da eso por 2?");assertEquals(20,ConversationProof.result(continued,"math").getInt("value"));
        resolution(continued,second,arithmetic.getString("request_id"));
        JSONObject wrongThreadNumber=send(first,"¿y cuánto da eso por 2?");clarification(wrongThreadNumber);
        ConversationProof.sameSnapshot(learned,U03Runtime.status(UiEvidence.app()).getJSONObject("snapshot"));
        JSONArray firstMessages=history(first).getJSONArray("messages"),secondMessages=history(second).getJSONArray("messages");Set<String> ids=new HashSet<>();
        for(int i=0;i<firstMessages.length();i++)ids.add(firstMessages.getJSONObject(i).getString("id"));
        for(int i=0;i<secondMessages.length();i++)assertFalse("Message IDs never cross threads",ids.contains(secondMessages.getJSONObject(i).getString("id")));
        IntegratedActivity activity=home(second,true);assertRendered(activity,second,secondMessages);UiEvidence.screenshot("chat-context-calculation.png");
        record("C03_contextUsesOnlyItsConversation",new JSONObject().put("passed",true).put("first_conversation_id",first).put("second_conversation_id",second)
            .put("native_subject_followup",true).put("native_explanation_followup",true).put("native_numeric_followup",true)
            .put("missing_context_requests_clarification",true).put("thread_context_isolated",true).put("global_personal_memory_preserved",true)
            .put("subject_and_number_context_survive_courtesy",true).put("subject_courtesy",subjectCourtesy).put("numeric_courtesy",numberCourtesy)
            .put("all_followups_read_only",true).put("subject_followup",related).put("why",why).put("numeric_followup",continued)
            .put("isolated_subject",isolated).put("isolated_number",wrongThreadNumber));
    }
    private static JSONObject fixtureCall(File personal,JSONObject args)throws Exception {
        Python python=Python.getInstance();PyObject base=python.getModule("u03_mobile");
        PyObject decoded=python.getModule("json").callAttr("loads",args.toString());
        PyObject answer=python.getModule("u03_conversation").callAttr("run",decoded,base.get("_root"),personal.getAbsolutePath());
        return new JSONObject(python.getModule("json").callAttr("dumps",answer).toString());
    }
    private static void copyPersonal(File destination)throws Exception {
        assertTrue(destination.getParentFile().mkdirs()||destination.getParentFile().isDirectory());
        Python python=Python.getInstance();PyObject sqlite=python.getModule("sqlite3");
        PyObject source=sqlite.callAttr("connect",python.getModule("u03_mobile").get("_db").toString());
        PyObject target=sqlite.callAttr("connect",destination.getAbsolutePath());
        try{source.callAttr("backup",target);}finally{target.callAttr("close");source.callAttr("close");}
    }
    private static void insertMessage(SQLiteDatabase db,int view,JSONObject message)throws Exception {
        db.execSQL("INSERT INTO messages VALUES(?,?,?,?,?,?,?)",new Object[]{message.getString("id"),view,message.getString("role"),message.getString("text"),
            message.getString("request_id"),message.getLong("created_at_ms"),message.has("provenance")?ConversationProof.canonical(message.getJSONObject("provenance")):null});
    }
    @Test public void C04_c18SparseViewsAndPendingRequestMigrate()throws Exception {
        String source=create("Recibo para migración aislada");JSONObject completed=send(source,"calcula 7 + 3");
        assertEquals(10,ConversationProof.result(completed,"math").getInt("value"));
        JSONObject personalBefore=U03Runtime.status(UiEvidence.app()).getJSONObject("snapshot");
        File directory=new File(UiEvidence.app().getCacheDir(),"c19-legacy-fixture-"+UUID.randomUUID());
        File legacy=new File(directory,"conversation-v1/conversation.sqlite"),personal=new File(directory,"model/personal.sqlite");
        assertTrue(legacy.getParentFile().mkdirs());copyPersonal(personal);
        JSONObject oldCompleteRequest=new JSONObject().put("action","send").put("request_id",completed.getString("request_id")).put("text","calcula 7 + 3");
        JSONObject oldResult=new JSONObject(completed.toString());oldResult.remove("conversation_id");oldResult.remove("message_scope");oldResult.put("view_id",2);
        JSONArray oldMessages=ConversationProof.legacyMessages(oldResult.getJSONArray("messages"));oldResult.put("messages",oldMessages);
        JSONObject pendingRequest=new JSONObject().put("action","send").put("request_id","legacy-pending-"+UUID.randomUUID()).put("text","calcula 9 - 4");
        JSONObject route=new JSONObject().put("kind","personal").put("prompt","calcula 9 - 4").put("write",false);
        long created=1700000000000L;JSONObject pendingUser=new JSONObject().put("id",pendingRequest.getString("request_id")+":user")
            .put("role","user").put("text",pendingRequest.getString("text")).put("request_id",pendingRequest.getString("request_id")).put("created_at_ms",created);
        try(SQLiteDatabase db=SQLiteDatabase.openOrCreateDatabase(legacy,null)){
            // The exact released C18 tables, not a C19 schema manufactured by its own migration.
            db.execSQL("CREATE TABLE preferences(key TEXT PRIMARY KEY,value TEXT NOT NULL)");db.execSQL("INSERT INTO preferences VALUES('view','0')");
            db.execSQL("CREATE TABLE requests(id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,state TEXT NOT NULL,action TEXT NOT NULL,input TEXT NOT NULL,route TEXT,view INTEGER NOT NULL,created_ms INTEGER NOT NULL,result TEXT)");
            db.execSQL("CREATE TABLE messages(id TEXT PRIMARY KEY,view INTEGER NOT NULL,role TEXT NOT NULL,text TEXT NOT NULL,request_id TEXT NOT NULL,created_ms INTEGER NOT NULL,provenance TEXT)");
            db.execSQL("INSERT INTO requests VALUES(?,?,'complete','send',?,?,2,?,?)",new Object[]{oldCompleteRequest.getString("request_id"),ConversationProof.sha(oldCompleteRequest),
                ConversationProof.canonical(oldCompleteRequest),ConversationProof.canonical(new JSONObject().put("kind","personal").put("prompt","calcula 7 + 3").put("write",false)),
                oldMessages.getJSONObject(0).getLong("created_at_ms"),ConversationProof.canonical(oldResult)});
            for(int i=0;i<oldMessages.length();i++)insertMessage(db,2,oldMessages.getJSONObject(i));
            db.execSQL("INSERT INTO requests VALUES(?,?,'pending','send',?,?,7,?,NULL)",new Object[]{pendingRequest.getString("request_id"),ConversationProof.sha(pendingRequest),
                ConversationProof.canonical(pendingRequest),ConversationProof.canonical(route),created});insertMessage(db,7,pendingUser);
        }
        JSONObject migrated=fixtureCall(personal,new JSONObject().put("action","list"));JSONArray threads=migrated.getJSONArray("conversations");
        assertEquals("Only actual legacy views migrate; no phantom 1/3/4/5/6 range",3,threads.length());
        for(String id:new String[]{"legacy-view-0","legacy-view-2","legacy-view-7"})assertFalse(ConversationProof.findConversation(threads,id).getBoolean("archived"));
        assertEquals("The empty active C18 view remains selected","legacy-view-0",migrated.getString("active_conversation_id"));
        JSONObject empty=fixtureCall(personal,new JSONObject().put("action","history"));assertEquals(0,empty.getJSONArray("messages").length());assertEquals(0,empty.getJSONArray("pending_requests").length());
        ConversationProof.sameMessages(oldMessages,fixtureCall(personal,new JSONObject().put("action","history").put("conversation_id","legacy-view-2")).getJSONArray("messages"));
        JSONObject pending=fixtureCall(personal,new JSONObject().put("action","history").put("conversation_id","legacy-view-7"));
        assertEquals(1,pending.getJSONArray("messages").length());assertEquals(1,pending.getJSONArray("pending_requests").length());
        JSONObject pendingMeta=pending.getJSONArray("pending_requests").getJSONObject(0);assertEquals("legacy-view-7",pendingMeta.getString("conversation_id"));
        assertEquals(pendingRequest.getString("request_id"),pendingMeta.getString("request_id"));
        JSONObject replay=fixtureCall(personal,oldCompleteRequest);assertEquals(ConversationProof.canonical(oldResult),ConversationProof.canonical(replay));
        JSONObject resumed=fixtureCall(personal,pendingRequest);assertEquals(5,ConversationProof.result(resumed,"math").getInt("value"));
        JSONObject resumedHistory=fixtureCall(personal,new JSONObject().put("action","history").put("conversation_id","legacy-view-7"));
        assertEquals(2,resumedHistory.getJSONArray("messages").length());assertEquals(0,resumedHistory.getJSONArray("pending_requests").length());
        ConversationProof.sameMessages(new JSONArray().put(pendingUser),ConversationProof.prefix(resumedHistory.getJSONArray("messages"),1));
        assertEquals("Replay and pending completion do not change active chat","legacy-view-0",resumedHistory.getString("active_conversation_id"));
        assertEquals(ConversationProof.canonical(resumed),ConversationProof.canonical(fixtureCall(personal,pendingRequest)));
        assertEquals(2,fixtureCall(personal,new JSONObject().put("action","history").put("conversation_id","legacy-view-7")).getJSONArray("messages").length());
        ConversationProof.sameMessages(oldMessages,fixtureCall(personal,new JSONObject().put("action","history").put("conversation_id","legacy-view-2")).getJSONArray("messages"));
        ConversationProof.sameSnapshot(personalBefore,U03Runtime.status(UiEvidence.app()).getJSONObject("snapshot"));
        record("C04_c18SparseViewsAndPendingRequestMigrate",new JSONObject().put("passed",true).put("actual_c18_schema",true)
            .put("empty_active_view_preserved",true).put("all_existing_views_visible",true).put("no_phantom_views",true)
            .put("legacy_complete_result_exact",true).put("pending_request_stays_in_origin_thread",true).put("pending_native_completion_is_idempotent",true)
            .put("active_conversation_unchanged",true).put("personal_model_unchanged",true).put("migrated",migrated).put("pending_before",pending)
            .put("pending_after",resumedHistory).put("native_completion",resumed));
    }
}
