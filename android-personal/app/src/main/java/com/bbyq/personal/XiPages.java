package com.bbyq.personal;

import java.io.*;
import java.nio.*;
import java.nio.charset.*;
import java.util.*;
import org.json.*;

/** Port of X10 NativePages: bounded byte frames, native decisions, no host text classifier. */
final class XiPages implements AutoCloseable {
    static final long B=9190000000000000000L, INPUT=B+4096, RECORD=B+16384;
    static final long CONTEXT=B+196608, REASON=B+65536, COMPOSE=B+98304, PARAPHRASE=B+262144;
    final XiSession session = new XiSession(null);
    final PersonalEngine engine;
    XiPages(PersonalEngine engine) { this.engine=engine; }
    static byte[] utf8(String s) throws IOException {
        try { ByteBuffer b=StandardCharsets.UTF_8.newEncoder().onMalformedInput(CodingErrorAction.REPORT)
                .onUnmappableCharacter(CodingErrorAction.REPORT).encode(java.nio.CharBuffer.wrap(s));
            byte[] out=new byte[b.remaining()];b.get(out);return out;
        } catch(CharacterCodingException e) { throw new IOException("El texto contiene Unicode incompleto",e); }
    }
    static String text(byte[] b) throws IOException {
        try { return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(b)).toString(); }
        catch(CharacterCodingException e) { throw new IOException("Salida UTF-8 inválida",e); }
    }
    static void put(StringBuilder b,long address,long value,int n) {
        for(int i=0;i<n;i++) b.append("store8 ").append(address+i).append(' ').append((value >>> (8*i))&255).append('\n');
    }
    static void data(StringBuilder b,long address,byte[] bytes) {
        for(int i=0;i<bytes.length;i++) put(b,address+i,bytes[i]&255,1);
    }
    void frame(byte[] raw,int offset,int total,String extra) {
        StringBuilder b=new StringBuilder("#!reverse-pc-machine-v1\n");
        put(b,B+8,raw.length,4);put(b,B+12,total,4);put(b,B+16,offset,4);data(b,INPUT,raw);
        session.run(b.append(extra).append("halt\n").toString());
    }
    String role(String name) throws Exception { return session.role(engine.asset(name+".rxe")); }
    long number(long address,int n) { return session.number(address,n); }
    void validate(byte[] raw) throws Exception {
        if(raw.length==0||raw.length>1048576) throw new IOException("Escribe entre 1 y 1.048.576 bytes");
        for(int offset=0;offset<raw.length;offset+=8192) {
            frame(Arrays.copyOfRange(raw,offset,Math.min(offset+8192,raw.length)),offset,raw.length,"");
            role("validate"); if(number(B+29,1)!=0) throw new IOException("Texto UTF-8 o controles no válidos");
        }
        if(number(B+48,1)!=0) throw new IOException("Secuencia UTF-8 incompleta");
    }
    int intent(byte[] raw) throws Exception { frame(Arrays.copyOf(raw,Math.min(raw.length,8192)),0,raw.length,"");role("intent");return (int)number(B+128,1); }
    int[] route(byte[] raw) throws Exception {
        frame(Arrays.copyOf(raw,Math.min(raw.length,8192)),0,raw.length,"");role("route");
        if(number(B+29,1)!=0)throw new IOException("La lección está incompleta o supera sus límites. Incluye definición, requiere, fuente y páginas; para corregir, añade revisión: N antes de la definición, usando la revisión de la respuesta anterior.");
        return new int[]{(int)number(B+64,1),(int)number(B+33,1)};
    }
    int[] quantumRoute(byte[] raw) throws Exception {
        frame(Arrays.copyOf(raw,Math.min(raw.length,128)),0,raw.length,"");role("v3-route");
        long q=8183000000000000000L;
        return new int[]{(int)number(q,1),(int)number(q+1,1),(int)number(q+2,1),(int)number(q+3,1),(int)number(q+8,4)};
    }
    int mobileRoute(byte[] raw) throws Exception {
        frame(Arrays.copyOf(raw,Math.min(raw.length,8192)),0,raw.length,"");role("mobile-route");
        if(number(B+512,1)==254)throw new IOException("Usa memoria guarda CLAVE 0|1; memoria corrige CLAVE 0|1; memoria consulta CLAVE; memoria estado; qchat TEXTO");
        return (int)number(B+512,1);
    }
    boolean qchatNeedsPrevious(String prompt) throws Exception {
        byte[] raw=utf8(String.join(" ",QuantumText.words(prompt)));
        frame(raw,0,raw.length,"");role("qchat-context");return number(B+516,1)==1;
    }
    String stream(byte[] raw,int mode) throws Exception {
        ByteArrayOutputStream all=new ByteArrayOutputStream();if(mode==3)all.write(utf8("Resumen extractivo: "));
        StringBuilder b=new StringBuilder();put(b,B+76,0,4);put(b,B+80,0,1);put(b,B+83,0,1);frame(new byte[0],0,raw.length,b.toString());
        for(int offset=0;offset<raw.length;offset+=8192){
            frame(Arrays.copyOfRange(raw,offset,Math.min(offset+8192,raw.length)),offset,raw.length,"");
            all.write(speech(role("stream"),false));if(all.size()>1048576)throw new IOException("Respuesta demasiado larga");
        }return text(all.toByteArray());
    }
    String record(byte[] old,int count,int revision) throws Exception {
        StringBuilder b=new StringBuilder();put(b,B+20,count,4);put(b,B+24,revision,4);put(b,B+36,1048576,4);put(b,B+28,old==null?0:1,1);
        data(b,RECORD,old==null?new byte[640]:old);frame(new byte[0],0,0,b.toString());return text(speech(role("record"),false));
    }
    String reason(byte[] raw) throws Exception {
        if(raw.length>640)return null;frame(raw,0,raw.length,"");String response=text(speech(role("reason"),false));
        return number(REASON+6,1)==0 && number(REASON+7,1)==1 && number(REASON+2,1)==0 && number(REASON,1)>0 && number(REASON,1)<5 ? response:null;
    }
    String compose(byte[] raw) throws Exception {
        if(raw.length>768)return null;frame(raw,0,raw.length,"");String response=text(speech(role("compose"),false));
        return number(COMPOSE,1)==1?response:null;
    }
    String paraphrase(byte[] raw) throws Exception {
        if(raw.length>512)return null;frame(raw,0,raw.length,"");String response=text(speech(role("paraphrase"),false));
        return number(PARAPHRASE,1)==1?response:null;
    }
    int[] context(byte[] raw,JSONArray rows) throws Exception {
        if(raw.length>256)return new int[]{0,0};StringBuilder b=new StringBuilder();put(b,CONTEXT+3,rows.length(),1);
        for(int i=0;i<rows.length();i++){byte[] v=utf8(rows.getJSONObject(i).getString("utterance"));put(b,CONTEXT+32+2*i,v.length,2);data(b,CONTEXT+4096+512*i,v);}
        frame(raw,0,raw.length,b.toString());role("context");int mode=(int)number(CONTEXT,1),slot=(int)number(CONTEXT+1,1);
        if(mode>9||slot>rows.length()||((mode==1||mode==2||mode==5||mode==9)&&slot<1))throw new IOException("Selección de contexto inválida");
        return new int[]{mode,slot};
    }
    static byte[] speech(String events,boolean legacy) throws Exception {
        ByteArrayOutputStream out=new ByteArrayOutputStream();
        for(String line:events.split("\n")) if(line.startsWith("{")) {
            JSONObject e=new JSONObject(line);String r=e.optString("register");
            if(e.optString("type").equals("register")&&(r.equals("r14")||(legacy&&r.equals("r9")))) {
                long v=e.getLong("value");if(v<0||v>255||out.size()>=1048576)throw new IOException("Byte de salida inválido");out.write((int)v);
            }
        }return out.toByteArray();
    }
    static JSONObject metrics(String events) throws Exception {
        JSONObject all=new JSONObject();for(String line:events.split("\n"))if(line.startsWith("{")){
            JSONObject e=new JSONObject(line);if(e.optString("type").equals("metric")){double v=e.getDouble("value");if(!Double.isFinite(v))throw new IOException("Métrica no finita");all.put(e.getString("name"),v);}
        }return all;
    }
    @Override public void close(){session.close();}
}
