package com.bbyq.personal;

import org.json.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Transport for one shared native-XI task, not an answer or learning model. */
final class EntityCycle {
    static final long E=8184000000000000000L,A=8140000000000000000L,Q=8160000000000000000L,M=8170000000000000000L;
    private final PersonalEngine engine;
    EntityCycle(PersonalEngine e){engine=e;}
    String library()throws Exception {
        StringBuilder b=new StringBuilder();
        for(String name:new String[]{"v3-common.xi","v3-benchmarks.xi","v3-qrl3.xi","v3-step.xi","qchat-model.xi","qmemory-model.xi","entity-workspace.xi","entity-credit.xi","entity-feedback.xi"})b.append(new String(engine.asset(name),StandardCharsets.UTF_8)).append('\n');
        return b.toString();
    }
    JSONObject run(XiSession s,String body)throws Exception{return XiPages.metrics(s.run("#!reverse-pc-machine-v1\nbudget 100000000\n"+body+"\nhalt\n"+library()));}
    private String field(long offset,long value){return "store64 "+(E+offset)+" "+value+"\n";}
    private String real(long offset,double value){if(!Double.isFinite(value))throw new IllegalArgumentException("Número no finito");return "fstore "+(E+offset)+" "+value+"\n";}
    private String number(long offset,String name){return "load64 r0 "+(E+offset)+"\nitof f0 r0\nfemit "+name+" f0\n";}
    private static long integer(JSONObject object,String key,long min,long max)throws Exception {
        Object value=object.get(key);if(!(value instanceof Number))throw new IOException("Se requiere un entero en "+key);double n=((Number)value).doubleValue();long result=((Number)value).longValue();
        if(!Double.isFinite(n)||n!=result||result<min||result>max)throw new IOException("Entero fuera de rango en "+key);return result;
    }
    private static String taskDigest(byte[] frame,String input,String trace,Integer teacher)throws Exception {
        java.io.ByteArrayOutputStream bytes=new java.io.ByteArrayOutputStream();bytes.write(frame);bytes.write(XiPages.utf8(input+"\n"+trace+"\n"+teacher));return PersonalEngine.hash(bytes.toByteArray());
    }
    JSONObject solve(String requestId,JSONObject input)throws Exception {
        String key=input.getString("memoria");int position=(int)integer(input,"posicion",0,6);
        if(key.length()<1||XiPages.utf8(key).length>64||position<0||position>6)throw new IOException("Usa una clave de memoria y una posición de 0 a 6");
        Set<String> allowed=new HashSet<>(Arrays.asList("memoria","posicion","datos","muestra"));Iterator<String> keys=input.keys();while(keys.hasNext())if(!allowed.contains(keys.next()))throw new IOException("Campo de misión desconocido");
        if(input.has("datos")&&input.has("muestra"))throw new IOException("Usa datos o una muestra, una fuente por misión");
        int slot=engine.memorySlot(key);boolean present=slot>=0,sensors=input.has("datos")||input.has("muestra");
        JSONObject trace=new JSONObject().put("version","E02").put("task",requestId).put("memory_key",key).put("position",position);
        try(XiSession shared=new XiSession(engine.bankState("entity"));XiSession quantum=new XiSession(engine.bankState("quantum"));XiSession memory=new XiSession(engine.bankState("qmemory"))) {
            double memoryProbability=0,classProbability=.5;StringBuilder sensorFrame=new StringBuilder();
            if(present){long site=20000+4L*slot;memoryProbability=run(memory,"fexpect f0 Z:"+site+"\nfset f1 1\nfsub f1 f0\nfdiv f1 2\nfemit p f1").getDouble("p");}
            if(input.has("datos")){
                JSONArray values=input.getJSONArray("datos");if(values.length()!=1000)throw new IOException("La misión necesita 1.000 valores numéricos");
                for(int i=0;i<1000;i++){Object v=values.get(i);if(!(v instanceof Number)||!Double.isFinite(((Number)v).doubleValue()))throw new IOException("Los datos deben ser números finitos");sensorFrame.append("fstore ").append(A+300000+8L*i).append(' ').append(((Number)v).doubleValue()).append('\n');}
            }else if(input.has("muestra")){
                long seed=integer(input,"muestra",0,2147483647L);
                sensorFrame.append("store64 ").append(A+256).append(' ').append(seed).append("\nstore64 ").append(A+272).append(" 0\nfstore ").append(A+296).append(" .1\ncall vqc_sample\n");
                trace.put("source","synthetic-example");
            }
            if(sensors)classProbability=run(quantum,sensorFrame+"store64 "+A+" 0\nstore64 "+(A+280)+" 0\ncall select_agent\ncall forward\nfemit p f21").getDouble("p");
            String staged=field(8,present?1:0)+field(16,sensors?1:0)+field(24,position)+field(176,1)+real(40,memoryProbability)+real(48,classProbability);
            JSONObject inferred=run(shared,staged+"call entity_infer\n"+number(88,"valid")+number(72,"goal")+number(56,"class")+number(64,"rule"));
            int action=-1;double right=.5;
            if(inferred.getInt("valid")==1){
                int goal=inferred.getInt("goal");JSONObject plan=run(quantum,"store64 "+(A+344)+" "+position+"\nstore64 "+(A+352)+" "+goal+"\nstore64 "+(A+360)+" 0\nstore64 "+(A+312)+" 12\nstore64 "+(A+320)+" 2\ncall qrl_step");
                action=plan.getInt("terminal")==1?2:plan.getInt("action");right=plan.optDouble("probability_right",.5);trace.put("plan",plan);
            }
            JSONObject decided=run(shared,field(80,action)+real(160,right)+"call entity_decide\n"+number(80,"action")+"fload f0 "+(E+112)+"\nfemit confidence f0");action=decided.getInt("action");
            JSONObject voice=voice(shared);
            StringBuilder check=new StringBuilder(field(592,voice.getJSONArray("ids").length()));
            JSONArray ids=voice.getJSONArray("ids");for(int i=0;i<ids.length();i++)check.append("store8 ").append(E+600+i).append(' ').append(ids.getInt(i)).append('\n');
            JSONObject validation=run(shared,check+"call entity_voice_check\n"+number(144,"voice_correct"));boolean verified=voice.getBoolean("terminated")&&validation.getInt("voice_correct")==1;
            String response=verified?voice.getString("text"):"No pude expresar un plan verificable. Necesito otra observación.";
            trace.put("memory",new JSONObject().put("present",present).put("probability_one",memoryProbability)).put("perception",new JSONObject().put("present",sensors).put("probability_one",classProbability)).put("reasoning",inferred).put("decision",decided).put("voice",voice).put("voice_verified",verified);
            engine.saveBank("entity",shared.save());
            Integer teacher=null;try(android.database.Cursor c=engine.db.rawQuery("SELECT value FROM memory_teachers WHERE key=?",new String[]{key})){if(c.moveToFirst())teacher=c.getInt(0);}
            byte[] frame=shared.bytes(E,352);String inputText=input.toString(),traceText=trace.toString();
            engine.db.execSQL("INSERT INTO entity_tasks(id,input,trace,workspace,digest,teacher,created) VALUES(?,?,?,?,?,?,?)",new Object[]{requestId,inputText,traceText,frame,taskDigest(frame,inputText,traceText,teacher),teacher,System.currentTimeMillis()});
            return new JSONObject().put("response",response).put("engine","E02-Entity-XI").put("entity_task",requestId).put("trace",trace).put("action",verified?action:-1);
        }
    }
    private JSONObject voice(XiSession shared)throws Exception {
        JSONArray vocab=new JSONArray(new String(engine.asset("entity-vocabulary.json"),StandardCharsets.UTF_8));List<String> prefix=new ArrayList<>();JSONArray ids=new JSONArray();boolean terminated=false;
        try(XiSession s=new XiSession(engine.bankState("entity-voice"))){
            StringBuilder initial=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(initial,E,shared.bytes(E,184));s.run(initial.append("halt\n").toString());
            for(int step=0;step<12;step++){
                int[] bits=QuantumText.bits("",prefix,"",Collections.emptySet(),Collections.emptySet());StringBuilder b=new StringBuilder();
                for(int i=0;i<100;i++)b.append("store8 ").append(Q+1000+i).append(' ').append(bits[i]).append('\n');
                String events=s.run("#!reverse-pc-machine-v1\nbudget 100000000\n"+b+"call entity_voice_bits\nstore64 "+(Q+80)+" 0\ncall qchat_encode\ncall qchat_next\nhalt\n"+library());int token=-1;
                for(String line:events.split("\n"))if(line.startsWith("{")){JSONObject e=new JSONObject(line);if(e.optString("type").equals("register")&&e.optString("register").equals("r12"))token=e.getInt("value");}
                if(token==0){terminated=true;break;}if(token<0||token>=vocab.length())throw new IOException("Token de entidad inválido");ids.put(token);prefix.add(vocab.getString(token));
            }
        }
        return new JSONObject().put("text",QuantumText.detokenize(prefix)).put("ids",ids).put("terminated",terminated);
    }
    JSONObject feedback(JSONObject evaluation)throws Exception {
        String taskId=evaluation.getString("tarea");int success=(int)integer(evaluation,"resultado",0,1);
        if(success<0||success>1)throw new IOException("La evaluación admite resultado 0 o 1");byte[] frame;JSONObject input;Integer teacher=null;
        try(android.database.Cursor c=engine.db.rawQuery("SELECT workspace,input,feedback,teacher,trace,digest FROM entity_tasks WHERE id=?",new String[]{taskId})){
            if(!c.moveToFirst())throw new IOException("No encontré esa tarea");
            if(!c.isNull(2))throw new IOException("Esta tarea ya tiene una evaluación; conservé la anterior");frame=c.getBlob(0);if(!c.isNull(3))teacher=c.getInt(3);
            if(frame.length!=352||!taskDigest(frame,c.getString(1),c.getString(4),teacher).equals(c.getString(5)))throw new IOException("La evidencia de la tarea está alterada; conservé los modelos");input=new JSONObject(c.getString(1));
        }
        try(XiSession s=new XiSession(engine.bankState("entity"))){
            StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(b,E+8,Arrays.copyOfRange(frame,8,104));XiPages.data(b,E+144,Arrays.copyOfRange(frame,144,184));s.run(b.append("halt\n").toString());
            run(s,real(96,success)+"call entity_learn");engine.saveBank("entity",s.save());
        }
        JSONArray learned=new JSONArray().put("shared");
        if(evaluation.has("clase")!=evaluation.has("regla"))throw new IOException("Para corregir datos externos incluye clase y regla");
        if(evaluation.has("clase")){
            int label=(int)integer(evaluation,"clase",0,1),rule=(int)integer(evaluation,"regla",0,1);if(!input.has("datos")&&!input.has("muestra"))throw new IOException("Faltan observaciones verificadas para entrenar");
            JSONArray updates=teach(frame,input,label,rule);for(int i=0;i<updates.length();i++)learned.put(updates.getString(i));
        }else if(input.has("muestra")&&teacher!=null){JSONArray updates=teach(frame,input,null,teacher);for(int i=0;i<updates.length();i++)learned.put(updates.getString(i));}
        engine.db.execSQL("UPDATE entity_tasks SET feedback=? WHERE id=?",new Object[]{success,taskId});
        return new JSONObject().put("response","Guardé la evaluación de la tarea y su aprendizaje.").put("engine","E02-Feedback-XI").put("entity_task",taskId).put("feedback",success).put("learned",learned);
    }
    private JSONArray teach(byte[] frame,JSONObject input,Integer suppliedLabel,int rule)throws Exception {
        JSONArray learned=new JSONArray();
        try(XiSession q=new XiSession(engine.bankState("quantum"));XiSession memory=new XiSession(engine.bankState("qmemory"));XiSession voice=new XiSession(engine.bankState("entity-voice"))){
            StringBuilder stage=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(stage,E,frame);q.run(stage.append("halt\n").toString());
            StringBuilder data=new StringBuilder();
            if(input.has("muestra"))data.append("store64 ").append(A+256).append(' ').append(input.getLong("muestra")).append("\nstore64 ").append(A+272).append(" 0\nfstore ").append(A+296).append(" .1\ncall vqc_sample\n");
            else if(input.has("datos")){JSONArray values=input.getJSONArray("datos");for(int i=0;i<1000;i++)data.append("fstore ").append(A+300000+8L*i).append(' ').append(values.getDouble(i)).append('\n');}
            else return learned;
            if(suppliedLabel!=null)data.append("fstore ").append(A+128).append(' ').append(suppliedLabel).append('\n');
            JSONObject observed=run(q,data+"fload f0 "+(A+128)+"\nfemit teacher f0");int label=observed.getInt("teacher");
            long before=q.number(A+5000,8);run(q,field(264,label)+field(272,rule)+"call entity_score\ncall entity_qrl_feedback");
            if(q.number(A+5000,8)>before)learned.put("QRL3");
            run(q,data+"store64 "+A+" 0\nstore64 "+(A+280)+" 0\nfstore "+(A+4024)+" .01\ncall supervised_update");engine.saveBank("quantum",q.save());learned.put("VQC3");
            // Rehearsal uses a private candidate. Copy only learned angles and
            // its update counter back; all user association states stay intact.
            try(XiSession rehearsal=new XiSession(engine.bankState("qmemory"))){
                run(rehearsal,"store64 "+(M+16)+" 0\nstore64 "+(M+200)+" 620511\nstore64 "+(M+208)+" 2\ncall qm_data\nstore8 "+(M+10000)+" "+rule+"\nstore8 "+(M+11000)+" 0\nstore8 "+(M+50000)+" "+rule+"\ncall qm_train");
                StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(b,M+64,rehearsal.bytes(M+64,24));XiPages.data(b,M+24,rehearsal.bytes(M+24,8));memory.run(b.append("halt\n").toString());engine.saveBank("qmemory",memory.save());
                learned.put("QMemory");
            }
            StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(b,E,frame);voice.run(b.append("halt\n").toString());run(voice,"call entity_voice_teacher");int size=(int)voice.number(E+512,8);byte[] tokens=voice.bytes(E+520,size);
            JSONArray vocab=new JSONArray(new String(engine.asset("entity-vocabulary.json"),StandardCharsets.UTF_8));
            for(int epoch=0;epoch<3;epoch++){
                List<String> prefix=new ArrayList<>();
                for(int i=0;i<=size;i++){
                    int[] bits=QuantumText.bits("",prefix,"",Collections.emptySet(),Collections.emptySet());StringBuilder body=new StringBuilder();for(int j=0;j<100;j++)body.append("store8 ").append(Q+1000+j).append(' ').append(bits[j]).append('\n');int target=i==size?0:tokens[i]&255;
                    run(voice,body+"call entity_voice_bits\nstore64 "+(Q+80)+" 0\ncall qchat_encode\ncall qchat_active\nstore64 "+(Q+48)+" "+target+"\nfstore "+(Q+32)+" .03\ncall qchat_train");if(i<size)prefix.add(vocab.getString(target));
                }
            }
            engine.saveBank("entity-voice",voice.save());learned.put("QChat100-action-head");
        }
        return learned;
    }
}
