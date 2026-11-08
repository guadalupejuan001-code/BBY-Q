package com.bbyq.u03;
import android.content.Context;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.json.JSONObject;
import java.io.File;
import java.nio.file.Files;
import java.nio.charset.StandardCharsets;
import static org.junit.Assert.*;
/** Run in a NEW process after am force-stop, not merely Session.close. */
@RunWith(AndroidJUnit4.class)
public class U03RestartTest {
 @Test public void originalReceiptAndSevenBanksSurviveProcessRestart()throws Exception{
  Context app=InstrumentationRegistry.getInstrumentation().getTargetContext();
  File file=new File(app.getFilesDir(),"restart-test.json");assertTrue("Previous test must have committed its fixture",file.isFile());
  JSONObject previous=new JSONObject(new String(Files.readAllBytes(file.toPath()),StandardCharsets.UTF_8));
  JSONObject state=U03Runtime.status(app);assertEquals(7,state.getInt("bank_count"));
  assertEquals(previous.getString("snapshot_canonical"),U03NativeTest.canonical(state.getJSONObject("snapshot")));
  JSONObject replay=U03Runtime.turn(app,previous.getString("request_id"),previous.getString("prompt"),"");
  assertEquals(previous.getString("receipt_sha256"),replay.getString("receipt_sha256"));
  assertEquals(previous.getString("snapshot_canonical"),U03NativeTest.canonical(U03Runtime.status(app).getJSONObject("snapshot")));
  Files.write(new File(app.getFilesDir(),"test-evidence/restart-after.json").toPath(),new JSONObject().put("passed",true).put("receipt_sha256",replay.getString("receipt_sha256")).put("new_process",true).toString().getBytes(StandardCharsets.UTF_8));
 }
}
