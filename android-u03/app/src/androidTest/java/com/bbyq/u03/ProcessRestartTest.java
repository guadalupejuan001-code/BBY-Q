package com.bbyq.u03;

import android.content.Context;
import android.content.SharedPreferences;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;

/** Run twice by CI, with adb force-stop separating real Android processes. */
@RunWith(AndroidJUnit4.class)
public final class ProcessRestartTest {
    @Test public void receiptSurvivesExternalProcessRestart()throws Exception{
        Context app=InstrumentationRegistry.getInstrumentation().getTargetContext();
        String phase=InstrumentationRegistry.getArguments().getString("persistence_phase","");
        SharedPreferences evidence=app.getSharedPreferences("c16-ci-restart",Context.MODE_PRIVATE);
        String id="c16-process-restart-original-native",prompt="calcula 13 + 7";
        U03Runtime.start(app);
        if(phase.equals("seed")){
            JSONObject r=U03Runtime.turn(app,id,prompt,"");assertTrue(r.toString(),r.getBoolean("ok"));
            assertTrue(r.getString("reply").contains("20"));
            assertTrue(evidence.edit().putString("receipt",r.getString("receipt_sha256"))
                .putLong("revision",r.getLong("after_revision")).putInt("pid",android.os.Process.myPid()).commit());
        }else if(phase.equals("verify")){
            assertTrue(evidence.contains("receipt"));
            assertNotEquals("CI must restart a real Android process",evidence.getInt("pid",-1),android.os.Process.myPid());
            JSONObject before=U03Runtime.status(app).getJSONObject("snapshot");
            assertEquals(evidence.getLong("revision",-1),before.getLong("revision"));
            JSONObject r=U03Runtime.turn(app,id,prompt,"");
            assertEquals(evidence.getString("receipt",null),r.getString("receipt_sha256"));
            assertEquals(before.getLong("revision"),r.getLong("after_revision"));
            assertTrue(U03Runtime.status(app).getJSONObject("memory").getBoolean("C1_synchronized_with_U02"));
        }else fail("Explicit seed/verify phase required; this is not a simulated restart");
    }
}
