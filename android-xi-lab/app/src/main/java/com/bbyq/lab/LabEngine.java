package com.bbyq.lab;

import android.content.Context;
import android.util.AtomicFile;
import com.reversepc.os.NativeRuntime;
import com.reversepc.os.ResultPacket;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * C13 real Android XI execution. One private RVPC2; NO synthetic Java learner.
 * XI alone parses conversation commands, trains VQC/QRL, selects Q policies
 * and classifies P01 intents. Java only frames requests and publishes states.
 * This deliberately does NOT claim to host the full X10 SQLite/Node system.
 */
public final class LabEngine {
    private static final long INPUT=9190000000000004096L;
    private static final long LENGTH=9190000000000000008L;
    private static final long TOTAL=9190000000000000012L;
    private static final long ROUTE=8180000000000000000L;
    private static final long INTENT=9190000000000000128L;
    private static final long COGNITIVE=8250000000000000000L;
    private final Context context;
    private final AtomicFile memory;
    public LabEngine(Context context) {
        this.context=context.getApplicationContext();
        this.memory=new AtomicFile(new File(context.getFilesDir(),"bbyq-c13-laboratory.rvp"));
    }
    private static String seed(){return "#!reverse-pc-machine-v1\n";}
    private static String put(long address,int value){
        if(value<0||value>255)throw new IllegalArgumentException("Byte fuera de rango");
        return "store8 "+address+" "+value+"\n";
    }
    private static String frame(byte[] text){
        if(text.length==0||text.length>190)throw new IllegalArgumentException("Máximo 190 bytes UTF-8");
        StringBuilder result=new StringBuilder(seed()).append(put(LENGTH,text.length)).append(put(TOTAL,text.length));
        for(int i=0;i<text.length;i++)result.append(put(INPUT+i,text[i]&255));
        result.append("halt\n");
        return result.toString();
    }
    private static String stage(long[][] changes) {
        StringBuilder result=new StringBuilder(seed());
        for(long[] item:changes)result.append(put(item[0],(int)item[1]));
        return result.append("halt\n").toString();
    }
    private ResultPacket run(byte[] state,String source)throws IOException{
        try {return ResultPacket.parse(NativeRuntime.execute(state,source));}
        catch(Exception error){throw new IOException("Error nativo XI: "+error.getMessage(),error);}
    }
    private String asset(String name)throws IOException{
        if(!name.matches("[a-z0-9-]{1,45}\\.xi"))throw new IOException("Ruta XI no permitida");
        try(InputStream in=context.getAssets().open("xi/"+name);
            ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] buffer=new byte[8192];
            int n;
            while((n=in.read(buffer))!=-1){
                if(out.size()+n>4*1024*1024)throw new IOException("Fuente XI demasiado grande");
                out.write(buffer,0,n);
            }
            return out.toString(StandardCharsets.UTF_8.name());
        }
    }
    private ResultPacket program(byte[] state,String name)throws IOException{return run(state,asset(name+".xi"));}
    private static List<Long> registers(String jsonl)throws IOException{
        List<Long> result=new ArrayList<>();
        try{
            for(String line:jsonl.split("\\n")){
                if(!line.startsWith("{"))continue;
                JSONObject item=new JSONObject(line);
                if("register".equals(item.optString("type")))result.add(item.getLong("value"));
            }
        }catch(Exception ex){throw new IOException("Salida XI corrupta",ex);}
        return result;
    }
    private static int get(List<Long> r,int index)throws IOException{
        if(index<0||index>=r.size()||r.get(index)>Integer.MAX_VALUE||r.get(index)<Integer.MIN_VALUE)
            throw new IOException("Registro XI no disponible");
        return r.get(index).intValue();
    }
    private static String hash(byte[] bytes)throws IOException{
        try{
            byte[] digest=MessageDigest.getInstance("SHA-256").digest(bytes);
            StringBuilder text=new StringBuilder();
            for(byte b:digest)text.append(String.format(Locale.ROOT,"%02x",b&255));
            return text.toString();
        }catch(Exception e){throw new IOException("SHA-256 no disponible",e);}
    }
    private void commit(byte[] candidate)throws IOException{
        if(candidate==null||candidate.length<29||candidate.length>32*1024*1024+29)
            throw new IOException("Memoria RVPC2 inválida");
        try{NativeRuntime.inspect(candidate);}catch(Exception e){throw new IOException("RVPC2 rechazado",e);}
        FileOutputStream file=null;
        try{
            file=memory.startWrite();
            file.write(candidate);
            memory.finishWrite(file);
        }catch(IOException|RuntimeException e){
            if(file!=null)memory.failWrite(file);
            throw new IOException("No se pudo confirmar la memoria XI",e);
        }
    }
    private byte[] read()throws IOException{
        if(!memory.getBaseFile().exists()){
            byte[] state;
            try{state=NativeRuntime.initialize();}
            catch(Exception e){throw new IOException("No se inició REVERSE-PC nativo",e);}
            for(String name:new String[]{"core-birth","vqc2-birth","qrl2-birth","policy-birth"})
                state=program(state,name).state;
            commit(state);
            return state;
        }
        byte[] state=memory.readFully();
        try{NativeRuntime.inspect(state);}catch(Exception e){throw new IOException("RVPC2 persistente corrupto",e);}
        return state;
    }
    private int[] route(byte[] state,String command)throws IOException{
        byte[] text=command.getBytes(StandardCharsets.UTF_8);
        if(text.length>96||text.length==0)throw new IOException("Orden XI de 1 a 96 bytes");
        for(byte b:text)if((b&255)<32||b==127)throw new IOException("No se admiten controles en comandos");
        byte[] framed=run(state,frame(text)).state;
        byte[] decided=program(framed,"conversation-route").state;
        StringBuilder read=new StringBuilder(seed());
        for(int i=0;i<4;i++)read.append("load8 r0 ").append(ROUTE+i).append("\nprint r0\n");
        read.append("halt\n");
        List<Long> v=registers(run(decided,read.toString()).output);
        if(v.size()!=4)throw new IOException("El enrutador XI no devolvió 4 bytes");
        return new int[]{get(v,0),get(v,1),get(v,2),get(v,3)};
    }
    private int[] status(byte[] state)throws IOException{
        List<Long> v=registers(program(state,"vqc2-status").output);
        if(v.size()!=6)throw new IOException("Estado XI incompleto");
        return new int[]{get(v,0),get(v,1),get(v,2),get(v,3),get(v,4),get(v,5)};
    }
    private static String brief(byte[] state)throws IOException{return "Estado SHA-256: "+hash(state).substring(0,16);}
    /** All user-facing quantum commands go through the original C08 native XI parser. */
    public synchronized String command(String message)throws IOException{
        byte[] state=read();
        int[] decision=route(state,message.trim());
        int action=decision[0],x=decision[1],y=decision[2];
        int[] flags=status(state);
        if(action==8)return "BBY Q XI Lab: quantum estado; quantum entrena xor; quantum entrena xnor; quantum evalua; quantum clasifica 0 1; quantum entrena agente; quantum planea 1 0. Esta edición no contiene la conversación X10 completa.";
        if(action==0||action==254)return "XI no reconoció la orden. Escribe «quantum ayuda».";
        if(action==1)return "VQC2 "+(flags[1]==1?"entrenado k="+flags[2]:"sin entrenar")+
            "; QRL2 "+(flags[4]==1?"entrenado, rondas="+flags[5]:"sin entrenar")+". "+brief(state);
        if(action==2||action==3){
            ResultPacket data=program(state,action==2?"vqc2-feed-xor":"vqc2-feed-xnor");
            ResultPacket trained=program(data.state,"vqc2-train");
            List<Long> r=registers(trained.output);
            int k=get(r,0),cost=get(r,1);
            commit(trained.state);
            return "VQC2 entrenado en XI con "+(action==2?"XOR":"XNOR")+
                "; k="+k+", Brier penalizado="+cost+"/10000. "+brief(trained.state);
        }
        if(action==4){
            if(flags[1]!=1)return "VQC2 no entrenado; ejecuta «quantum entrena xor».";
            List<Long> r=registers(program(state,"vqc2-eval").output);
            return "Holdout XI VQC2: "+get(r,0)+"/4, Brier="+get(r,1)+"/10000. No se modificó el modelo.";
        }
        if(action==5){
            if(flags[1]!=1)return "VQC2 no entrenado.";
            if(x>1||y>1)throw new IOException("Dos bits binarios requeridos");
            byte[] framed=run(state,stage(new long[][]{{8100000000000004700L,x},{8100000000000004701L,y}})).state;
            List<Long> r=registers(program(framed,"vqc2-infer").output);
            return "VQC2 Bell ["+x+","+y+"]: clase="+get(r,2)+
                ", P(paridad=1)="+get(r,1)+"/10000, k="+get(r,0)+". Medición simulada en XI; consulta sin mutación.";
        }
        if(action==6){
            ResultPacket trained=program(state,"qrl2-train");
            int epochs=get(registers(trained.output),0);
            commit(trained.state);
            return "QRL2 XI entrenado: rondas="+epochs+", 2 decisiones por episodio. "+brief(trained.state);
        }
        if(action==7){
            if(flags[4]!=1)return "QRL2 no entrenado.";
            if(x>1||y>1)throw new IOException("Objetivo e inicio binarios requeridos");
            byte[] framed=run(state,stage(new long[][]{{8100000000000005005L,x},{8100000000000005006L,y}})).state;
            List<Long> r=registers(program(framed,"qrl2-act").output);
            return "QRL2: objetivo="+x+", inicio="+y+", acciones=["+get(r,0)+","+get(r,2)+
                "], final="+get(r,3)+", éxito="+(get(r,4)==1?"sí":"no")+". Solo consulta.";
        }
        throw new IOException("Acción XI incompatible");
    }
    private static int p01Context(int id) throws IOException{
        if(id<0||id>8)throw new IOException("Intento P01 fuera de la tabla");
        return 2*id; // No P05 conversation history on standalone Android.
    }
    private int contextOf(byte[] state,String question)throws IOException{
        byte[] text=question.getBytes(StandardCharsets.UTF_8);
        byte[] framed=run(state,frame(text)).state;
        byte[] parsed=program(framed,"p01-intent").state;
        List<Long> r=registers(run(parsed,seed()+"load8 r0 "+INTENT+"\nprint r0\nhalt\n").output);
        return p01Context(get(r,0));
    }
    private String policy(byte[] state,int context)throws IOException{
        byte[] framed=run(state,stage(new long[][]{{COGNITIVE+1,context}})).state;
        List<Long> r=registers(program(framed,"policy-decide").output);
        String[] routes={"X10","P05 memoria","P03 razonamiento","P04 composición"};
        return "P01 contexto="+get(r,0)+"; sugerencia XI="+routes[get(r,1)]+
            "; Q="+get(r,2)+"/10000, ejemplos="+get(r,3)+".";
    }
    public synchronized String observe(String message)throws IOException{
        byte[] state=read();
        return policy(state,contextOf(state,message))+
            " Modo observación: no se ejecuta la ruta ni se genera una respuesta X10.";
    }
    public synchronized String feedback(String message,int action,int reward)throws IOException{
        if(action<0||action>3||reward<0||reward>100)throw new IOException("Acción 0..3 y recompensa 0..100");
        byte[] state=read();
        int context=contextOf(state,message),value=reward*100;
        byte[] framed=run(state,stage(new long[][]{
            {COGNITIVE+1,context},{COGNITIVE+2,action},{COGNITIVE+3,value%256},{COGNITIVE+4,value/256}
        })).state;
        ResultPacket trained=program(framed,"policy-update");
        List<Long> r=registers(trained.output);
        commit(trained.state);
        return "Feedback XI: ruta="+get(r,1)+", Q="+get(r,2)+"/10000, actualizaciones="+get(r,3)+". "+
                policy(trained.state,context);
    }
}
