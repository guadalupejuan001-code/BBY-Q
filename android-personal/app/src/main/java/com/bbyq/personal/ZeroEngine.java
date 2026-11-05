package com.bbyq.personal;

import android.database.Cursor;
import org.json.*;
import java.io.*;
import java.math.BigDecimal;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;

/** Vocabulary/row transport and rendering. Rules, proof search, routes,
 * arithmetic, contextual reference and feedback are native XI programs. */
final class ZeroEngine {
    static final long Z=9185000000000000000L;
    private static final Pattern TOKENS=Pattern.compile("\\$[a-z]+|[0-9]+(?:\\.[0-9]+)?|[\\p{L}\\p{N}_]+|[.!?;,:()+*/-]");
    private static final Pattern NUMBER=Pattern.compile("[0-9]+(?:\\.[0-9]+)?");
    private final PersonalEngine engine;
    private final JSONObject words;
    ZeroEngine(PersonalEngine e)throws Exception{engine=e;words=new JSONObject(new String(e.asset("zero-schema.json"),StandardCharsets.UTF_8)).getJSONObject("words");}
    static void initialize(PersonalEngine e)throws Exception {
        e.db.execSQL("CREATE TABLE IF NOT EXISTS zero_vocab(id INTEGER PRIMARY KEY,token TEXT UNIQUE NOT NULL)");
        e.db.execSQL("CREATE TABLE IF NOT EXISTS zero_facts(key TEXT PRIMARY KEY,record BLOB NOT NULL CHECK(length(record)=32),digest TEXT NOT NULL,source TEXT NOT NULL)");
        e.db.execSQL("CREATE TABLE IF NOT EXISTS zero_rules(key TEXT PRIMARY KEY,record BLOB NOT NULL CHECK(length(record)=128),digest TEXT NOT NULL,source TEXT NOT NULL)");
        e.db.execSQL("CREATE TABLE IF NOT EXISTS zero_tasks(id TEXT PRIMARY KEY,kind INTEGER NOT NULL,status INTEGER NOT NULL,trace TEXT NOT NULL,digest TEXT NOT NULL,feedback INTEGER CHECK(feedback IN (0,1)),created INTEGER NOT NULL)");
        JSONObject words=new JSONObject(new String(e.asset("zero-schema.json"),StandardCharsets.UTF_8)).getJSONObject("words");Iterator<String> names=words.keys();
        while(names.hasNext()){String word=names.next();int id=words.getInt(word);e.db.execSQL("INSERT OR IGNORE INTO zero_vocab VALUES(?,?)",new Object[]{id,word});try(Cursor c=e.db.rawQuery("SELECT token FROM zero_vocab WHERE id=?",new String[]{String.valueOf(id)})){if(!c.moveToFirst()||!c.getString(0).equals(word))throw new IOException("Vocabulario de BBY Q 0 incompatible");}}
        try(Cursor c=e.db.rawQuery("SELECT name FROM states WHERE name='zero'",null)){
            if(!c.moveToFirst())try(XiSession s=new XiSession(null)){s.run("#!reverse-pc-machine-v1\nstore64 "+(Z+900)+" 1\nhalt\n");e.saveBank("zero",s.save());}
        }
        e.bankState("zero");
    }
    private static List<String> tokens(String text){
        String normalized=Normalizer.normalize(text.toLowerCase(Locale.ROOT),Normalizer.Form.NFD).replaceAll("\\p{M}","");List<String> out=new ArrayList<>();Matcher m=TOKENS.matcher(normalized);while(m.find())out.add(m.group());return out;
    }
    private long word(String text){
        try(Cursor c=engine.db.rawQuery("SELECT id FROM zero_vocab WHERE token=?",new String[]{text})){if(c.moveToFirst())return c.getLong(0);}
        long id;try(Cursor c=engine.db.rawQuery("SELECT COALESCE(MAX(id),1023)+1 FROM zero_vocab",null)){c.moveToFirst();id=Math.max(1024,c.getLong(0));}engine.db.execSQL("INSERT INTO zero_vocab VALUES(?,?)",new Object[]{id,text});return id;
    }
    private String token(long id){
        if(id<0)return "$"+(char)('x'+(int)(-id-1));
        try(Cursor c=engine.db.rawQuery("SELECT token FROM zero_vocab WHERE id=?",new String[]{String.valueOf(id)})){return c.moveToFirst()?c.getString(0):"[término desconocido]";}
    }
    private static long integer(byte[] data,int index){return ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN).getLong(index*8);}
    private static byte[] packed(long... values){ByteBuffer b=ByteBuffer.allocate(values.length*8).order(ByteOrder.LITTLE_ENDIAN);for(long v:values)b.putLong(v);return b.array();}
    private static void stage(XiSession s,long offset,byte[] bytes){StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(b,Z+offset,bytes);s.run(b.append("halt\n").toString());}
    private long number(XiSession s,long offset){return s.number(Z+offset,8);}
    private String call(XiSession s,int command)throws Exception {s.run("#!reverse-pc-machine-v1\nstore64 "+(Z+24)+" "+command+"\nhalt\n");return s.run(new String(engine.asset("zero.xi"),StandardCharsets.UTF_8));}
    private static final class Parsed {
        String text;int op,status;byte[] atom,rule;
        Parsed(String value){text=value;}
    }
    private Parsed parse(XiSession s,String text,boolean batch)throws Exception {
        Parsed p=new Parsed(text);List<String> list=tokens(text);
        StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\nstore64 "+(Z+32)+" "+list.size()+"\nstore64 "+(Z+136)+" "+(batch?1:0)+"\n");
        for(int i=0;i<Math.min(128,list.size());i++){
            String value=list.get(i);b.append("store64 ").append(Z+4096+8L*i).append(' ').append(word(value)).append('\n');boolean numeric=NUMBER.matcher(value).matches();
            b.append("store64 ").append(Z+8192+8L*i).append(' ').append(numeric?1:0).append('\n');
            if(numeric){double n=Double.parseDouble(value);if(!Double.isFinite(n))throw new IOException("Número fuera del rango disponible");b.append("fstore ").append(Z+12288+8L*i).append(' ').append(n).append('\n');}
        }
        s.run(b.append("halt\n").toString());call(s,0);p.op=(int)number(s,0);p.status=(int)number(s,16);
        if(Arrays.asList(1,3,4,8,9,10,14,15).contains(p.op))p.atom=s.bytes(Z+16384,32);
        if(p.op==2||p.op==7||p.op==12)p.rule=s.bytes(Z+16448,128);return p;
    }
    private List<byte[]> records(String table,int length)throws Exception {
        List<byte[]> rows=new ArrayList<>();try(Cursor c=engine.db.rawQuery("SELECT record,digest FROM "+table+" ORDER BY rowid",null)){
            while(c.moveToNext()){byte[] row=c.getBlob(0);if(row.length!=length||!PersonalEngine.hash(row).equals(c.getString(1)))throw new IOException("Conocimiento de BBY Q 0 alterado; conservé el estado");rows.add(row);}
        }return rows;
    }
    private void knowledge(XiSession s,List<byte[]> facts,List<byte[]> rules,int budget)throws Exception {
        if(facts.size()>1024||rules.size()>256)throw new IOException("La consulta supera la capacidad de esta ventana de trabajo; divide el conocimiento en grupos");
        StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");
        for(int i=0;i<facts.size();i++){byte[] row=new byte[64];System.arraycopy(facts.get(i),0,row,0,32);ByteBuffer.wrap(row).order(ByteOrder.LITTLE_ENDIAN).putLong(32,i+1);XiPages.data(b,Z+100000+64L*i,row);}
        for(int i=0;i<rules.size();i++){byte[] row=rules.get(i).clone();ByteBuffer.wrap(row).order(ByteOrder.LITTLE_ENDIAN).putLong(104,i+1).putLong(112,1);XiPages.data(b,Z+200000+128L*i,row);}
        b.append("store64 ").append(Z+64).append(' ').append(facts.size()).append("\nstore64 ").append(Z+72).append(' ').append(rules.size()).append("\nstore64 ").append(Z+104).append(' ').append(budget).append('\n');s.run(b.append("halt\n").toString());
    }
    private List<byte[]> lessonFacts()throws Exception {
        List<byte[]> rows=new ArrayList<>();long relation=word("requiere");
        // The existing field is transported as one term, never split into new claims.
        try(Cursor c=engine.db.rawQuery("SELECT record,digest FROM lessons ORDER BY rowid",null)){
            while(c.moveToNext()){
                byte[] row=c.getBlob(0);if(row.length!=640||!PersonalEngine.hash(row).equals(c.getString(1)))throw new IOException("Lección alterada");int key=row[1]&255,requirement=row[3]&255;if(key<1||key>64||requirement<1||requirement>224)continue;
                String subject=String.join("_",tokens(XiPages.text(Arrays.copyOfRange(row,16,16+key)))),object=String.join("_",tokens(XiPages.text(Arrays.copyOfRange(row,304,304+requirement))));if(!subject.isEmpty()&&!object.isEmpty())rows.add(packed(word(subject),relation,word(object),1));
            }
        }return rows;
    }
    private String fact(byte[] row){return token(integer(row,0))+" "+(integer(row,3)<0?"no ":"")+token(integer(row,1))+" "+token(integer(row,2));}
    private void teach(Parsed p)throws Exception {
        if(p.op==2||p.op==12){String key=PersonalEngine.hash(Arrays.copyOf(p.rule,104));if(p.op==12)engine.db.execSQL("DELETE FROM zero_rules WHERE key=?",new Object[]{key});else engine.db.execSQL("INSERT OR IGNORE INTO zero_rules VALUES(?,?,?,?)",new Object[]{key,p.rule,PersonalEngine.hash(p.rule),p.text});return;}
        String key=PersonalEngine.hash(p.atom);
        if(p.op==8){try(Cursor c=engine.db.rawQuery("SELECT key,record,digest FROM zero_facts",null)){List<String> remove=new ArrayList<>();while(c.moveToNext()){byte[] row=c.getBlob(1);if(row.length!=32||!PersonalEngine.hash(row).equals(c.getString(2)))throw new IOException("Hecho alterado");if(Arrays.equals(Arrays.copyOf(row,24),Arrays.copyOf(p.atom,24)))remove.add(c.getString(0));}for(String k:remove)engine.db.execSQL("DELETE FROM zero_facts WHERE key=?",new Object[]{k});}}
        if(p.op==9)engine.db.execSQL("DELETE FROM zero_facts WHERE key=?",new Object[]{key});else engine.db.execSQL("INSERT OR IGNORE INTO zero_facts VALUES(?,?,?,?)",new Object[]{key,p.atom,PersonalEngine.hash(p.atom),p.text});
    }
    JSONObject solve(XiPages pages,String text)throws Exception{return solve(pages,text,30000);}
    void clearContext()throws Exception {
        try(XiSession s=new XiSession(engine.bankState("zero"))){if(number(s,920)!=0||number(s,928)!=1){stage(s,920,packed(0,1));engine.saveBank("zero",s.save());}}
    }
    JSONObject solve(XiPages pages,String text,int budget)throws Exception {
        if(XiPages.utf8(text).length>262144)return null;String[] parts=text.split("[;\\n]+");List<String> lines=new ArrayList<>();for(String v:parts)if(!v.trim().isEmpty())lines.add(v.trim());if(lines.isEmpty()||lines.size()>64)return null;
        try(XiSession s=new XiSession(engine.bankState("zero"))){
            List<Parsed> parsed=new ArrayList<>();boolean batch=false;
            for(String line:lines){Parsed p=parse(s,line,batch);if(p.op==0)return null;if(p.status==4)throw new IOException("No pude interpretar ese paso. Usa un hecho de tres términos o una regla con premisas completas.");parsed.add(p);batch|=p.op==11;}
            List<byte[]> temporaryFacts=new ArrayList<>(),temporaryRules=new ArrayList<>();JSONArray steps=new JSONArray();List<String> answers=new ArrayList<>();int lastKind=3,lastStatus=1;stage(s,224,packed(1));
            for(Parsed initial:parsed){
                Parsed p=parse(s,initial.text,batch);int op=p.op;JSONObject step=new JSONObject().put("operation",op).put("input",p.text);lastKind=op;lastStatus=p.status;
                if(op==1||op==2||op==8||op==9||op==12){
                    teach(p);step.put("status",1).put("persistent",true);lastStatus=1;
                    if(op==1||op==8)stage(s,920,packed(integer(p.atom,0),0));
                    answers.add(op==9||op==12?"Retiré ese conocimiento explícito y volveré a calcular sus consecuencias.":op==8?"Guardé la corrección. Las reglas que sigan contradiciéndola se mostrarán como conflicto.":op==2?"Aprendí la regla; puedo aplicarla a otros sujetos con las mismas relaciones.":"Aprendí: "+fact(p.atom)+".");
                }else if(op==10){temporaryFacts.add(p.atom);stage(s,920,packed(integer(p.atom,0),0));step.put("status",1).put("persistent",false);}
                else if(op==7){temporaryRules.add(p.rule);step.put("status",1).put("persistent",false);}
                else if(op==11){step.put("status",1);}
                else if(op==6){JSONObject feedback=feedbackLatest(s,number(s,56));answers.add(feedback.getString("response"));step.put("status",1).put("feedback",feedback);lastKind=6;lastStatus=1;}
                else if(op==14||op==15){
                    JSONObject evidence=observe(s,p);step.put("evidence",evidence);int status=evidence.getInt("status");lastStatus=status;step.put("status",status);
                    if(status==1){byte[] atom=s.bytes(Z+16384,32);temporaryFacts.add(atom);step.put("atom",new JSONArray(Arrays.asList(integer(atom,0),integer(atom,1),integer(atom,2),integer(atom,3))));answers.add((op==15?"El clasificador propone: ":"Recuperé de memoria: ")+fact(atom)+".");}
                    else answers.add("Falta la asociación de memoria solicitada. Puedes enseñarla con memoria guarda CLAVE 0|1.");
                }else if(op==16){
                    Matcher m=TOKENS.matcher(p.text);if(!m.find())throw new IOException("Consulta vacía");String tool=p.text.substring(m.end()).trim();JSONObject result=engine.dispatchExisting(pages,tool);answers.add(result.getString("response"));lastStatus=result.optInt("status",1);step.put("status",lastStatus).put("tool",result);
                }else if(op==3||op==4){
                    if(p.status==5){step.put("status",5);answers.add("No puedo identificar un antecedente único. Nombra el sujeto.");lastStatus=5;}
                    else{
                        List<byte[]> facts=records("zero_facts",32),rules=records("zero_rules",128);facts.addAll(lessonFacts());facts.addAll(temporaryFacts);rules.addAll(temporaryRules);knowledge(s,facts,rules,budget);call(s,op==3?1:2);int status=(int)number(s,16),count=(int)number(s,112);lastStatus=status;
                        step.put("status",status).put("work",number(s,152)).put("premises",facts.size()).put("rules",rules.size());
                        if(status==3)answers.add("No completé la búsqueda dentro del presupuesto de trabajo. El resultado sigue sin determinar.");
                        else if(status==0)answers.add(op==4?"No encontré una ruta con las conexiones conocidas.":"No tengo evidencia suficiente para determinarlo.");
                        else if(op==4){
                            if(status==2)answers.add("Hay conexiones contradictorias. Necesito aclararlas antes de dar una ruta.");
                            else{byte[] path=s.bytes(Z+300000,count*8);JSONArray nodes=new JSONArray();List<String> names=new ArrayList<>();for(int i=count-1;i>=0;i--){long id=integer(path,i);nodes.put(id);names.add(token(id));}step.put("path",nodes);answers.add("Ruta: "+String.join(" → ",names)+". Pasos: "+Math.max(0,count-1)+".");}
                        }else{
                            int proofCount=(int)number(s,176),total=(int)number(s,80);byte[] proof=s.bytes(Z+304096,proofCount*8);JSONArray witness=new JSONArray();List<String> statements=new ArrayList<>();
                            for(int i=proofCount-1;i>=0;i--){int index=(int)integer(proof,i)-1;if(index<0||index>=total)throw new IOException("Referencia de prueba inválida");byte[] row=s.bytes(Z+100000+64L*index,64);JSONObject evidence=new JSONObject().put("fact",fact(row)).put("rule",integer(row,5)).put("left",integer(row,6)).put("right",integer(row,7));witness.put(evidence);statements.add(fact(row));}
                            step.put("proof",witness);String prefix=status==2?"Hay evidencia a favor y en contra; necesito una aclaración.":status==-1?"La evidencia contradice esa afirmación.":"Sí, se deduce de los hechos y reglas disponibles.";
                            if(integer(p.atom,0)<0||integer(p.atom,1)<0||integer(p.atom,2)<0){List<String> matches=new ArrayList<>();byte[] refs=s.bytes(Z+300000,count*8);for(int i=0;i<count;i++){int index=(int)integer(refs,i)-1;matches.add(fact(s.bytes(Z+100000+64L*index,64)));}prefix=status==2?"Hay resultados contradictorios.":"Encontré: "+String.join("; ",matches)+".";}
                            answers.add(prefix+(statements.isEmpty()?"":"\nEvidencia: "+String.join(" → ",statements)+"."));
                        }
                    }
                }else if(op==5){String events=call(s,3);int status=(int)number(s,16);lastStatus=status;step.put("status",status);if(status!=1)throw new IOException("La expresión está incompleta o contiene una operación inválida, como dividir entre cero");double value=XiPages.metrics(events).getDouble("result");step.put("result",value);answers.add("El resultado es "+BigDecimal.valueOf(value).stripTrailingZeros().toPlainString()+".");}
                stage(s,232,packed(step.optInt("status",1)));call(s,6);steps.put(step);
            }
            if(answers.isEmpty())answers.add("Preparé los hechos y reglas para esta tarea. Añade una pregunta o un objetivo.");
            lastStatus=(int)number(s,224);String id=UUID.randomUUID().toString();JSONObject trace=new JSONObject().put("version","0").put("task",id).put("steps",steps).put("status",lastStatus);String evidence=trace.toString();
            if(lastKind!=6){int learnedKind=Math.min(16,Math.max(1,lastKind));engine.db.execSQL("INSERT INTO zero_tasks(id,kind,status,trace,digest,created) VALUES(?,?,?,?,?,?)",new Object[]{id,learnedKind,lastStatus,evidence,PersonalEngine.hash(XiPages.utf8(evidence)),System.currentTimeMillis()});}
            engine.saveBank("zero",s.save());return new JSONObject().put("response",String.join("\n\n",answers)).put("engine","BBY-Q-0-XI").put("zero_task",id).put("trace",trace).put("status",lastStatus);
        }
    }
    private JSONObject observe(XiSession s,Parsed p)throws Exception {
        double probability=0;boolean present=true;JSONObject evidence=new JSONObject();
        if(p.op==14){String key=token(integer(p.atom,0));int slot=engine.memorySlot(key);present=slot>=0;if(present)try(XiSession memory=new XiSession(engine.bankState("qmemory"))){EntityCycle cycle=new EntityCycle(engine);probability=cycle.run(memory,"fexpect f0 Z:"+(20000+4L*slot)+"\nfset f1 1\nfsub f1 f0\nfdiv f1 2\nfemit p f1").getDouble("p");}evidence.put("component","QMemory").put("key",key);}
        else{long seed=number(s,56);try(XiSession q=new XiSession(engine.bankState("quantum"))){EntityCycle cycle=new EntityCycle(engine);long a=EntityCycle.A;probability=cycle.run(q,"store64 "+(a+256)+" "+seed+"\nstore64 "+(a+272)+" 0\nfstore "+(a+296)+" .1\ncall vqc_sample\nstore64 "+a+" 0\nstore64 "+(a+280)+" 0\ncall select_agent\ncall forward\nfemit p f21").getDouble("p");}evidence.put("component","VQC3").put("source","synthetic-example").put("seed",seed);}
        s.run("#!reverse-pc-machine-v1\nstore64 "+(Z+192)+" "+p.op+"\nstore64 "+(Z+216)+" "+(present?1:0)+"\nfstore "+(Z+208)+" "+probability+"\nhalt\n");call(s,5);return evidence.put("probability_one",probability).put("status",number(s,16));
    }
    private JSONObject feedbackLatest(XiSession s,long rating)throws Exception {
        JSONObject target=engine.latestPendingTask();if(target==null)throw new IOException("No hay tareas pendientes de evaluar");
        if(target.getString("kind").equals("entity"))return new EntityCycle(engine).feedback(new JSONObject().put("tarea",target.getString("id")).put("resultado",rating));
        return feedback(s,target.getString("id"),rating);
    }
    JSONObject feedbackId(String id,int rating)throws Exception {
        try(XiSession s=new XiSession(engine.bankState("zero"))){JSONObject result=feedback(s,id,rating);engine.saveBank("zero",s.save());return result.put("engine","BBY-Q-0-Feedback-XI").put("zero_task",id);}
    }
    private JSONObject feedback(XiSession s,String target,long rating)throws Exception {
        String id,trace;int kind;
        try(Cursor c=engine.db.rawQuery("SELECT id,kind,trace,digest,feedback FROM zero_tasks WHERE id=?",new String[]{target})){
            if(!c.moveToFirst())throw new IOException("No hay una tarea de BBY Q 0 pendiente de evaluar");id=c.getString(0);kind=c.getInt(1);trace=c.getString(2);if(!PersonalEngine.hash(XiPages.utf8(trace)).equals(c.getString(3)))throw new IOException("La evidencia está alterada; conservé el aprendizaje");
            if(!c.isNull(4))throw new IOException("Esta tarea ya tiene una evaluación");
        }
        stage(s,192,packed(kind));stage(s,56,packed(rating));call(s,4);JSONArray children=new JSONArray();
        if(rating==1){JSONArray steps=new JSONObject(trace).getJSONArray("steps");Set<String> seen=new HashSet<>();for(int i=0;i<steps.length();i++){JSONObject tool=steps.getJSONObject(i).optJSONObject("tool");if(tool==null||!tool.has("entity_task"))continue;String child=tool.getString("entity_task");if(!seen.add(child))continue;boolean pending;try(Cursor c=engine.db.rawQuery("SELECT feedback FROM entity_tasks WHERE id=?",new String[]{child})){pending=c.moveToFirst()&&c.isNull(0);}if(pending)children.put(new EntityCycle(engine).feedback(new JSONObject().put("tarea",child).put("resultado",1)));}}
        engine.db.execSQL("UPDATE zero_tasks SET feedback=? WHERE id=?",new Object[]{rating,id});
        return new JSONObject().put("response","Guardé tu evaluación. Los hechos y las pruebas conservan su evidencia.").put("task",id).put("updates",number(s,944)).put("specialist_feedback",children);
    }
}
