package com.bbyq.u03;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import android.content.Context;
import org.json.JSONObject;
import org.json.JSONArray;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;
import java.util.UUID;

/** Android 15 instrumentation must execute ORIGINAL U02 via native XI JNI. */
@RunWith(AndroidJUnit4.class)
public class U03NativeTest {
    private Context app(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private String id(String name){return "u03-android-"+name+"-"+UUID.randomUUID().toString();}
    @Test public void authenticU02StartupAndSevenSHAAuthenticatedBanks() throws Exception {
        JSONObject s=U03Runtime.start(app());
        assertEquals("U02",s.getString("entity"));
        assertEquals(7,s.getInt("banks"));
        assertEquals(159,s.getInt("historical_assets"));
        assertTrue(s.getBoolean("checkpoint_identity_verified"));
        assertTrue(s.getBoolean("C1_U02_synchronized"));
        assertFalse(s.getBoolean("model_promoted"));
        assertFalse(s.getBoolean("gpu_C12_ported"));
    }
    @Test public void originalC1CalculationAndIdempotentReceipt() throws Exception {
        U03Runtime.start(app());
        String request=id("math");
        JSONObject first=U03Runtime.turn(app(),request,"calcula 7 + 3","");
        assertTrue(first.toString(),first.getBoolean("ok"));
        assertTrue(first.toString(),first.getBoolean("native_XI"));
        assertTrue(first.toString(),first.getBoolean("original_U02"));
        assertTrue(first.toString(),first.getString("reply").contains("10"));
        JSONObject second=U03Runtime.turn(app(),request,"calcula 7 + 3","");
        // A replay may reorder JSON object keys because SQLite stores
        // canonical JSON. Compare SHA-256 over the entire original receipt
        // including trace and outputs, not JSONObject.toString() ordering.
        assertEquals(64,first.getString("receipt_sha256").length());
        assertEquals(first.getString("receipt_sha256"),
                     second.getString("receipt_sha256"));
        assertEquals(first.getLong("after_revision"),second.getLong("after_revision"));
    }
    @Test public void sixEnginesOriginalU02NativeMission() throws Exception {
        U03Runtime.start(app());
        JSONObject result=U03Runtime.turn(app(),id("mission"),
            "guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3","");
        assertTrue(result.toString(),result.getBoolean("ok"));
        assertTrue(result.toString(),result.getBoolean("native_XI"));
        JSONArray trace=result.getJSONArray("trace");
        boolean c1=false,qmem=false,vqc=false,qrl=false,entity=false,qchat=false;
        for(int i=0;i<trace.length();i++){
            JSONObject row=trace.getJSONObject(i);
            String op=row.optString("operation");
            String bank=row.optString("bank");
            c1 |= op.contains("c1_");
            qmem |= bank.equals("memory");
            vqc |= bank.equals("v3");
            qrl |= op.contains("qrl") || op.contains("policy");
            entity |= bank.equals("entity");
            qchat |= bank.equals("voice");
        }
        assertTrue("missing C1",c1);
        assertTrue("missing QMemory",qmem);
        assertTrue("missing VQC",vqc);
        assertTrue("missing QRL",qrl);
        assertTrue("missing Entity",entity);
        assertTrue("missing QChat",qchat);
        JSONObject state=U03Runtime.status(app());
        assertEquals(7,state.getInt("bank_count"));
        assertTrue(state.getJSONObject("memory").getBoolean("C1_synchronized_with_U02"));
    }
    @Test public void cyclesAndNoSilentPromotion() throws Exception {
        String p=U03Runtime.panel(app());
        for(int i=0;i<=15;i++)assertTrue(p,String.format("C%02d",i).length()>0 &&
            p.contains(String.format("C%02d",i)));
        JSONObject s=U03Runtime.status(app());
        assertTrue(s.getBoolean("C11_C12_unpromoted"));
        assertTrue(s.getBoolean("C13_cache_disabled"));
    }
}
