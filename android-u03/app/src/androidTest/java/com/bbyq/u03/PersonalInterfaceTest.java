package com.bbyq.u03;

import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.Activity;
import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.Insets;
import android.graphics.Rect;
import android.os.Build;
import android.os.ParcelFileDescriptor;
import android.os.SystemClock;
import android.view.InputDevice;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.inputmethod.InputMethodManager;
import android.webkit.WebView;
import android.widget.EditText;
import android.widget.TextView;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.runner.lifecycle.ActivityLifecycleMonitorRegistry;
import androidx.test.runner.lifecycle.Stage;
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
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import static org.junit.Assert.*;

/** Real Android system bars, IME, touch navigation and durable native conversation. */
@RunWith(AndroidJUnit4.class)
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public final class PersonalInterfaceTest {
    private String oldFont,oldNavigation;
    @BeforeClass public static void initializeEvidence()throws Exception {
        UiEvidence.write("personal-interface-proof.json",new JSONObject()
            .put("schema","BBYQ-0-Android-interface-v1").put("android_api",Build.VERSION.SDK_INT)
            .put("cases",new JSONObject()));
        assertTrue("These regressions must run on Android 15 or newer",Build.VERSION.SDK_INT>=35);
        U03Runtime.start(UiEvidence.app());
    }
    @Before public void saveDeviceConfiguration()throws Exception {
        oldFont=UiEvidence.shell("settings get system font_scale").trim();
        oldNavigation=UiEvidence.shell("settings get secure navigation_mode").trim();
        UiEvidence.shell("settings put system font_scale 1.0");
        UiEvidence.finishActivities();
        assertTrue(UiEvidence.app().getSharedPreferences(UiKit.PREFS,Context.MODE_PRIVATE).edit()
            .remove("chat_draft").remove("chat_selection").putFloat("font_scale",1f).commit());
    }
    private void restoreDeviceConfiguration()throws Exception {
        UiEvidence.finishActivities();
        if(oldFont!=null&&!oldFont.equals("null")&&!oldFont.isEmpty())
            UiEvidence.shell("settings put system font_scale "+oldFont);
        else UiEvidence.shell("settings delete system font_scale");
        if("0".equals(oldNavigation))UiEvidence.navigation(false);
        else if("2".equals(oldNavigation))UiEvidence.navigation(true);
    }
    @Rule public final TestWatcher failureEvidence=new TestWatcher(){
        @Override protected void failed(Throwable error,Description description){
            try{
                String file="personal-failure-"+description.getMethodName()+".png";
                UiEvidence.screenshot(file);
                record(description.getMethodName(),new JSONObject().put("passed",false)
                    .put("error",error.toString()).put("screenshot",file));
            }catch(Exception ignored){}
        }
        @Override protected void finished(Description description){
            try{restoreDeviceConfiguration();}catch(Exception e){throw new AssertionError("Restore emulator configuration",e);}
        }
    };
    private static void record(String key,JSONObject value)throws Exception {
        JSONObject proof=UiEvidence.read("personal-interface-proof.json");
        proof.getJSONObject("cases").put(key,value);UiEvidence.write("personal-interface-proof.json",proof);
    }
    private JSONObject conversation(String action)throws Exception {
        return U03Runtime.operation(UiEvidence.app(),"conversation",new JSONObject().put("action",action)
            .put("request_id","ui-"+UUID.randomUUID()).toString());
    }
    private IntegratedActivity home()throws Exception {
        IntegratedActivity activity=UiEvidence.start(IntegratedActivity.class);
        UiEvidence.until("Home composer is laid out",15000,()->UiEvidence.ui(()->{
            View input=activity.findViewById(0x5802003),send=activity.findViewById(0x5802004);
            return input!=null&&send!=null&&input.getWidth()>0&&send.getHeight()>0;
        }));
        return activity;
    }
    private void navigationAndKeyboard(boolean gesture)throws Exception {
        String mode=gesture?"gesture":"threebutton";
        UiEvidence.navigation(gesture);conversation("clear_view");
        IntegratedActivity activity=home();
        JSONObject empty=UiEvidence.homeBounds(activity,false);
        UiEvidence.write("personal-bounds-"+mode+".json",empty);
        UiEvidence.screenshot(gesture?"personal-main-gesture.png":"personal-main-empty.png");
        UiEvidence.assertHomeSafe(empty);
        assertTrue("Navigation inset must be real",empty.getJSONObject("system_bars").getInt("bottom")>0);
        EditText input=UiEvidence.ui(()->activity.findViewById(0x5802003));
        UiEvidence.tap(input);
        UiEvidence.ui(()->{
            input.requestFocus();
            ((InputMethodManager)activity.getSystemService(Context.INPUT_METHOD_SERVICE))
                .showSoftInput(input,InputMethodManager.SHOW_IMPLICIT);
            return null;
        });
        UiEvidence.until("The real Android keyboard is visible",15000,()->UiEvidence.imeVisible(activity));
        UiEvidence.ui(()->{input.setText("calcula 7 + 3");return null;});
        UiEvidence.until("Sending is enabled",15000,()->UiEvidence.ui(()->activity.findViewById(0x5802004).isEnabled()));
        JSONObject keyboard=UiEvidence.homeBounds(activity,true);
        UiEvidence.write("personal-bounds-keyboard-"+mode+".json",keyboard);
        UiEvidence.screenshot("personal-main-keyboard-"+mode+".png");
        UiEvidence.assertHomeSafe(keyboard);
        assertTrue(keyboard.getBoolean("ime_visible"));
        assertTrue(keyboard.getJSONObject("ime").getInt("bottom")>keyboard.getJSONObject("system_bars").getInt("bottom"));
        JSONObject answer=sendPrepared(activity,"calcula 7 + 3");
        JSONObject result=UiEvidence.nativeResult(answer,"math");
        assertEquals(10,result.getInt("value"));
        record(gesture?"P02_gestureAndKeyboard":"P01_threeButtonAndKeyboard",new JSONObject()
            .put("passed",true).put("navigation_mode",mode).put("empty",empty).put("keyboard",keyboard)
            .put("touch_send_reached_native_math",true).put("assistant",answer));
    }
    @Test public void P01_threeButtonAndKeyboard()throws Exception {navigationAndKeyboard(false);}
    @Test public void P02_gestureAndKeyboard()throws Exception {navigationAndKeyboard(true);}
    @Test public void P03_landscapeLargeFontAndSideBars()throws Exception {
        UiEvidence.navigation(false);UiEvidence.shell("settings put system font_scale 2.0");
        IntegratedActivity first=home();
        UiEvidence.ui(()->{first.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);return null;});
        UiEvidence.until("Landscape configuration is applied",15000,()->{
            Activity a=UiEvidence.resumed(IntegratedActivity.class);
            return a!=null&&UiEvidence.ui(()->a.getResources().getConfiguration().orientation==Configuration.ORIENTATION_LANDSCAPE
                &&a.getResources().getConfiguration().fontScale>=1.9f);
        });
        IntegratedActivity activity=UiEvidence.resumed(IntegratedActivity.class);
        UiEvidence.ui(()->{((EditText)activity.findViewById(0x5802003)).setText("Mensaje con letra grande");return null;});
        JSONObject geometry=UiEvidence.homeBounds(activity,false);
        UiEvidence.write("personal-bounds-landscape-large-font.json",geometry);
        UiEvidence.screenshot("personal-main-landscape-large-font.png");
        UiEvidence.assertHomeSafe(geometry);
        assertTrue(geometry.getDouble("font_scale")>=1.9);
        JSONObject bars=geometry.getJSONObject("system_bars");
        assertTrue("Three-button landscape must exercise a side navigation bar",bars.getInt("left")>0||bars.getInt("right")>0);
        UiEvidence.ui(()->{
            UiEvidence.assertTextFits((TextView)activity.findViewById(0x5802004));
            UiEvidence.assertTextFits((TextView)activity.findViewById(0x5802003));return null;
        });
        record("P03_landscapeLargeFontAndSideBars",new JSONObject().put("passed",true).put("geometry",geometry));
    }
    private JSONObject send(IntegratedActivity activity,String text)throws Exception {
        UiEvidence.ui(()->{((EditText)activity.findViewById(0x5802003)).setText(text);return null;});
        UiEvidence.until("Send button is enabled",15000,()->UiEvidence.ui(()->activity.findViewById(0x5802004).isEnabled()));
        return sendPrepared(activity,text);
    }
    private JSONObject sendPrepared(IntegratedActivity activity,String text)throws Exception {
        int before=conversation("history").getJSONArray("messages").length();
        UiEvidence.assertHomeSafe(UiEvidence.homeBounds(activity,UiEvidence.imeVisible(activity)));
        UiEvidence.tap(UiEvidence.ui(()->activity.findViewById(0x5802004)));
        AtomicReference<JSONObject> answer=new AtomicReference<>();
        UiEvidence.until("Touch submission produces a durable assistant response",90000,()->{
            JSONArray messages=conversation("history").getJSONArray("messages");
            if(messages.length()<before+2)return false;
            for(int i=before;i<messages.length()-1;i++){
                JSONObject user=messages.getJSONObject(i),assistant=messages.getJSONObject(i+1);
                if("user".equals(user.optString("role"))&&text.equals(user.optString("text"))
                    &&"assistant".equals(assistant.optString("role"))){answer.set(assistant);return true;}
            }
            return false;
        });
        String reply=answer.get().getString("text");
        assertFalse(reply.isEmpty());
        UiEvidence.until("The persisted answer is rendered in the conversation",15000,()->UiEvidence.ui(()->
            UiEvidence.textTree(activity.findViewById(0x5802005)).contains(reply)));
        return answer.get();
    }
    @Test public void P04_nativeConversationHistoryAndRecreation()throws Exception {
        UiEvidence.navigation(false);conversation("clear_view");IntegratedActivity activity=home();
        JSONObject greeting=send(activity,"hola");
        assertEquals("Native greeting is displayed as generated",UiEvidence.nativeResult(greeting,"text").getString("text").trim(),greeting.getString("text"));
        assertEquals("native_reference",greeting.getJSONObject("provenance").getString("response_origin"));
        JSONObject math=send(activity,"calcula 7 + 3");assertEquals(10,UiEvidence.nativeResult(math,"math").getInt("value"));
        JSONObject fact=send(activity,"recuerda que Lira es robot");assertEquals(1,UiEvidence.nativeResult(fact,"put").getInt("status"));
        JSONObject taught=U03Runtime.status(UiEvidence.app()).getJSONObject("snapshot");
        JSONObject query=send(activity,"¿Lira es robot?");JSONObject proof=UiEvidence.nativeResult(query,"query");
        assertEquals(1,proof.getInt("status"));assertTrue(proof.getJSONArray("proof").length()>0);
        UiEvidence.hideKeyboard(activity);UiEvidence.screenshot("personal-main-chat.png");
        JSONObject why=send(activity,"¿Por qué?");assertEquals(1,UiEvidence.nativeResult(why,"query").getInt("status"));
        assertTrue("Explanation must retain actual proof",why.getJSONObject("provenance").getJSONArray("proof").length()>0);
        JSONObject unknown=send(activity,"zxqv 047 sin una petición definida");
        assertEquals("abstention",unknown.getJSONObject("provenance").getString("response_origin"));
        assertFalse(unknown.getJSONObject("provenance").getBoolean("personal_memory_written"));
        UiEvidence.sameSnapshot(taught,U03Runtime.status(UiEvidence.app()).getJSONObject("snapshot"));
        JSONArray original=conversation("history").getJSONArray("messages");assertEquals(12,original.length());
        JSONObject before=UiEvidence.homeBounds(activity,false);UiEvidence.assertHomeSafe(before);
        IntegratedActivity old=activity;UiEvidence.ui(()->{old.recreate();return null;});
        UiEvidence.until("A new Activity instance restores the conversation",15000,()->{
            Activity current=UiEvidence.resumed(IntegratedActivity.class);return current!=null&&current!=old;
        });
        IntegratedActivity recreated=UiEvidence.resumed(IntegratedActivity.class);
        UiEvidence.until("All persisted messages are rendered after recreation",15000,()->UiEvidence.ui(()->{
            String shown=UiEvidence.textTree(recreated.findViewById(0x5802005));
            for(int i=0;i<original.length();i++)if(!shown.contains(original.getJSONObject(i).getString("text")))return false;
            return true;
        }));
        assertEquals("Recreation neither duplicates nor deletes conversation",original.toString(),conversation("history").getJSONArray("messages").toString());
        JSONObject after=UiEvidence.homeBounds(recreated,false);UiEvidence.assertHomeSafe(after);
        UiEvidence.write("personal-bounds-conversation.json",after);
        record("P04_nativeConversationHistoryAndRecreation",new JSONObject().put("passed",true)
            .put("greeting",greeting).put("math",math).put("taught_fact",fact).put("query",query)
            .put("explanation",why).put("unknown",unknown).put("queries_and_unknown_did_not_train",true)
            .put("history_preserved_exactly",true).put("new_activity_instance",true).put("geometry",after));
    }
    @Test public void P05_modelTrainingAndIllustratedGuide()throws Exception {
        UiEvidence.navigation(false);IntegratedActivity home=home();
        UiEvidence.tap(UiEvidence.ui(()->home.findViewById(0x5802010)));
        ModelActivity model=UiEvidence.awaitActivity(ModelActivity.class);
        UiEvidence.until("The model hub has finished loading",15000,()->UiEvidence.ui(()->{
            String status=((TextView)model.findViewById(0x5804006)).getText().toString();
            return status.startsWith("Modelo inicial")||status.startsWith("En uso:");
        }));
        UiEvidence.screenshot("personal-model-hub.png");
        UiEvidence.ui(()->{View training=model.findViewById(0x5804001);
            training.requestRectangleOnScreen(new Rect(0,0,training.getWidth(),training.getHeight()),true);return null;});
        JSONObject hub=UiEvidence.bounds(model,new int[]{0x5804001,0x5804007},false);
        UiEvidence.write("personal-bounds-model-hub.json",hub);UiEvidence.screenshot("personal-model-hub-training.png");
        UiEvidence.assertSafe(hub);UiEvidence.tap(UiEvidence.ui(()->model.findViewById(0x5804001)));
        TrainingActivity training=UiEvidence.awaitActivity(TrainingActivity.class);
        JSONObject workspace=UiEvidence.bounds(training,new int[]{0x5803002,0x5803020,0x5803021,0x5803022,0x5803023},false);
        UiEvidence.write("personal-bounds-training.json",workspace);UiEvidence.screenshot("personal-training.png");
        UiEvidence.assertSafe(workspace);UiEvidence.tap(UiEvidence.ui(()->training.findViewById(0x5803002)));
        JSONObject guide=UiEvidence.scrollGuideToIllustration(training,"personal-guide-scrolled.png");
        UiEvidence.write("personal-bounds-guide.json",guide);
        UiEvidence.tap(UiEvidence.ui(()->training.guideRootForTests().findViewById(0x5803090)));
        UiEvidence.until("Guide closes back to the training workspace",10000,()->UiEvidence.ui(()->training.guideWebViewForTests()==null));
        record("P05_modelTrainingAndIllustratedGuide",new JSONObject().put("passed",true)
            .put("hub",hub).put("training",workspace).put("guide",guide).put("guide_return_button_worked",true));
    }
}

