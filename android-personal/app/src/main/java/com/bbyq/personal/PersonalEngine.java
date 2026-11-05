package com.bbyq.personal;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.util.AtomicFile;
import com.reversepc.os.NativeRuntime;
import org.json.*;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;

/** One durable Android session for X10, history, QChat100, QMemory and V3.
 * Java transports bytes and transactions. XI owns text and circuit decisions. */
public final class PersonalEngine implements AutoCloseable {
    private static PersonalEngine instance;
    public static synchronized PersonalEngine get(Context c)throws Exception {
        if(instance==null)instance=new PersonalEngine(c.getApplicationContext());return instance;
    }
    private final Context context;
    final SQLiteDatabase db;
    private final Map<String,byte[]> cache=new HashMap<>();
    private final JSONObject manifest;
    private static final long F=9100000000000200000L,C=F+256,LEGACY=9110000000000000000L,ROWS=LEGACY+4096;
    private static final long A=8140000000000000000L,M=8170000000000000000L;
    private static final int MAX_STATE=32*1024*1024;
    private static final String[] BANKS={"chat","quantum","qchat","qmemory"};
    private static final String[] SEEDS={"chat-model.rvpbin","quantum-model.rvpbin","qchat-model.rvpbin","qmemory-model.rvpbin"};
    public PersonalEngine(Context c)throws Exception {
        context=c;File dir=new File(c.getFilesDir(),"bbyq-unified");
        if(!dir.exists()&&!dir.mkdirs())throw new IOException("No se pudo abrir tu sesión");
        manifest=new JSONObject(new String(raw("engine/manifest.json"),StandardCharsets.UTF_8));
        db=SQLiteDatabase.openOrCreateDatabase(new File(dir,"session.sqlite"),null);
        boolean ready=false;
        try {
            db.execSQL("PRAGMA synchronous=FULL");
            db.beginTransaction();
            try {
                db.execSQL("CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)");
                db.execSQL("CREATE TABLE IF NOT EXISTS states(name TEXT PRIMARY KEY,data BLOB NOT NULL,digest TEXT NOT NULL,identity TEXT NOT NULL)");
                db.execSQL("CREATE TABLE IF NOT EXISTS lessons(key TEXT PRIMARY KEY,record BLOB NOT NULL CHECK(length(record)=640),digest TEXT NOT NULL,slot INTEGER UNIQUE)");
                db.execSQL("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,request_id TEXT,role TEXT NOT NULL,text TEXT NOT NULL,created INTEGER NOT NULL,UNIQUE(request_id,role))");
                db.execSQL("CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result TEXT NOT NULL)");
                db.execSQL("CREATE TABLE IF NOT EXISTS context_turns(generation INTEGER PRIMARY KEY,utterance TEXT NOT NULL,reply TEXT NOT NULL,digest TEXT NOT NULL)");
                db.execSQL("CREATE TABLE IF NOT EXISTS memory_slots(key TEXT PRIMARY KEY,slot INTEGER UNIQUE NOT NULL CHECK(slot>=0 AND slot<250))");
                db.execSQL("CREATE TABLE IF NOT EXISTS model_archives(name TEXT NOT NULL,identity TEXT NOT NULL,digest TEXT NOT NULL,data BLOB NOT NULL,created INTEGER NOT NULL,PRIMARY KEY(name,identity,digest))");
                if(meta("schema",null)==null)initialize();
                if(!meta("schema","").equals("X10-Android-2"))throw new IOException("Versión de sesión incompatible");
                for(String bank:BANKS){upgradeModel(bank);checkIdentity(bank);}
                db.setTransactionSuccessful();ready=true;
            } finally {db.endTransaction();}
        } finally {if(!ready)db.close();}
    }
    private byte[] raw(String name)throws IOException {
        try(InputStream in=context.getAssets().open(name)){return bounded(in);}
    }
    private static byte[] bounded(InputStream in)throws IOException {
        try(ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[16384];int n;while((n=in.read(b))!=-1){if(out.size()+n>MAX_STATE)throw new IOException("Límite de estado superado");out.write(b,0,n);}return out.toByteArray();
        }
    }
    public static String hash(byte[] b)throws Exception {
        byte[] d=MessageDigest.getInstance("SHA-256").digest(b);StringBuilder s=new StringBuilder();for(byte v:d)s.append(String.format(Locale.ROOT,"%02x",v&255));return s.toString();
    }
    byte[] asset(String name)throws Exception {
        if(!cache.containsKey(name)){
            byte[] b=raw("engine/"+name);if(!hash(b).equals(manifest.getJSONObject("files").getString(name)))throw new IOException("Activo del motor alterado: "+name);cache.put(name,b);
        }return cache.get(name);
    }
    private byte[] seed(String name)throws Exception {try(GZIPInputStream in=new GZIPInputStream(new ByteArrayInputStream(asset(name)))){return bounded(in);}}
    private static byte[] pack(byte[] data)throws IOException {ByteArrayOutputStream b=new ByteArrayOutputStream();try(GZIPOutputStream out=new GZIPOutputStream(b)){out.write(data);}return b.toByteArray();}
    private static byte[] unpack(byte[] data)throws IOException {try(GZIPInputStream in=new GZIPInputStream(new ByteArrayInputStream(data))){return bounded(in);}}
    private String identity(String bank)throws Exception{return manifest.getJSONObject("identities").getString(bank);}
    private void putMeta(String key,Object value){db.execSQL("INSERT OR REPLACE INTO metadata VALUES(?,?)",new Object[]{key,String.valueOf(value)});}
    private String meta(String key,String fallback){try(Cursor c=db.rawQuery("SELECT value FROM metadata WHERE key=?",new String[]{key})){return c.moveToFirst()?c.getString(0):fallback;}}
    private int count(){return Integer.parseInt(meta("count","0"));}
    private void checkIdentity(String name)throws Exception {try(Cursor c=db.rawQuery("SELECT identity FROM states WHERE name=?",new String[]{name})){if(!c.moveToFirst()||!identity(name).equals(c.getString(0)))throw new IOException("El motor cambió; conservé el estado de "+name);}}
    private byte[] state(String name)throws Exception {
        checkIdentity(name);return uncheckedState(name);
    }
    private byte[] uncheckedState(String name)throws Exception {
        try(Cursor c=db.rawQuery("SELECT data,digest FROM states WHERE name=?",new String[]{name})){
            if(!c.moveToFirst())throw new IOException("Estado ausente: "+name);byte[] b=unpack(c.getBlob(0));if(!hash(b).equals(c.getString(1)))throw new IOException("Checkpoint alterado: "+name);return b;
        }
    }
    private void save(String name,byte[] b)throws Exception {db.execSQL("INSERT OR REPLACE INTO states VALUES(?,?,?,?)",new Object[]{name,pack(b),hash(b),identity(name)});}
    private void upgradeModel(String name)throws Exception {
        String old;try(Cursor c=db.rawQuery("SELECT identity FROM states WHERE name=?",new String[]{name})){if(!c.moveToFirst())throw new IOException("Estado ausente: "+name);old=c.getString(0);}
        if(identity(name).equals(old))return;
        JSONObject previous=manifest.optJSONObject("previous_identities");
        if(previous==null||!old.equals(previous.optString(name)))throw new IOException("Identidad de modelo desconocida; conservé "+name);
        byte[] current=uncheckedState(name);
        db.execSQL("INSERT OR IGNORE INTO model_archives SELECT name,identity,digest,data,? FROM states WHERE name=?",new Object[]{System.currentTimeMillis(),name});
        if(name.equals("qchat")){save(name,seed("qchat-model.rvpbin"));return;}
        if(name.equals("quantum")){
            try(XiSession live=new XiSession(current);XiSession fresh=new XiSession(seed("quantum-model.rvpbin"))){
                StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\nbudget 100000000\n");
                for(int role=0;role<2;role++){
                    long meta=A+(role==0?4000:5000),theta=A+(role==0?100000:200000);
                    // A phone may contain additional personal training; retain that agent.
                    if(live.number(meta,8)!=10000){putMeta(role==0?"local_vqc_preserved":"local_qrl_preserved",true);continue;}
                    for(long[] span:new long[][]{{theta,8000},{theta+10000,8000},{theta+20000,8000},{meta,48}})XiPages.data(b,span[0],fresh.bytes(span[0],(int)span[1]));
                }
                live.run(b.append("halt\n").toString());save(name,live.save());return;
            }
        }
        if(name.equals("qmemory")){
            // Learned angles change future writes; existing quantum associations stay intact.
            try(XiSession live=new XiSession(current);XiSession fresh=new XiSession(seed("qmemory-model.rvpbin"))){
                StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(b,M+64,fresh.bytes(M+64,24));XiPages.data(b,M+24,fresh.bytes(M+24,8));
                live.run(b.append("halt\n").toString());save(name,live.save());return;
            }
        }
        throw new IOException("Este modelo requiere una migración específica: "+name);
    }
    private void initialize()throws Exception {
        File old=new File(context.getFilesDir(),"bbyq-personal");
        for(int i=0;i<BANKS.length;i++){
            AtomicFile prior=new AtomicFile(new File(old,i==0?"conversation.rvp":"quantum-v3.rvp"));
            boolean migrate=i<2&&(prior.getBaseFile().exists()||new File(prior.getBaseFile()+".bak").exists());
            byte[] b=migrate?prior.readFully():seed(SEEDS[i]);NativeRuntime.inspect(b);
            if(i==0){byte[] marker=memory(b,LEGACY,2);if(marker[0]!=87||marker[1]!=2)throw new IOException("La conversación anterior necesita una migración compatible");}
            if(i==1&&memory(b,A+1000,1)[0]!=(byte)173)throw new IOException("El checkpoint anterior no es V3 nativo");
            save(BANKS[i],b);
            if(migrate&&i==1&&manifest.has("previous_identities"))db.execSQL("UPDATE states SET identity=? WHERE name='quantum'",new Object[]{manifest.getJSONObject("previous_identities").getString("quantum")});
        }
        putMeta("generation",0);refreshLessons(state("chat"));
        File history=new File(old,"history.sqlite");
        if(history.exists())try(SQLiteDatabase source=SQLiteDatabase.openDatabase(history.getPath(),null,SQLiteDatabase.OPEN_READONLY);
             Cursor rows=source.rawQuery("SELECT role,text,created FROM messages ORDER BY id",null)){
            while(rows.moveToNext())db.execSQL("INSERT INTO messages(role,text,created) VALUES(?,?,?)",new Object[]{rows.getString(0),rows.getString(1),rows.getLong(2)});
        }
        putMeta("schema","X10-Android-2");putMeta("migrated",old.exists());
    }
    private interface CellVisitor {void visit(long address,int value)throws IOException;}
    // Iterate only stored exceptions. No reserved slot range is materialized.
    private static void cells(byte[] state,CellVisitor visitor)throws IOException {
        if(state.length<29)throw new IOException("Estado incompleto");ByteBuffer header=ByteBuffer.wrap(state).order(ByteOrder.LITTLE_ENDIAN);
        long core=header.getLong(5),mem=header.getLong(13);if(core<0||mem<0||core+mem!=state.length-29)throw new IOException("Longitudes RVPC2 inválidas");
        int p=29+(int)core;
        while(p<state.length){int end=p;while(end<state.length&&state[end]!=10)end++;
            if(end>p+4&&state[p]=='O'&&state[p+1]==' '){long address=0;int j=p+2;boolean outside=false;
                while(j<end&&state[j]>='0'&&state[j]<='9'){int v=state[j++]-'0';if(outside||address>(Long.MAX_VALUE-v)/10)outside=true;else address=address*10+v;}
                if(j<end&&state[j++]==' '){int v=0;while(j<end&&state[j]>='0'&&state[j]<='9'){v=v*10+state[j++]-'0';if(v>255)throw new IOException("Byte inválido");}if(!outside)visitor.visit(address,v);}
            }p=end+1;
        }
    }
    static byte[] memory(byte[] state,long base,int length)throws IOException {
        if(length<0||length>65536)throw new IOException("Límite de página superado");byte[] out=new byte[length];
        cells(state,(address,value)->{if(address>=base&&address-base<length)out[(int)(address-base)]=(byte)value;});return out;
    }
    private void refreshLessons(byte[] state)throws Exception {
        byte[] meta=new byte[12];Map<Integer,byte[]> rows=new TreeMap<>();
        cells(state,(address,value)->{
            if(address>=LEGACY&&address-LEGACY<meta.length)meta[(int)(address-LEGACY)]=(byte)value;
            if(address>=ROWS&&address-ROWS<4096*640L){int offset=(int)(address-ROWS),slot=offset/640;byte[] record=rows.get(slot);if(record==null){record=new byte[640];rows.put(slot,record);}record[offset%640]=(byte)value;}
        });int total=0;
        for(Map.Entry<Integer,byte[]> entry:rows.entrySet()){int slot=entry.getKey();byte[] record=entry.getValue();if(record[0]!=1)continue;int n=record[1]&255;if(n<1||n>64)throw new IOException("Clave de lección inválida");
            String key=XiPages.text(Arrays.copyOfRange(record,16,16+n));
            db.execSQL("INSERT OR REPLACE INTO lessons VALUES(?,?,?,?)",new Object[]{key,record,hash(record),slot});total++;
        }
        int expected=(meta[2]&255)|((meta[3]&255)<<8);if(total!=expected)throw new IOException("Recuento de lecciones incompatible");
        putMeta("count",dbCount("lessons"));long revision=0;for(int i=0;i<4;i++)revision|=(meta[8+i]&255L)<<(8*i);putMeta("revision",Math.max(revision,Long.parseLong(meta("revision","0"))));
    }
    private int dbCount(String table){try(Cursor c=db.rawQuery("SELECT count(*) FROM "+table,null)){c.moveToFirst();return c.getInt(0);}}
    public synchronized String chat(String message)throws Exception{return chat(UUID.randomUUID().toString(),message);}
    public synchronized String chat(String requestId,String message)throws Exception{return turn(requestId,message,false).getString("response");}
    synchronized JSONObject testTurn(String id,String text,boolean failBeforeCommit)throws Exception{return turn(id,text,failBeforeCommit);}
    private JSONObject turn(String id,String message,boolean failBeforeCommit)throws Exception {
        if(id==null||!id.matches("[A-Za-z0-9_.-]{1,96}"))throw new IOException("Identificador de operación inválido");
        byte[] raw=XiPages.utf8(message);if(raw.length==0||raw.length>1048576)throw new IOException("Tamaño de mensaje inválido");String digest=hash(raw);
        db.beginTransaction();try {
            try(Cursor c=db.rawQuery("SELECT digest,result FROM receipts WHERE id=?",new String[]{id})){
                if(c.moveToFirst()){if(!digest.equals(c.getString(0)))throw new IOException("El identificador ya corresponde a otro mensaje");JSONObject replay=new JSONObject(c.getString(1));replay.put("replayed",true);return replay;}
            }
            long generation=Long.parseLong(meta("generation","0"));if(generation>=1048576)throw new IOException("Capacidad de sesión alcanzada");
            long started=System.nanoTime();JSONObject result;
            try(XiPages pages=new XiPages(this)){pages.validate(raw);result=dispatch(pages,raw,message);}
            String response=result.getString("response");if(XiPages.utf8(response).length>1048576)throw new IOException("Límite de respuesta superado");
            result.put("generation",generation+1).put("request_id",id).put("replayed",false).put("elapsed_ms",(System.nanoTime()-started)/1000000.0);
            long now=System.currentTimeMillis();db.execSQL("INSERT INTO messages(request_id,role,text,created) VALUES(?,?,?,?)",new Object[]{id,"user",message,now});
            db.execSQL("INSERT INTO messages(request_id,role,text,created) VALUES(?,?,?,?)",new Object[]{id,"assistant",response,now});
            if(!result.optBoolean("context_skip")){
                String utterance=raw.length<=384?message:"",reply=XiPages.utf8(response).length<=512?response:"";
                db.execSQL("INSERT INTO context_turns VALUES(?,?,?,?)",new Object[]{generation+1,utterance,reply,hash(XiPages.utf8(utterance))});
                db.execSQL("DELETE FROM context_turns WHERE generation NOT IN (SELECT generation FROM context_turns ORDER BY generation DESC LIMIT 32)");
            }
            putMeta("generation",generation+1);db.execSQL("INSERT INTO receipts VALUES(?,?,?,?)",new Object[]{id,digest,generation+1,result.toString()});
            if(failBeforeCommit)throw new IOException("Injected failure before commit");
            db.setTransactionSuccessful();return result;
        }finally{db.endTransaction();}
    }
    private static JSONObject reply(String text,String engine)throws Exception{return new JSONObject().put("response",text).put("engine",engine);}
    private JSONObject dispatch(XiPages p,byte[] raw,String text)throws Exception {
        int[] v3=p.quantumRoute(raw);if(v3[3]==1)return quantumTurn(v3,raw);
        int mobile=p.mobileRoute(raw);if(mobile>=1&&mobile<=4)return memoryTurn(p,mobile);
        if(mobile==5){int offset=(int)p.number(XiPages.B+513,1);return generated(p,XiPages.text(Arrays.copyOfRange(raw,offset,raw.length)),true);}
        JSONArray rows=contextRows();JSONObject recalled=contextTurn(p,raw,rows);if(recalled!=null)return recalled;
        int[] route=p.route(raw);int intent=p.intent(raw);
        if(route[0]==2||route[0]==3)return reply(p.stream(raw,route[0]),"X10-stream-XI");
        if(route[0]==1){
            String key=XiPages.text(p.session.bytes(XiPages.B+2048,(int)p.number(XiPages.B+32,1)));byte[] old=null;Integer slot=null;
            try(Cursor c=db.rawQuery("SELECT record,digest,slot FROM lessons WHERE key=?",new String[]{key})){
                if(c.moveToFirst()){old=c.getBlob(0);if(!hash(old).equals(c.getString(1)))throw new IOException("Página de lección alterada");if(!c.isNull(2))slot=c.getInt(2);}
            }
            if(old!=null||route[1]<4||route[1]>7){
                int revision=Integer.parseInt(meta("revision","0"));String response=p.record(old,count(),revision);int status=(int)p.number(XiPages.B+29,1);
                if(status!=0)throw new IOException(response);int next=(int)p.number(XiPages.B+24,4);
                if(next!=revision){
                    byte[] record=p.number(XiPages.B+28,1)==1?p.session.bytes(XiPages.RECORD,640):null;
                    if(record==null)db.execSQL("DELETE FROM lessons WHERE key=?",new Object[]{key});
                    else {
                        if(slot==null){boolean[] used=new boolean[4096];try(Cursor c=db.rawQuery("SELECT slot FROM lessons WHERE slot IS NOT NULL",null)){while(c.moveToNext())used[c.getInt(0)]=true;}for(int i=0;i<used.length;i++)if(!used[i]){slot=i;break;}}
                        db.execSQL("INSERT OR REPLACE INTO lessons VALUES(?,?,?,?)",new Object[]{key,record,hash(record),slot});
                    }
                    putMeta("count",p.number(XiPages.B+20,4));putMeta("revision",next);
                    if(slot!=null)syncLesson(slot,record);
                }
                return reply(response,"X10-lessons-XI");
            }
        }
        if(intent==3||intent==4){String composed=p.compose(raw);if(composed!=null)return reply(composed,"P04-XI");}
        String reason=p.reason(raw);if(reason!=null)return reply(reason,"P03-XI");
        if(intent!=5&&intent!=6){String canonical=p.paraphrase(raw);if(canonical!=null){
            byte[] b=XiPages.utf8(canonical);int mode=(int)p.number(XiPages.PARAPHRASE+1,1);String answer=null;
            if(mode==1){JSONObject r=contextTurn(p,b,rows);if(r!=null)return r;}
            else if(mode>=2&&mode<=4)answer=p.compose(b);else if(mode==5)answer=p.reason(b);
            if(answer!=null)return reply(answer,"P06-XI");
        }}
        if(intent==1){JSONObject candidate=generated(p,text,false);if(candidate!=null)return candidate;}
        return legacy(raw,intent==5||intent==6);
    }
    private void syncLesson(int slot,byte[] record)throws Exception {
        StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");XiPages.data(b,ROWS+slot*640L,record==null?new byte[640]:record);
        try(Cursor c=db.rawQuery("SELECT count(*) FROM lessons WHERE slot IS NOT NULL",null)){c.moveToFirst();XiPages.put(b,LEGACY+2,c.getInt(0),2);}
        XiPages.put(b,LEGACY+8,Long.parseLong(meta("revision","0")),4);
        try(XiSession s=new XiSession(state("chat"))){s.run(b.append("halt\n").toString());save("chat",s.save());}
    }
    private JSONObject legacy(byte[] raw,boolean learn)throws Exception {
        if(raw.length>16384)throw new IOException("Para textos de más de 16.384 bytes usa repetición exacta o resumen extractivo");
        try(XiSession s=new XiSession(state("chat"))){
            s.run(new String(asset("guard.xi"),StandardCharsets.UTF_8));StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");
            for(long[] x:new long[][]{{F+2,1},{F+3,0},{F+4,1},{F+8,raw.length&255},{F+9,raw.length>>>8},{F+10,0}})XiPages.put(b,x[0],x[1],1);
            XiPages.data(b,C,raw);s.run(b.append("halt\n").toString());String events=s.role(asset("front.rxe"));
            if(s.number(9120000000000000002L,1)==0)events=s.role(asset("code.rxe"));
            if(s.number(F+3,1)==3||s.number(F+2,1)!=0)throw new IOException("Entrada no consumida por el motor");
            String response=XiPages.text(XiPages.speech(events,true));if(response.isEmpty())throw new IOException("El motor no emitió respuesta");
            if(s.number(9090000000000000002L,1)==2)response+="\nLa ejecución de tareas de escritorio sigue disponible en el PC.";
            s.run(new String(asset("text-finish.xi"),StandardCharsets.UTF_8));
            if(learn){byte[] next=s.save();save("chat",next);refreshLessons(next);}
            else if(response.equals("Registré tus datos.")||response.equals("Registré esa afirmación."))response="Recibí la afirmación. Para guardarla como aprendizaje, pide «recuerda que ...».";
            return reply(response,"X08-preserved-X10").put("knowledge_read_only",!learn);
        }
    }
    private JSONArray contextRows()throws Exception {
        JSONArray rows=new JSONArray();try(Cursor c=db.rawQuery("SELECT generation,utterance,reply,digest FROM context_turns ORDER BY generation DESC LIMIT 8",null)){
            while(c.moveToNext()){if(!hash(XiPages.utf8(c.getString(1))).equals(c.getString(3)))throw new IOException("Índice de conversación alterado");rows.put(new JSONObject().put("generation",c.getLong(0)).put("utterance",c.getString(1)).put("reply",c.getString(2)));}
        }return rows;
    }
    private JSONObject contextTurn(XiPages p,byte[] raw,JSONArray rows)throws Exception {
        int[] decision=p.context(raw,rows);int mode=decision[0];if(mode==0)return null;String response;
        if(mode==6){int n=dbCount("context_turns");db.execSQL("DELETE FROM context_turns");db.execSQL("DELETE FROM metadata WHERE key IN ('qchat_previous','qchat_previous_generation')");response="Vacié "+n+" entradas del índice breve. Tu historial y tus lecciones siguen guardados.";}
        else if(mode==7)response="El índice breve conserva "+dbCount("context_turns")+" turnos, con un máximo de 32; las consultas examinan los 8 más recientes.";
        else if(mode==8){StringBuilder b=new StringBuilder("Últimos mensajes:\n");for(int i=0;i<Math.min(5,rows.length());i++)b.append(rows.getJSONObject(i).getString("utterance")).append('\n');response=b.toString();}
        else if(mode==3)response="No encontré una mención verificable de ese tema en los turnos recientes.";
        else if(mode==4)response="No puedo identificar un antecedente único. Menciona el tema por su nombre.";
        else {JSONObject row=rows.getJSONObject(decision[1]-1);String value=row.getString(mode==9?"reply":"utterance");response=value.isEmpty()?"No tengo una entrada anterior completa dentro de la ventana conversacional.":"En el turno "+row.getLong("generation")+(mode==9?" respondí: «":" escribiste: «")+value+"».";}
        return reply(response,"P05-XI").put("context_skip",true);
    }
    private JSONObject generated(XiPages pages,String prompt,boolean explicit)throws Exception {
        boolean followUp=pages.qchatNeedsPrevious(prompt);
        long generation=Long.parseLong(meta("generation","0")),prior=Long.parseLong(meta("qchat_previous_generation","-33"));
        String previous=followUp&&generation-prior<=32?meta("qchat_previous",""):"";
        JSONObject generated=QuantumText.generate(this,state("qchat"),prompt,previous);
        if(!generated.getBoolean("terminated")||generated.getString("response").isEmpty()){
            if(!explicit)return null;return reply("El generador no completó una respuesta dentro de su presupuesto de 16 tokens.","QChat100-XI").put("generation",generated);
        }
        if(!explicit&&generated.getDouble("log_probability")<-1)return null;
        // Transport only: XI selects context use; command turns never become model inputs.
        putMeta("qchat_previous",followUp&&!previous.isEmpty()?previous:prompt);putMeta("qchat_previous_generation",generation+1);
        generated.put("context_used",!previous.isEmpty());
        return reply(generated.getString("response"),"QChat100-XI").put("model_output",generated);
    }
    private String qLibrary()throws Exception {return new String(asset("v3-common.xi"),StandardCharsets.UTF_8)+"\n"+new String(asset("v3-benchmarks.xi"),StandardCharsets.UTF_8)+"\n"+new String(asset("v3-qrl3.xi"),StandardCharsets.UTF_8)+"\n"+new String(asset("v3-step.xi"),StandardCharsets.UTF_8);}
    private String quantum(XiSession s,String body)throws Exception{return s.run("#!reverse-pc-machine-v1\nbudget 10000000\n"+body+"\nhalt\n"+qLibrary());}
    private JSONObject status(XiSession s)throws Exception {
        if(s.number(A+1000,1)!=173)throw new IOException("Modelo V3 incompatible");
        return new JSONObject().put("vqc_episodes",s.number(A+4000,8)).put("qrl_episodes",s.number(A+5000,8)).put("qubits_per_agent",1000).put("backend","XI/Ether nativo sin MPS");
    }
    public synchronized JSONObject quantumStatus()throws Exception {try(XiSession s=new XiSession(state("quantum"))){return status(s);}}
    private JSONObject quantumTurn(int[] d,byte[] raw)throws Exception {
        String help="quantum v3 estado; quantum v3 planea POSICIÓN OBJETIVO (0–6); quantum v3 clasifica [1000 números].";
        if(d[0]==5||d[0]==254||d[0]==0)return reply(help,"V3-XI");
        try(XiSession s=new XiSession(state("quantum"))){
            if(d[0]==1){JSONObject st=status(s);return reply("VQC3: "+st.getLong("vqc_episodes")+" episodios; QRL3: "+st.getLong("qrl_episodes")+" episodios. 1.000 cúbits por agente.","V3-XI").put("metrics",st);}
            if(d[0]==2)return reply("Los resultados publicados corresponden a tareas sintéticas y a checkpoints concretos. Consulta el informe de evaluación; no son una medida de conversación general.","V3-XI");
            if(d[0]==4){JSONObject result=action(s,d[1],d[2]);return reply(result.optInt("terminal")==1?"El objetivo ya está alcanzado. No hay movimiento pendiente.":"QRL3 propone moverse a la "+(result.getInt("action")==1?"derecha":"izquierda")+" desde "+d[1]+" hacia "+d[2]+(d[2]==6?".":". Este objetivo no formó parte de su entrenamiento original."),"QRL3-XI").put("metrics",result);}
            if(d[0]==3){
                if(d[4]<1||d[4]>=raw.length||raw.length-d[4]>262144)throw new IOException("Entrada VQC3 fuera de límites");
                JSONArray input=new JSONArray(XiPages.text(Arrays.copyOfRange(raw,d[4],raw.length)));if(input.length()!=1000)throw new IOException("Se requieren exactamente 1.000 números");
                StringBuilder b=new StringBuilder("store64 "+A+" 0\nstore64 "+(A+280)+" 0\n");
                for(int i=0;i<1000;i++){Object value=input.get(i);if(!(value instanceof Number)||!Double.isFinite(((Number)value).doubleValue()))throw new IOException("Se requieren números finitos");b.append("fstore ").append(A+300000+i*8L).append(' ').append(Double.toString(((Number)value).doubleValue())).append('\n');}
                b.append("call select_agent\ncall forward\nfemit probability f21\n");JSONObject result=XiPages.metrics(quantum(s,b.toString()));
                return reply("VQC3 predijo la clase "+(result.getDouble("probability")>=.5?1:0)+" para las 1.000 entradas numéricas.","VQC3-XI").put("metrics",result);
            }throw new IOException("Acción V3 inválida");
        }
    }
    private JSONObject action(XiSession s,int position,int goal)throws Exception {
        if(position<0||position>6||goal<0||goal>6)throw new IOException("Posición u objetivo inválido");
        return XiPages.metrics(quantum(s,"store64 "+(A+344)+" "+position+"\nstore64 "+(A+352)+" "+goal+"\nstore64 "+(A+360)+" 0\nstore64 "+(A+312)+" 12\nstore64 "+(A+320)+" 2\ncall qrl_step"));
    }
    public synchronized JSONObject quantumAction()throws Exception {try(XiSession s=new XiSession(state("quantum"))){return action(s,3,6);}}
    public synchronized JSONObject trainEpisode()throws Exception {
        db.beginTransaction();try(XiSession s=new XiSession(state("quantum"))){
            JSONObject before=status(s);String curriculum=manifest.has("balanced_version")?"store64 "+(A+560)+" 1\nstore64 "+(A+568)+" "+(before.getLong("qrl_episodes")%42)+"\n":"";
            quantum(s,curriculum+"fstore "+(A+304)+" .15\nstore64 "+(A+312)+" 12\nstore64 "+(A+320)+" 0\nstore64 "+(A+328)+" 0\nstore64 "+(A+336)+" 0\ncall qrl_episode");
            JSONObject next=status(s);if(next.getLong("qrl_episodes")!=before.getLong("qrl_episodes")+1)throw new IOException("El entrenamiento no avanzó");save("quantum",s.save());db.setTransactionSuccessful();return next;
        }finally{db.endTransaction();}
    }
    private JSONObject memoryTurn(XiPages p,int op)throws Exception {
        if(op==4)return reply("QMemory: "+dbCount("memory_slots")+" asociaciones binarias guardadas, de 250 disponibles. 1.000 cúbits simulados; consulta y corrección usan las puertas entrenadas.","QMemory-XI");
        String key=XiPages.text(p.session.bytes(XiPages.B+544,(int)p.number(XiPages.B+514,1)));int slot=-1;
        try(Cursor c=db.rawQuery("SELECT slot FROM memory_slots WHERE key=?",new String[]{key})){if(c.moveToFirst())slot=c.getInt(0);}
        if(op==1&&slot>=0)throw new IOException("La asociación ya existe. Usa memoria corrige "+key+" 0|1");
        if(op!=1&&slot<0)throw new IOException("No encontré esa asociación cuántica");
        if(slot<0){boolean[] used=new boolean[250];try(Cursor c=db.rawQuery("SELECT slot FROM memory_slots",null)){while(c.moveToNext())used[c.getInt(0)]=true;}for(int i=0;i<250;i++)if(!used[i]){slot=i;break;}if(slot<0)throw new IOException("La memoria binaria está completa");}
        long site=20000+4L*slot;StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\nbudget 10000000\n");
        if(op==1||op==2){int value=(int)p.number(XiPages.B+515,1);b.append("qprepare ").append(site).append(" 4\n");if(value==1)b.append("x ").append(site+1).append('\n');b.append("set r14 ").append(site).append("\nset r7 ").append(site+1).append("\nfload f5 ").append(M+64).append("\ncall qm_exchange\n");}
        b.append("fexpect f0 Z:").append(site).append("\nfset f1 1\nfsub f1 f0\nfdiv f1 2\nfemit probability_one f1\nhalt\n").append(new String(asset("qmemory-model.xi"),StandardCharsets.UTF_8));
        JSONObject result;
        try(XiSession s=new XiSession(state("qmemory"))){result=XiPages.metrics(s.run(b.toString()));if(op==1||op==2){save("qmemory",s.save());db.execSQL("INSERT OR REPLACE INTO memory_slots VALUES(?,?)",new Object[]{key,slot});}}
        int value=result.getDouble("probability_one")>=.5?1:0;
        return reply((op==3?"La memoria cuántica recuperó ":op==2?"Reemplacé la asociación por ":"Guardé la asociación binaria ")+key+" = "+value+".","QMemory-XI").put("metrics",result);
    }
    public synchronized JSONArray messages(){
        JSONArray all=new JSONArray();try(Cursor c=db.rawQuery("SELECT role,text FROM (SELECT id,role,text FROM messages ORDER BY id DESC LIMIT 100) ORDER BY id",null)){
            while(c.moveToNext())try{all.put(new JSONObject().put("role",c.getString(0)).put("text",c.getString(1)));}catch(JSONException impossible){throw new IllegalStateException(impossible);}
        }return all;
    }
    public synchronized String exportHistory(){StringBuilder b=new StringBuilder("BBY Q · X\n\n");try(Cursor c=db.rawQuery("SELECT role,text FROM messages ORDER BY id",null)){while(c.moveToNext())b.append(c.getString(0).equals("user")?"X":"BBY Q").append(": ").append(c.getString(1)).append("\n\n");}return b.toString();}
    public synchronized String stateHash()throws Exception{return hash(state("chat"));}
    public synchronized JSONObject sessionStatus()throws Exception {
        JSONObject banks=new JSONObject();for(String name:BANKS){checkIdentity(name);try(Cursor c=db.rawQuery("SELECT digest FROM states WHERE name=?",new String[]{name})){c.moveToFirst();banks.put(name,c.getString(0));}}
        String integrity;try(Cursor c=db.rawQuery("PRAGMA integrity_check",null)){c.moveToFirst();integrity=c.getString(0);}
        return new JSONObject().put("engine","X10-Android-2").put("release",manifest.optString("balanced_version","2.0")).put("generation",Long.parseLong(meta("generation","0"))).put("lessons",count()).put("revision",meta("revision","0")).put("banks",banks).put("integrity",integrity).put("binary_memories",dbCount("memory_slots")).put("archived_models",dbCount("model_archives"));
    }
    @Override public synchronized void close(){db.close();synchronized(PersonalEngine.class){if(instance==this)instance=null;}}
}
