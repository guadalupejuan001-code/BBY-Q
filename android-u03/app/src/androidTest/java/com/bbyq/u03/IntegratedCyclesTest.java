package com.bbyq.u03;

import android.content.Context;
import android.content.Intent;
import android.app.Activity;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.json.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.*;
import java.util.UUID;

/** Must run actual original XI inference/training and Android WAL, not mocks. */
@RunWith(AndroidJUnit4.class)
public final class IntegratedCyclesTest {
    private static final String MISSION="guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3";
    private Context app(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
    private String id(){return "c16-"+UUID.randomUUID();}
    private JSONObject op(String name)throws Exception{return U03Runtime.operation(app(),name,"{}");}
    private JSONObject snapshot()throws Exception{return U03Runtime.status(app()).getJSONObject("snapshot");}
    private void unchanged(JSONObject before)throws Exception{
        JSONObject after=snapshot();
        assertEquals(before.getLong("revision"),after.getLong("revision"));
        assertEquals(before.getString("metadata_sha256"),after.getString("metadata_sha256"));
        assertEquals(before.getInt("tasks"),after.getInt("tasks"));
        JSONObject banks=before.getJSONObject("banks");
        java.util.Iterator<String> keys=banks.keys();
        while(keys.hasNext()){String k=keys.next();assertEquals(banks.getString(k),after.getJSONObject("banks").getString(k));}
    }
    @Test public void M01_loaderAndAllProtectedHeadsAreReal()throws Exception{
        JSONObject start=U03Runtime.start(app());
        assertEquals(7,start.getInt("banks"));assertEquals(159,start.getInt("historical_assets"));
        JSONObject heads=start.getJSONObject("recovered_original_heads");
        assertEquals("ed0f0067e43fcab74ba81c574bca983d8a497322ae5d7e8218f7a2941aa53018",heads.getString("c06"));
        assertEquals("fd0d68731996771adcfc1bf8bd2a6f634d96dcc042fdb87efbb97103b0e59ecb",heads.getString("c07"));
        assertEquals("0bb44c4d3da0797934abf1fe51d76354ed54d7f470cb1897c5bae48c8c432448",heads.getString("c08"));
        JSONObject diag=U03Runtime.diagnostics(app());
        assertTrue(diag.getJSONArray("abis").length()>0);
        assertTrue(diag.getLong("page_size")>=4096);
        assertTrue(diag.getJSONArray("packaged_libraries").toString().contains("libreverse_os.so"));
        assertEquals("",diag.getString("last_error"));
    }
    @Test public void M02_liveTurnUsesC03C04C05C06C09()throws Exception{
        JSONObject r=U03Runtime.turn(app(),id(),"calcula 7 + 3","");
        assertTrue(r.toString(),r.getBoolean("ok"));
        assertTrue(r.getBoolean("native_XI"));assertTrue(r.has("C03"));assertTrue(r.has("C04"));
        assertEquals(64,r.getJSONObject("C05").getString("wire_sha256").length());
        assertTrue(r.getJSONObject("C06").toString(),r.getJSONObject("C06").getBoolean("native_XI"));
        assertTrue(r.getJSONObject("C09").getBoolean("read_only"));
        assertEquals(0,r.getJSONObject("C09").getInt("new_memory_authorities"));
        assertTrue(r.getJSONObject("C00").getInt("native_packets")>0);
        JSONObject memory=op("memory");assertEquals(7,memory.getJSONObject("bank_sha256").length());
    }
    @Test public void M02_C10ActualNativePlanAndProofWithoutPersonalWrites()throws Exception{
        assertTrue(U03Runtime.turn(app(),id(),MISSION,"").getBoolean("ok"));
        assertTrue(U03Runtime.turn(app(),id(),"si alguien es clase cero entonces es alerta","").getBoolean("ok"));
        JSONObject before=snapshot();
        JSONObject p=U03Runtime.operation(app(),"plan","{\"observation\":\"Nara\",\"association\":\"Faro Azul\",\"position\":3}");
        assertEquals(p.toString(),"native_plan",p.getString("status"));
        assertTrue(p.getBoolean("native_goal_executed_in_disposable_copy"));
        assertEquals(0,p.getInt("original_database_writes"));
        JSONObject proof=U03Runtime.operation(app(),"prove","{\"observation\":\"Nara\"}");
        assertEquals(proof.toString(),"native_proof",proof.getString("status"));
        assertTrue(proof.getJSONObject("native").getJSONArray("symbolic_proof_ids").length()>0);
        unchanged(before);
    }
    @Test public void M03_recoveredC06C07C08ActuallyPredict()throws Exception{
        JSONObject before=snapshot();
        JSONObject sem=U03Runtime.operation(app(),"semantic","{\"text\":\"define Prisma no Brisa\"}");
        assertTrue(sem.getBoolean("native_XI"));assertFalse(sem.getBoolean("overrides_C1"));
        JSONObject e=U03Runtime.operation(app(),"evidence","{\"query\":{\"subject\":\"Movil\",\"predicate\":\"operativo\"},\"evidence\":[]}");
        assertEquals("evaluated",e.getString("status"));
        for(String c:new String[]{"C07","C08"}){
            JSONObject h=e.getJSONObject("assessments").getJSONObject(c);
            assertTrue(h.getBoolean("native_XI"));assertEquals("ask_for_evidence",h.getString("recommended_action"));
            assertFalse(h.getBoolean("model_promoted"));
        }
        assertTrue(e.getJSONObject("assessments").getJSONObject("C08").getString("clarification").length()>20);
        unchanged(before);
    }
    @Test public void M04_C11RunsNativeFeedbackAndAuditsAllWeights()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("c11");
        assertTrue(r.getBoolean("passed"));assertEquals(6,r.getInt("changed_regions"));
        assertTrue(r.getBoolean("labels_revealed_after_inference"));assertFalse(r.getBoolean("model_promoted"));
        assertEquals(4,r.getJSONObject("evaluation").getJSONObject("frozen").getInt("total"));
        assertEquals(4,r.getJSONObject("evaluation").getJSONObject("joint-verified").getInt("total"));
        unchanged(before);
    }
    @Test public void M04_C12RunsNativeCrossBlockTrainingAndSavedCandidate()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("c12");
        assertTrue(r.getBoolean("passed"));assertEquals(6,r.getInt("changed_regions"));
        assertEquals(6,r.getJSONObject("evaluation").getJSONObject("joint-verified").getInt("total"));
        assertFalse(r.getBoolean("model_promoted"));
        JSONObject test=U03Runtime.operation(app(),"candidate","{\"cycle\":\"c12\",\"text\":\"calcula 7 + 3\"}");
        assertTrue(test.getBoolean("native_XI_executed"));assertTrue(test.getBoolean("tested_in_disposable_copy"));
        assertFalse(test.getBoolean("candidate_modified"));unchanged(before);
    }
    @Test public void M05_C01ActualTransportParity()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("transport");
        assertTrue(r.getBoolean("passed"));assertEquals(2,r.getJSONArray("trials").length());
        assertFalse(r.getBoolean("inference_results_cached"));unchanged(before);
    }
    @Test public void M05_C02ActualOptimisticPersistenceParity()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("persistence");
        assertTrue(r.getBoolean("passed"));assertEquals(2,r.getJSONArray("trials").length());
        assertFalse(r.getBoolean("default_persistence_replaced"));unchanged(before);
    }
    @Test public void M05_C13ActualScopedCacheWithBothArms()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("cache");
        assertTrue(r.getBoolean("passed"));assertFalse(r.getBoolean("cache_enabled_globally"));
        for(String arm:new String[]{"frozen","c12-unpromoted"})assertEquals(6,r.getJSONObject("arms").getJSONObject(arm).getInt("pairs"));
        unchanged(before);
    }
    @Test public void M05_C14ActualDisjointJniPacketsAndAblations()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("profile");
        assertTrue(r.getBoolean("passed"));assertTrue(r.getInt("packets")>0);
        assertEquals(5,r.getJSONArray("ablations").length());
        assertTrue(r.isNull("exclusive_native_gate_cpu_ms"));
        assertFalse(r.getBoolean("hardware_GPU_used"));unchanged(before);
    }
    @Test public void M05_C15RealAndroidWalRollbackReplayAndReopen()throws Exception{
        JSONObject before=snapshot();JSONObject r=op("stress");assertTrue(r.getBoolean("passed"));
        for(String arm:new String[]{"frozen","c12-unpromoted"}){
            JSONObject a=r.getJSONObject("arms").getJSONObject(arm);
            assertEquals(2,a.getInt("committed"));assertTrue(a.getBoolean("exact_replay"));
            assertEquals(3,a.getJSONArray("rollback_cutpoints").length());assertTrue(a.getBoolean("reopen_exact"));
            assertTrue(a.getBoolean("different_payload_rejected"));
            for(int i=0;i<a.getJSONArray("readers").length();i++)assertTrue(a.getJSONArray("readers").getJSONObject(i).getBoolean("postcommit_verified"));
        }
        unchanged(before);
    }
    /** BBY Q 0 moves the original operation picker into Mi BBY Q / Avanzado. */
    @Test public void M06IntegratedLauncherExposesActualCycleActions()throws Exception{
        IntegratedActivity a=UiEvidence.start(IntegratedActivity.class);
        try{
            assertNotNull(a.findViewById(0x5802003));assertNotNull(a.findViewById(0x5802004));
            UiEvidence.tap(UiEvidence.ui(()->a.findViewById(0x5802010)));
            ModelActivity model=UiEvidence.awaitActivity(ModelActivity.class);
            UiEvidence.until("Personal model has loaded",15000,()->UiEvidence.ui(()->{
                String status=((android.widget.TextView)model.findViewById(0x5804006)).getText().toString();
                return status.startsWith("Modelo inicial")||status.startsWith("En uso:");
            }));
            UiEvidence.ui(()->{
                android.view.View advanced=model.findViewById(0x5804005);assertNotNull(advanced);
                advanced.requestRectangleOnScreen(new android.graphics.Rect(0,0,advanced.getWidth(),advanced.getHeight()),true);return null;
            });
            UiEvidence.tap(UiEvidence.ui(()->model.findViewById(0x5804005)));
            UiEvidence.tapText("Laboratorios y operaciones");
            UiEvidence.assertAccessibleClass("Spinner");
            UiEvidence.tapText("Ejecutar operación");
            JSONObject displayed=UiEvidence.displayedReport("bank_sha256");
            assertEquals(7,displayed.getJSONObject("bank_sha256").length());
            assertTrue(displayed.getBoolean("C1_synchronized_with_U02"));
            JSONObject cap=op("capabilities");assertTrue(cap.getJSONObject("interactive").has("C10"));
            assertTrue(cap.getJSONObject("laboratory").has("C15"));
        }finally{UiEvidence.finishActivities();}
    }
}