/** Shared instrumentation evidence helpers; all coordinates come from actual Android views. */
final class UiEvidence {
    private UiEvidence(){}
    interface MainValue<T>{T get()throws Exception;}
    interface Condition{boolean ready()throws Exception;}
    static Instrumentation instrument(){return InstrumentationRegistry.getInstrumentation();}
    static Context app(){return instrument().getTargetContext();}
    static <T>T ui(MainValue<T> action)throws Exception {
        AtomicReference<T> value=new AtomicReference<>();AtomicReference<Throwable> error=new AtomicReference<>();
        instrument().runOnMainSync(()->{try{value.set(action.get());}catch(Throwable e){error.set(e);}});
        if(error.get() instanceof AssertionError)throw (AssertionError)error.get();
        if(error.get() instanceof Exception)throw (Exception)error.get();
        if(error.get()!=null)throw new RuntimeException(error.get());return value.get();
    }
    static void until(String reason,long timeout,Condition condition)throws Exception {
        long end=SystemClock.elapsedRealtime()+timeout;
        do{if(condition.ready())return;SystemClock.sleep(100);}while(SystemClock.elapsedRealtime()<end);
        fail(reason+" (timeout "+timeout+" ms)");
    }
    static String shell(String command)throws Exception {
        try(ParcelFileDescriptor.AutoCloseInputStream in=new ParcelFileDescriptor.AutoCloseInputStream(instrument().getUiAutomation().executeShellCommand(command));
            ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buf=new byte[4096];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);
            return out.toString(StandardCharsets.UTF_8.name());
        }
    }
    static void navigation(boolean gesture)throws Exception {
        String overlay="com.android.internal.systemui.navbar."+(gesture?"gestural":"threebutton");
        String result=shell("cmd overlay enable-exclusive --category "+overlay);
        assertFalse("Navigation overlay failed: "+result,result.contains("Error")||result.contains("Exception"));
        until("Real system navigation mode changes",10000,()->shell("settings get secure navigation_mode").trim().equals(gesture?"2":"0"));
    }
    static <T extends Activity>T resumed(Class<T> type)throws Exception {
        return ui(()->{for(Activity a:ActivityLifecycleMonitorRegistry.getInstance().getActivitiesInStage(Stage.RESUMED))
            if(type.isInstance(a))return type.cast(a);return null;});
    }
    static <T extends Activity>T awaitActivity(Class<T> type)throws Exception {
        until(type.getSimpleName()+" is resumed",15000,()->resumed(type)!=null);
        T activity=resumed(type);until("Window has insets and a measured layout",10000,()->ui(()->{
            View decor=activity.getWindow().getDecorView();return decor.getWidth()>0&&decor.getRootWindowInsets()!=null;
        }));instrument().waitForIdleSync();return activity;
    }
    static <T extends Activity>T start(Class<T> type)throws Exception {
        instrument().startActivitySync(new Intent(app(),type).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK|Intent.FLAG_ACTIVITY_CLEAR_TASK));
        return awaitActivity(type);
    }
    static void finishActivities()throws Exception {
        ui(()->{
            for(Stage stage:new Stage[]{Stage.RESUMED,Stage.PAUSED,Stage.STARTED,Stage.STOPPED,Stage.CREATED}){
                Collection<Activity> activities=new ArrayList<>(ActivityLifecycleMonitorRegistry.getInstance().getActivitiesInStage(stage));
                for(Activity activity:activities)if(activity.getPackageName().equals(app().getPackageName()))activity.finish();
            }
            return null;
        });instrument().waitForIdleSync();
    }
    static JSONObject rect(Rect r)throws Exception{return new JSONObject().put("left",r.left).put("top",r.top).put("right",r.right).put("bottom",r.bottom).put("width",r.width()).put("height",r.height());}
    static Rect rect(JSONObject r)throws Exception{return new Rect(r.getInt("left"),r.getInt("top"),r.getInt("right"),r.getInt("bottom"));}
    static JSONObject inset(Insets i)throws Exception{return new JSONObject().put("left",i.left).put("top",i.top).put("right",i.right).put("bottom",i.bottom);}
    static Rect screenRect(View view){int[] p=new int[2];view.getLocationOnScreen(p);return new Rect(p[0],p[1],p[0]+view.getWidth(),p[1]+view.getHeight());}
    static boolean imeVisible(Activity activity)throws Exception{return ui(()->{
        WindowInsets insets=activity.getWindow().getDecorView().getRootWindowInsets();return insets!=null&&insets.isVisible(WindowInsets.Type.ime());
    });}
    static void hideKeyboard(Activity activity)throws Exception {
        ui(()->{activity.getWindow().getInsetsController().hide(WindowInsets.Type.ime());return null;});
        until("Keyboard is hidden",10000,()->!imeVisible(activity));instrument().waitForIdleSync();
    }
    static JSONObject homeBounds(Activity activity,boolean ime)throws Exception{return bounds(activity,new int[]{0x5802003,0x5802004,0x5802007},ime);}
    static JSONObject bounds(Activity activity,int[] ids,boolean ime)throws Exception {
        instrument().waitForIdleSync();return ui(()->{
            View decor=activity.getWindow().getDecorView();WindowInsets insets=decor.getRootWindowInsets();assertNotNull(insets);
            Insets bars=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
            Insets keyboard=insets.getInsets(WindowInsets.Type.ime());
            Rect window=new Rect(activity.getWindowManager().getMaximumWindowMetrics().getBounds());
            Rect safe=new Rect(window.left+Math.max(bars.left,ime?keyboard.left:0),window.top+Math.max(bars.top,ime?keyboard.top:0),
                window.right-Math.max(bars.right,ime?keyboard.right:0),window.bottom-Math.max(bars.bottom,ime?keyboard.bottom:0));
            JSONObject views=new JSONObject();
            for(int id:ids){View view=activity.findViewById(id);assertNotNull("Missing view "+Integer.toHexString(id),view);
                Rect visible=new Rect();boolean hasVisible=view.getGlobalVisibleRect(visible);
                views.put(Integer.toHexString(id),new JSONObject().put("rect",rect(screenRect(view))).put("visible_rect",rect(visible))
                    .put("shown",view.isShown()&&hasVisible).put("enabled",view.isEnabled()));}
            return new JSONObject().put("android_api",Build.VERSION.SDK_INT).put("window",rect(window)).put("safe",rect(safe))
                .put("system_bars",inset(bars)).put("ime",inset(keyboard)).put("ime_visible",insets.isVisible(WindowInsets.Type.ime()))
                .put("font_scale",activity.getResources().getConfiguration().fontScale).put("views",views);
        });
    }
    static void assertSafe(JSONObject geometry)throws Exception {
        Rect safe=rect(geometry.getJSONObject("safe"));JSONObject views=geometry.getJSONObject("views");
        for(java.util.Iterator<String> it=views.keys();it.hasNext();){String id=it.next();JSONObject v=views.getJSONObject(id);
            Rect box=rect(v.getJSONObject("rect")),visible=rect(v.getJSONObject("visible_rect"));
            assertTrue("Control "+id+" is not visible: "+geometry,v.getBoolean("shown")&&box.width()>0&&box.height()>0);
            assertTrue("Control "+id+" overlaps bars/keyboard: "+geometry,safe.contains(box));
            assertEquals("Control "+id+" is clipped",box,visible);
        }
    }
    static void assertHomeSafe(JSONObject geometry)throws Exception {assertSafe(geometry);}
    static void assertTextFits(TextView view){
        if(view.getText().length()==0)return; // The send button uses a drawable with an accessibility label.
        assertNotNull("Text has a real layout",view.getLayout());
        assertTrue("Large text is clipped vertically",view.getLayout().getHeight()<=view.getHeight()-view.getCompoundPaddingTop()-view.getCompoundPaddingBottom()+1);
    }
    static void tap(View view)throws Exception {
        assertNotNull(view);Rect r=ui(()->screenRect(view));assertTrue(r.width()>0&&r.height()>0);
        tap(r);
    }
    static void tap(Rect r)throws Exception {
        long time=SystemClock.uptimeMillis();MotionEvent down=MotionEvent.obtain(time,time,MotionEvent.ACTION_DOWN,r.exactCenterX(),r.exactCenterY(),0);
        MotionEvent up=MotionEvent.obtain(time,time+80,MotionEvent.ACTION_UP,r.exactCenterX(),r.exactCenterY(),0);
        down.setSource(InputDevice.SOURCE_TOUCHSCREEN);up.setSource(InputDevice.SOURCE_TOUCHSCREEN);
        try{instrument().sendPointerSync(down);SystemClock.sleep(80);instrument().sendPointerSync(up);}finally{down.recycle();up.recycle();}
        instrument().waitForIdleSync();
    }
    static void swipe(View view,float fraction)throws Exception {
        swipe(ui(()->screenRect(view)),fraction);
    }
    private static void swipe(Rect r,float fraction)throws Exception {
        float x=r.exactCenterX(),start=r.top+r.height()*0.78f,end=start-r.height()*fraction;
        long begin=SystemClock.uptimeMillis();
        for(int i=0;i<=40;i++){
            int action=i==0?MotionEvent.ACTION_DOWN:i==40?MotionEvent.ACTION_UP:MotionEvent.ACTION_MOVE;
            MotionEvent e=MotionEvent.obtain(begin,SystemClock.uptimeMillis(),action,x,start+(end-start)*i/40f,0);e.setSource(InputDevice.SOURCE_TOUCHSCREEN);
            try{instrument().sendPointerSync(e);}finally{e.recycle();}SystemClock.sleep(15);
        }
        instrument().waitForIdleSync();SystemClock.sleep(150);
    }
    private static Rect accessibleTarget(AccessibilityNodeInfo node,String value,boolean byClass){
        if(node==null)return null;
        boolean matches=byClass?String.valueOf(node.getClassName()).contains(value):
            value.contentEquals(node.getText()==null?"":node.getText())||value.contentEquals(node.getContentDescription()==null?"":node.getContentDescription());
        if(matches&&node.isVisibleToUser()&&node.isEnabled()){Rect r=new Rect();node.getBoundsInScreen(r);if(r.width()>0&&r.height()>0)return r;}
        for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);
            if(child!=null){Rect found=accessibleTarget(child,value,byClass);child.recycle();if(found!=null)return found;}}
        return null;
    }
    static void tapText(String value)throws Exception {
        for(int attempt=0;attempt<12;attempt++){
            AccessibilityNodeInfo root=instrument().getUiAutomation().getRootInActiveWindow();Rect target=null,window=new Rect();
            if(root!=null){target=accessibleTarget(root,value,false);root.getBoundsInScreen(window);root.recycle();}
            if(target!=null){tap(target);return;}
            if(attempt>0&&window.height()>0)swipe(window,0.35f);else SystemClock.sleep(200);
        }
        fail("Reachable control not found: "+value);
    }
    static void assertAccessibleClass(String name)throws Exception {
        until("Visible advanced control "+name,10000,()->{
            AccessibilityNodeInfo root=instrument().getUiAutomation().getRootInActiveWindow();
            if(root==null)return false;Rect found=accessibleTarget(root,name,true);root.recycle();return found!=null;
        });
    }
    private static JSONObject accessibleJson(AccessibilityNodeInfo node,String requiredKey){
        if(node==null)return null;
        if(node.isVisibleToUser()&&node.getText()!=null){
            try{JSONObject value=new JSONObject(node.getText().toString());if(value.has(requiredKey))return value;}catch(Exception ignored){}
        }
        for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);
            if(child!=null){JSONObject found=accessibleJson(child,requiredKey);child.recycle();if(found!=null)return found;}}
        return null;
    }
    static JSONObject displayedReport(String requiredKey)throws Exception {
        AtomicReference<JSONObject> result=new AtomicReference<>();
        until("The actual operation report is displayed",20000,()->{
            AccessibilityNodeInfo root=instrument().getUiAutomation().getRootInActiveWindow();
            if(root==null)return false;JSONObject found=accessibleJson(root,requiredKey);root.recycle();result.set(found);return found!=null;
        });return result.get();
    }
    static String textTree(View view){
        if(view==null)return "";StringBuilder text=new StringBuilder();
        if(view instanceof TextView)text.append(((TextView)view).getText()).append('\n');
        if(view instanceof ViewGroup){ViewGroup group=(ViewGroup)view;for(int i=0;i<group.getChildCount();i++)text.append(textTree(group.getChildAt(i)));}
        return text.toString();
    }
    static JSONObject nativeResult(JSONObject message,String kind)throws Exception {
        JSONObject provenance=message.getJSONObject("provenance");assertTrue(provenance.toString(),provenance.getBoolean("native_XI"));
        JSONObject receipt=provenance.getJSONObject("receipt");JSONArray trace=receipt.getJSONArray("trace");boolean nativeCall=false;
        for(int i=0;i<trace.length();i++)if(trace.getJSONObject(i).optBoolean("native"))nativeCall=true;
        assertTrue("Conversation must execute the original XI",nativeCall);
        JSONArray results=receipt.getJSONArray("results");for(int i=0;i<results.length();i++)if(kind.equals(results.getJSONObject(i).optString("kind")))return results.getJSONObject(i);
        throw new AssertionError("Missing native "+kind+" result: "+receipt);
    }
    static void sameSnapshot(JSONObject before,JSONObject after)throws Exception {
        for(String key:new String[]{"revision","metadata_sha256","tasks","feedback"})assertEquals(key,before.get(key),after.get(key));
        JSONObject banks=before.getJSONObject("banks");assertEquals(7,banks.length());assertEquals(7,after.getJSONObject("banks").length());
        for(java.util.Iterator<String> names=banks.keys();names.hasNext();){String name=names.next();assertEquals(name,banks.getString(name),after.getJSONObject("banks").getString(name));}
    }
    static void visualReady(WebView web)throws Exception {
        CountDownLatch rendered=new CountDownLatch(1);ui(()->{web.postVisualStateCallback(SystemClock.uptimeMillis(),new WebView.VisualStateCallback(){
            @Override public void onComplete(long requestId){web.postOnAnimation(rendered::countDown);}});return null;});
        assertTrue("WebView commits a real visual frame",rendered.await(10,TimeUnit.SECONDS));instrument().waitForIdleSync();
    }
    private static JSONObject visibleDiagram(AccessibilityNodeInfo node,Rect viewport)throws Exception {
        if(node==null)return null;
        String label=String.valueOf(node.getContentDescription())+" "+String.valueOf(node.getText());
        String type=String.valueOf(node.getClassName());Rect bounds=new Rect();node.getBoundsInScreen(bounds);
        boolean titled=label.contains("Del estado actual a una sesión")||label.contains("Nara, robot y máquina")
            ||label.contains("Diferencia entre enseñar")||label.contains("Predicción, respuesta correcta")
            ||label.contains("Comparar el estado inicial")||label.contains("Qué viaja en tu archivo");
        if(titled&&type.contains("Image")&&node.isVisibleToUser()&&bounds.width()>viewport.width()/2&&bounds.height()>80&&viewport.contains(bounds))
            return new JSONObject().put("label",label).put("class",type).put("bounds",rect(bounds));
        for(int i=0;i<node.getChildCount();i++){AccessibilityNodeInfo child=node.getChild(i);
            if(child!=null){JSONObject found=visibleDiagram(child,viewport);child.recycle();if(found!=null)return found;}}
        return null;
    }
    static JSONObject scrollGuideToIllustration(TrainingActivity activity,String screenshot)throws Exception {
        until("Actual guide WebView is available",10000,()->ui(()->activity.guideWebViewForTests()!=null));
        WebView web=ui(activity::guideWebViewForTests);
        until("Offline document has loaded beyond its cover",15000,()->ui(()->web.getContentHeight()*web.getScale()>web.getHeight()*2));
        visualReady(web);int before=ui(web::getScrollY);Rect viewport=ui(()->screenRect(web));
        AccessibilityServiceInfo info=instrument().getUiAutomation().getServiceInfo();
        info.flags|=AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS|AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS;
        instrument().getUiAutomation().setServiceInfo(info);
        JSONObject diagram=null;JSONArray offsets=new JSONArray();
        for(int step=0;step<18&&diagram==null;step++){
            swipe(web,0.24f);visualReady(web);int offset=ui(web::getScrollY);offsets.put(offset);
            AccessibilityNodeInfo root=instrument().getUiAutomation().getRootInActiveWindow();
            if(root!=null){diagram=visibleDiagram(root,viewport);root.recycle();}
        }
        int after=ui(web::getScrollY);screenshot(screenshot);
        JSONObject report=new JSONObject().put("viewport",rect(viewport)).put("scroll_y_before",before).put("scroll_y_after",after)
            .put("touch_scroll_offsets",offsets).put("screenshot",screenshot).put("visible_svg",diagram==null?JSONObject.NULL:diagram);
        write(screenshot.replace(".png","-scroll.json"),report);
        assertTrue("Touch gestures must scroll the real guide beyond the cover: "+report,after-before>viewport.height());
        assertNotNull("A labelled SVG image must actually be fully visible inside the WebView: "+report,diagram);
        assertFalse("Guide remains offline and does not enable scripting",ui(()->web.getSettings().getJavaScriptEnabled()));
        return report;
    }
    static void screenshot(String filename)throws Exception {
        Bitmap image=instrument().getUiAutomation().takeScreenshot();assertNotNull("Screen capture",image);
        try(FileOutputStream out=new FileOutputStream(new File(app().getFilesDir(),filename))){assertTrue(image.compress(Bitmap.CompressFormat.PNG,100,out));}
        finally{image.recycle();}
    }
    static void write(String filename,JSONObject value)throws Exception {
        try(FileOutputStream out=new FileOutputStream(new File(app().getFilesDir(),filename))){out.write(value.toString(2).getBytes(StandardCharsets.UTF_8));}
    }
    static JSONObject read(String filename)throws Exception {
        try(FileInputStream in=new FileInputStream(new File(app().getFilesDir(),filename));ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1)out.write(b,0,n);return new JSONObject(out.toString(StandardCharsets.UTF_8.name()));
        }
    }
}
