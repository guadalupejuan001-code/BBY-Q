package com.bbyq.personal;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.util.AtomicFile;
import com.reversepc.os.NativeRuntime;
import com.reversepc.os.ResultPacket;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.GZIPInputStream;

/** Android transport for the existing XI chat and V3 models. No Java language model. */
public final class PersonalEngine {
 private static PersonalEngine instance;
 public static synchronized PersonalEngine get(Context c)throws Exception {
  if(instance==null)instance=new PersonalEngine(c.getApplicationContext());
  return instance;
 }
 private final Context context;
 private final AtomicFile conversation,quantum;
 private final SQLiteDatabase history;
 private final Map<String,byte[]> cache=new HashMap<>();
 private final JSONObject manifest;
 private static final long F=9100000000000200000L,C=F+256,A=8140000000000000000L;
 public PersonalEngine(Context c)throws Exception {
  context=c;
  File dir=new File(c.getFilesDir(),"bbyq-personal");if(!dir.exists()&&!dir.mkdirs())throw new IOException("No se pudo abrir tu memoria");
  conversation=new AtomicFile(new File(dir,"conversation.rvp"));
  quantum=new AtomicFile(new File(dir,"quantum-v3.rvp"));
  history=SQLiteDatabase.openOrCreateDatabase(new File(dir,"history.sqlite"),null);
  history.execSQL("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,role TEXT NOT NULL,text TEXT NOT NULL,created INTEGER NOT NULL)");
  manifest=new JSONObject(new String(raw("engine/manifest.json"),StandardCharsets.UTF_8));
 }
 private byte[] raw(String name)throws IOException {
  try(InputStream in=context.getAssets().open(name);ByteArrayOutputStream out=new ByteArrayOutputStream()){
   byte[] b=new byte[16384];int n;
   while((n=in.read(b))!=-1){if(out.size()+n>32*1024*1024)throw new IOException("Activo demasiado grande");out.write(b,0,n);}
   return out.toByteArray();
  }
 }
 public static String hash(byte[] b)throws Exception {
  byte[] d=MessageDigest.getInstance("SHA-256").digest(b);StringBuilder s=new StringBuilder();
  for(byte v:d)s.append(String.format(Locale.ROOT,"%02x",v&255));return s.toString();
 }
 private byte[] asset(String name)throws Exception {
  if(!cache.containsKey(name)){
   byte[] b=raw("engine/"+name);
   if(!hash(b).equals(manifest.getJSONObject("files").getString(name)))throw new IOException("El archivo del motor no coincide: "+name);
   cache.put(name,b);
  }return cache.get(name);
 }
 private byte[] seed(String name)throws Exception {
  try(GZIPInputStream in=new GZIPInputStream(new ByteArrayInputStream(asset(name)));ByteArrayOutputStream out=new ByteArrayOutputStream()){
   byte[] b=new byte[16384];int n;while((n=in.read(b))!=-1){if(out.size()+n>32*1024*1024)throw new IOException("Memoria demasiado grande");out.write(b,0,n);}
   return out.toByteArray();
  }
 }
 private byte[] read(AtomicFile file,String name)throws Exception {
  if(!file.getBaseFile().exists()&&!new File(file.getBaseFile().getPath()+".bak").exists()){
   byte[] state=seed(name);NativeRuntime.inspect(state);commit(file,state);return state;
  }return file.readFully();
 }
 private void commit(AtomicFile f,byte[] state)throws Exception {
  NativeRuntime.inspect(state);FileOutputStream out=null;
  try{out=f.startWrite();out.write(state);f.finishWrite(out);}catch(Exception e){if(out!=null)f.failWrite(out);throw e;}
 }
 private ResultPacket xi(byte[] state,String source){return ResultPacket.parse(NativeRuntime.execute(state,source));}
 private ResultPacket role(byte[] state,String name)throws Exception {
  byte[] data=asset(name);return name.endsWith(".rxe")?ResultPacket.parse(NativeRuntime.executeRxe(state,data)):xi(state,new String(data,StandardCharsets.UTF_8));
 }
 private static int memoryByte(byte[] state,long address)throws IOException {
  if(state.length<29)throw new IOException("Memoria incompleta");
  long n=ByteBuffer.wrap(state).order(ByteOrder.LITTLE_ENDIAN).getLong(5);
  if(n<0||n>state.length-29)throw new IOException("Memoria inválida");
  byte[] needle=("O "+address+" ").getBytes(StandardCharsets.US_ASCII);int begin=29+(int)n;
  outer:for(int i=begin;i+needle.length<state.length;i++){
   if(i>begin&&state[i-1]!=10)continue;
   for(int j=0;j<needle.length;j++)if(state[i+j]!=needle[j])continue outer;
   int value=0,j=i+needle.length;
   while(j<state.length&&state[j]>=48&&state[j]<=57){value=value*10+state[j++]-48;if(value>255)throw new IOException("Byte inválido");}
   return value;
  }return 0;
 }
 private static String speech(String output)throws Exception {
  ByteArrayOutputStream bytes=new ByteArrayOutputStream();
  for(String line:output.split("\n")){
   if(!line.startsWith("{"))continue;JSONObject e=new JSONObject(line);
   if(e.optString("type").equals("register")&&Arrays.asList("r14","r9").contains(e.optString("register"))){
    int v=e.getInt("value");if(v<0||v>255||bytes.size()>65536)throw new IOException("Respuesta inválida");bytes.write(v);
   }
  }
  if(bytes.size()==0)throw new IOException("El motor no produjo respuesta");
  return StandardCharsets.UTF_8.newDecoder().onMalformedInput(java.nio.charset.CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes.toByteArray())).toString();
 }
 public synchronized String chat(String message)throws Exception {
  byte[] input=message.getBytes(StandardCharsets.UTF_8);
  if(input.length==0||input.length>16384)throw new IOException("Escribe entre 1 y 16.384 bytes de texto");
  byte[] state=read(conversation,"chat-model.rvp.gz");
  state=role(state,"guard.xi").state;
  StringBuilder frame=new StringBuilder("#!reverse-pc-machine-v1\n");
  frame.append("store8 ").append(F+2).append(" 1\nstore8 ").append(F+3).append(" 0\nstore8 ").append(F+4).append(" 1\n");
  frame.append("store8 ").append(F+8).append(" ").append(input.length&255).append("\nstore8 ").append(F+9).append(" ").append(input.length>>8).append("\nstore8 ").append(F+10).append(" 0\n");
  for(int i=0;i<input.length;i++)frame.append("store8 ").append(C+i).append(" ").append(input[i]&255).append("\n");
  state=xi(state,frame.append("halt\n").toString()).state;
  ResultPacket result=role(state,"front.rxe");
  if(memoryByte(result.state,9120000000000000002L)==0)result=role(result.state,"code.rxe");
  if(memoryByte(result.state,F+3)==3)throw new IOException("Este mensaje no es compatible con el módulo solicitado");
  if(memoryByte(result.state,F+2)!=0)throw new IOException("El motor no consumió la entrada");
  String response=speech(result.output);
  if(memoryByte(result.state,9090000000000000002L)==2)response+="\n\nLa ejecución de tareas de escritorio aún no está disponible en esta versión móvil.";
  byte[] finished=role(result.state,"text-finish.xi").state;
  commit(conversation,finished);
  history.beginTransaction();try{
   history.execSQL("INSERT INTO messages(role,text,created) VALUES(?,?,?)",new Object[]{"user",message,System.currentTimeMillis()});
   history.execSQL("INSERT INTO messages(role,text,created) VALUES(?,?,?)",new Object[]{"assistant",response,System.currentTimeMillis()});
   history.setTransactionSuccessful();
  }finally{history.endTransaction();}
  return response;
 }
 public synchronized JSONArray messages(){
  JSONArray all=new JSONArray();
  try(Cursor c=history.rawQuery("SELECT role,text FROM (SELECT id,role,text FROM messages ORDER BY id DESC LIMIT 100) ORDER BY id",null)){
   while(c.moveToNext())try{all.put(new JSONObject().put("role",c.getString(0)).put("text",c.getString(1)));}catch(Exception ignored){}
  }return all;
 }
 public synchronized String exportHistory(){
  StringBuilder all=new StringBuilder("BBY Q · X\n\n");
  try(Cursor c=history.rawQuery("SELECT role,text FROM messages ORDER BY id",null)){
   while(c.moveToNext())all.append(c.getString(0).equals("user")?"X":"BBY Q").append(": ").append(c.getString(1)).append("\n\n");
  }return all.toString();
 }
 private String library()throws Exception{return new String(asset("v3-common.xi"),StandardCharsets.UTF_8)+"\n"+new String(asset("v3-benchmarks.xi"),StandardCharsets.UTF_8)+"\n"+new String(asset("v3-qrl3.xi"),StandardCharsets.UTF_8);}
 private ResultPacket quantum(byte[] state,String body)throws Exception{return xi(state,"#!reverse-pc-machine-v1\nbudget 10000000\n"+body+"\nhalt\n"+library());}
 private static JSONObject metrics(String text)throws Exception{
  JSONObject out=new JSONObject();
  for(String line:text.split("\n"))if(line.startsWith("{")){JSONObject e=new JSONObject(line);if(e.optString("type").equals("metric"))out.put(e.getString("name"),e.getDouble("value"));}
  return out;
 }
 public synchronized JSONObject quantumStatus()throws Exception{
  byte[] state=read(quantum,"quantum-model.rvp.gz");
  StringBuilder body=new StringBuilder("load8 r0 "+(A+1000)+"\ncmp r0 173\nje valid_model\ndiv r0 0\nlabel valid_model\n");
  for(int r=0;r<2;r++)body.append("load64 r0 ").append(A+(r==0?4000:5000)).append("\nitof f0 r0\nfemit ").append(r==0?"vqc_episodes":"qrl_episodes").append(" f0\n");
  JSONObject data=metrics(quantum(state,body.toString()).output);
  data.put("qubits_per_agent",1000);data.put("backend","XI/Ether nativo · sin MPS");return data;
 }
 public synchronized JSONObject quantumAction()throws Exception{
  byte[] state=read(quantum,"quantum-model.rvp.gz");
  String body="store64 "+(A+344)+" 3\nstore64 "+(A+352)+" 6\nstore64 "+(A+360)+" 0\nstore64 "+(A+312)+" 12\nstore64 "+(A+320)+" 2\ncall qrl_observe\n";
  body+=new String(asset("v3-qrl3-act.xi"),StandardCharsets.UTF_8).replaceFirst("^#!reverse-pc-machine-v1\\n","");
  return metrics(quantum(state,body.replace("\nhalt\n","\n")).output);
 }
 public synchronized JSONObject trainEpisode()throws Exception {
  byte[] state=read(quantum,"quantum-model.rvp.gz");
  ResultPacket result=quantum(state,"fstore "+(A+304)+" .15\nstore64 "+(A+312)+" 12\nstore64 "+(A+320)+" 0\nstore64 "+(A+328)+" 0\nstore64 "+(A+336)+" 0\ncall qrl_episode");
  commit(quantum,result.state);return quantumStatus();
 }
 public synchronized String stateHash()throws Exception{return hash(read(conversation,"chat-model.rvp.gz"));}
}
