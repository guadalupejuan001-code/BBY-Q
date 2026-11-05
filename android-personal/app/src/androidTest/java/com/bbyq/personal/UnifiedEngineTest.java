package com.bbyq.personal;

import android.content.*;
import android.database.sqlite.SQLiteDatabase;
import android.util.AtomicFile;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.*;
import org.junit.runner.RunWith;
import org.json.*;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.zip.GZIPInputStream;
import static org.junit.Assert.*;

@RunWith(AndroidJUnit4.class)
public class UnifiedEngineTest {
    private Context context;
    @Before public void fresh()throws Exception {
        Context base=InstrumentationRegistry.getInstrumentation().getTargetContext();
        File root=new File(base.getCacheDir(),"unified-"+System.nanoTime());assertTrue(root.mkdirs());
        context=new ContextWrapper(base){@Override public File getFilesDir(){return root;}};
    }
    private static byte[] bytes(InputStream in)throws Exception {
        try(InputStream source=in;ByteArrayOutputStream b=new ByteArrayOutputStream()){byte[] v=new byte[16384];int n;while((n=source.read(v))!=-1)b.write(v,0,n);return b.toByteArray();}
    }
    private String lesson(String prefix,String definition){return prefix+"faro\ndefinición: "+definition+"\nrequiere: energía\nfuente: X\npáginas: 1";}
    private String correction(PersonalEngine engine,String definition)throws Exception {
        return lesson("corrige lección: ",definition).replace("\ndefinición:","\nrevisión: "+engine.sessionStatus().getString("revision")+"\ndefinición:");
    }
    @Test public void replayAndRollbackSurviveRestart()throws Exception {
        try(PersonalEngine e=new PersonalEngine(context)) {
            String first=e.chat("teach-1",lesson("aprende: ","una luz"));
            JSONObject before=e.sessionStatus();
            assertEquals(first,e.chat("teach-1",lesson("aprende: ","una luz")));
            assertEquals(before.getLong("generation"),e.sessionStatus().getLong("generation"));
            try{e.chat("teach-1","hola");fail("Replay mismatch");}catch(IOException expected){}
            int messages=e.messages().length();
            try{e.testTurn("failed-1",correction(e,"una estrella"),true);fail("Injected rollback");}catch(IOException expected){assertEquals("Injected failure before commit",expected.getMessage());}
            assertEquals(messages,e.messages().length());assertEquals(before.toString(),e.sessionStatus().toString());
        }
        try(PersonalEngine e=new PersonalEngine(context)){
            assertTrue(e.chat("que es faro").contains("una luz"));
            e.chat(correction(e,"una estrella"));assertTrue(e.chat("que es faro").contains("una estrella"));
            e.chat("olvida lección: faro");assertEquals(480,e.sessionStatus().getInt("lessons"));
        }
    }
    @Test public void realQuantumMemoryPersistsAndRollsBack()throws Exception {
        String original;
        try(PersonalEngine e=new PersonalEngine(context)){
            assertTrue(e.chat("memoria guarda faro 1").contains("faro = 1"));
            original=e.sessionStatus().getJSONObject("banks").getString("qmemory");
            try{e.testTurn("bad-correction","memoria corrige faro 0",true);fail("Rollback");}catch(IOException expected){}
            assertEquals(original,e.sessionStatus().getJSONObject("banks").getString("qmemory"));
            assertTrue(e.chat("memoria consulta faro").contains("faro = 1"));
        }
        try(PersonalEngine e=new PersonalEngine(context)){
            assertTrue(e.chat("memoria consulta faro").contains("faro = 1"));
            e.chat("memoria corrige faro 0");assertTrue(e.chat("memoria consulta faro").contains("faro = 0"));
            assertEquals(1,e.sessionStatus().getInt("binary_memories"));
        }
    }
    @Test public void oneChatRoutesToBothQuantumAgentsAndGenerator()throws Exception {
        try(PersonalEngine e=new PersonalEngine(context)){
            assertTrue(e.chat("quantum v3 estado").contains(String.valueOf(e.quantumStatus().getLong("qrl_episodes"))));
            JSONObject plan=e.testTurn("plan","quantum v3 planea 3 6",false);
            assertEquals("QRL3-XI",plan.getString("engine"));assertEquals(0,plan.getJSONObject("metrics").getInt("terminal"));
            JSONObject done=e.testTurn("done","quantum v3 planea 6 6",false);
            assertEquals(1,done.getJSONObject("metrics").getInt("terminal"));assertFalse(done.getJSONObject("metrics").has("action"));
            JSONArray values=new JSONArray();for(int i=0;i<1000;i++)values.put(i%2==0?.1:-.1);
            JSONObject predicted=e.testTurn("classify","quantum v3 clasifica "+values,false);
            assertEquals("VQC3-XI",predicted.getString("engine"));assertTrue(predicted.getJSONObject("metrics").getDouble("probability")>=0);
            JSONObject generated=e.testTurn("generator","qchat hola",false);
            assertEquals("QChat100-XI",generated.getString("engine"));assertEquals("Hola X.",generated.getString("response"));
            assertTrue(generated.getJSONObject("model_output").getBoolean("terminated"));
        }
    }
    @Test public void nativeContextAndLongUtf8TextStayReadOnly()throws Exception {
        try(PersonalEngine e=new PersonalEngine(context)){
            String before=e.stateHash();
            e.chat("Mi proyecto se llama Neral.");assertTrue(e.chat("¿qué dije sobre Neral?").contains("Mi proyecto se llama Neral."));
            StringBuilder b=new StringBuilder();for(int i=0;i<2000;i++)b.append("á🎸");String body=b.toString();
            assertEquals(body,e.chat("repite exactamente:\n"+body));
            assertEquals(before,e.stateHash());
            long generation=e.sessionStatus().getLong("generation");
            for(String bad:new String[]{"", "\uD800", "memoria guarda faro 3"})try{e.chat(bad);fail("Reject invalid input");}catch(IOException expected){}
            assertEquals(generation,e.sessionStatus().getLong("generation"));
        }
    }
    @Test public void corruptCheckpointDoesNotResetOrPublishATurn()throws Exception {
        try(PersonalEngine e=new PersonalEngine(context)){
            int before=e.messages().length();String digest=e.sessionStatus().getJSONObject("banks").getString("qmemory");
            e.db.execSQL("UPDATE states SET data=? WHERE name='qmemory'",new Object[]{new byte[]{1,2,3}});
            try{e.chat("memoria guarda faro 1");fail("Corrupt checkpoint accepted");}catch(IOException expected){}
            assertEquals(before,e.messages().length());
            try(android.database.Cursor c=e.db.rawQuery("SELECT digest FROM states WHERE name='qmemory'",null)){assertTrue(c.moveToFirst());assertEquals(digest,c.getString(0));}
        }
    }
    @Test public void originalAndroidSessionAndTrainingAreMigratedOnce()throws Exception {
        File old=new File(context.getFilesDir(),"bbyq-personal");assertTrue(old.mkdirs());
        Context tests=InstrumentationRegistry.getInstrumentation().getContext();
        byte[] chat=bytes(new GZIPInputStream(tests.getAssets().open("migration-model.rvpbin")));
        byte[] quantum=bytes(new GZIPInputStream(tests.getAssets().open("old-quantum.rvpbin")));
        try(FileOutputStream out=new FileOutputStream(new File(old,"conversation.rvp"))){out.write(chat);}
        try(FileOutputStream out=new FileOutputStream(new File(old,"quantum-v3.rvp"))){out.write(quantum);}
        try(SQLiteDatabase history=SQLiteDatabase.openOrCreateDatabase(new File(old,"history.sqlite"),null)){
            history.execSQL("CREATE TABLE messages(id INTEGER PRIMARY KEY,role TEXT,text TEXT,created INTEGER)");history.execSQL("INSERT INTO messages VALUES(1,'user','historial anterior',1)");
        }
        try(PersonalEngine e=new PersonalEngine(context)){
            assertEquals(PersonalEngine.hash(chat),e.stateHash());assertTrue(e.exportHistory().contains("historial anterior"));
            assertTrue(e.chat("que es prueba movil").contains("una leccion personal de X"));assertEquals(481,e.sessionStatus().getInt("lessons"));
        }
        try(PersonalEngine e=new PersonalEngine(context)){assertEquals(3,e.messages().length());assertEquals(PersonalEngine.hash(chat),e.stateHash());}
        assertArrayEquals(chat,bytes(new FileInputStream(new File(old,"conversation.rvp"))));
    }
    @Test public void concurrentReplayCommitsOnlyOnce()throws Exception {
        try(PersonalEngine a=new PersonalEngine(context);PersonalEngine b=new PersonalEngine(context)){
            ExecutorService pool=Executors.newFixedThreadPool(2);
            try{Future<String> first=pool.submit(()->a.chat("same-id","memoria guarda uno 1"));Future<String> second=pool.submit(()->b.chat("same-id","memoria guarda uno 1"));
                assertEquals(first.get(90,TimeUnit.SECONDS),second.get(90,TimeUnit.SECONDS));assertEquals(1,a.sessionStatus().getLong("generation"));assertEquals(2,a.messages().length());
            }finally{pool.shutdownNow();}
        }
    }
    @Test public void nativeSessionRejectsClosedHandlesAndPreservesFailedCandidate()throws Exception {
        XiSession xi=new XiSession(null);xi.run("#!reverse-pc-machine-v1\nstore8 123 7\nhalt\n");
        try{xi.run("#!reverse-pc-machine-v1\nstore8 123 9\ndiv r0 0\nhalt\n");fail("Native failure");}catch(IllegalStateException expected){}
        assertEquals(7,xi.number(123,1));
        xi.run("#!reverse-pc-machine-v1\nstore8 99999999999999999999999999999999999999999999999999999 1\nhalt\n");
        assertEquals(7,PersonalEngine.memory(xi.save(),123,1)[0]);
        xi.close();xi.close();try{xi.number(123,1);fail("Closed session");}catch(IllegalStateException expected){}
    }
    @Test public void nativeReasoningCompositionAndParaphraseShareTheSession()throws Exception {
        try(PersonalEngine e=new PersonalEngine(context)){
            String before=e.stateHash();
            JSONObject reasoning=e.testTurn("reason","Todos los motores son máquinas. Alpha es un motor. ¿Alpha es máquina?",false);
            assertEquals("P03-XI",reasoning.getString("engine"));assertTrue(reasoning.getString("response").contains("alpha -> motor -> maquinas"));
            JSONObject poem=e.testTurn("poem","Escribe un poema de cuatro versos sobre una guitarra.",false);
            assertEquals("P04-XI",poem.getString("engine"));assertEquals(4,poem.getString("response").split("\n").length);
            JSONObject paraphrase=e.testTurn("paraphrase","hazme un poema sobre una guitarra",false);
            assertEquals("P06-XI",paraphrase.getString("engine"));assertTrue(paraphrase.getString("response").contains("una guitarra"));
            assertEquals(before,e.stateHash());
        }
    }
    @Test public void quantumTextCodecMatchesTheIndependentOriginalPythonCodec()throws Exception {
        Context tests=InstrumentationRegistry.getInstrumentation().getContext();
        JSONArray cases=new JSONArray(new String(bytes(tests.getAssets().open("qchat-codec.json")),java.nio.charset.StandardCharsets.UTF_8));
        try(PersonalEngine e=new PersonalEngine(context)){
            Set<String> input=QuantumText.set(new JSONArray(new String(e.asset("qchat-input-vocabulary.json"),java.nio.charset.StandardCharsets.UTF_8)));
            Set<String> history=QuantumText.set(new JSONArray(new String(e.asset("qchat-history-vocabulary.json"),java.nio.charset.StandardCharsets.UTF_8)));
            for(int i=0;i<cases.length();i++){
                JSONObject c=cases.getJSONObject(i);List<String> prefix=new ArrayList<>();JSONArray p=c.getJSONArray("prefix"),expected=c.getJSONArray("bits");for(int j=0;j<p.length();j++)prefix.add(p.getString(j));
                int[] actual=QuantumText.bits(c.getString("prompt"),prefix,c.getString("previous"),input,history);
                for(int j=0;j<100;j++)assertEquals("case "+i+" bit "+j,expected.getInt(j),actual[j]);
            }
        }
    }
    private JSONObject restoreOldModels(PersonalEngine e,boolean personalize)throws Exception {
        JSONObject before=e.sessionStatus().getJSONObject("banks");
        Context tests=InstrumentationRegistry.getInstrumentation().getContext();
        JSONObject identities=new JSONObject(new String(bytes(tests.getAssets().open("old-identities.json")),java.nio.charset.StandardCharsets.UTF_8));
        for(String bank:new String[]{"quantum","qchat","qmemory"}){
            byte[] state=bytes(new GZIPInputStream(tests.getAssets().open("old-"+bank+".rvpbin")));
            try(XiSession s=new XiSession(state)){
                if(personalize&&bank.equals("quantum"))s.run("#!reverse-pc-machine-v1\nstore64 8140000000000005000 10001\nfstore 8140000000000200000 .1234\nhalt\n");
                if(bank.equals("qmemory"))s.run("#!reverse-pc-machine-v1\nqprepare 20000 4\nx 20000\nhalt\n");
                state=s.save();
            }
            ByteArrayOutputStream packed=new ByteArrayOutputStream();try(java.util.zip.GZIPOutputStream gzip=new java.util.zip.GZIPOutputStream(packed)){gzip.write(state);}
            e.db.execSQL("UPDATE states SET data=?,digest=?,identity=? WHERE name=?",new Object[]{packed.toByteArray(),PersonalEngine.hash(state),identities.getString(bank),bank});
            before.put(bank,PersonalEngine.hash(state));
        }
        e.db.execSQL("INSERT INTO memory_slots VALUES('anterior',0)");
        return before;
    }
    @Test public void balancedUpgradePreservesLessonsBinaryStateAndPersonalTraining()throws Exception {
        JSONObject fresh;
        try(PersonalEngine e=new PersonalEngine(context)){
            fresh=e.quantumStatus();e.chat(lesson("aprende: ","una luz"));restoreOldModels(e,true);
        }
        try(PersonalEngine e=new PersonalEngine(context)){
            assertEquals(fresh.getLong("vqc_episodes"),e.quantumStatus().getLong("vqc_episodes"));
            assertEquals(10001,e.quantumStatus().getLong("qrl_episodes"));
            assertEquals(3,e.sessionStatus().getInt("archived_models"));
            assertTrue(e.chat("que es faro").contains("una luz"));
            assertTrue(e.chat("memoria consulta anterior").contains("anterior = 1"));
            assertEquals("Hola X.",e.chat("qchat hola"));
        }
        try(PersonalEngine e=new PersonalEngine(context)){assertEquals(3,e.sessionStatus().getInt("archived_models"));}
    }
    @Test public void failedModelUpgradeRollsBackEveryBank()throws Exception {
        JSONObject old;
        try(PersonalEngine e=new PersonalEngine(context)){
            old=restoreOldModels(e,false);
            e.db.execSQL("UPDATE states SET data=? WHERE name='qchat'",new Object[]{new byte[]{1,2,3}});
        }
        try{new PersonalEngine(context);fail("Corrupted old model must prevent the upgrade");}catch(IOException expected){}
        File file=new File(context.getFilesDir(),"bbyq-unified/session.sqlite");
        try(SQLiteDatabase db=SQLiteDatabase.openDatabase(file.getPath(),null,SQLiteDatabase.OPEN_READONLY)){
            try(android.database.Cursor c=db.rawQuery("SELECT count(*) FROM model_archives",null)){assertTrue(c.moveToFirst());assertEquals(0,c.getInt(0));}
            try(android.database.Cursor c=db.rawQuery("SELECT name,digest FROM states",null)){while(c.moveToNext())assertEquals(old.getString(c.getString(0)),c.getString(1));}
        }
    }
    @Test public void generatorContextSurvivesCommandsRestartAndRollback()throws Exception {
        try(PersonalEngine e=new PersonalEngine(context)){
            assertEquals("La memoria conserva información.",e.chat("qchat que es memoria"));
            e.chat("memoria guarda faro 1");e.chat("quantum v3 planea 3 6");
            try{e.testTurn("failed-generator","qchat que es circuito",true);fail("Rollback");}catch(IOException expected){assertEquals("Injected failure before commit",expected.getMessage());}
        }
        try(PersonalEngine e=new PersonalEngine(context)){
            JSONObject follow=e.testTurn("follow-up","qchat dime más",false);
            assertEquals("La memoria conserva información.",follow.getString("response"));
            assertTrue(follow.getJSONObject("model_output").getBoolean("context_used"));
            assertEquals("La memoria conserva información.",e.chat("qchat repítelo"));
            assertEquals("Hola X.",e.chat("qchat hola"));
            e.chat("qchat que es memoria");e.chat("@context clear");
            assertFalse(e.testTurn("cleared","qchat dime más",false).getJSONObject("model_output").getBoolean("context_used"));
        }
    }
}
