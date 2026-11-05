package com.bbyq.personal;

import android.content.*;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.json.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.Pattern;
import static org.junit.Assert.*;

/** Frozen product assessment: records failures without changing product logic. */
@RunWith(AndroidJUnit4.class)
public class CapabilityAuditTest {
 private final JSONArray cases=new JSONArray();
 private static String fold(String s){return Normalizer.normalize(s.toLowerCase(Locale.ROOT),Normalizer.Form.NFD).replaceAll("\\p{M}","");}
 private Context base(){return InstrumentationRegistry.getInstrumentation().getTargetContext();}
 private Context isolated()throws Exception {Context b=base();File root=new File(b.getCacheDir(),"capability-"+System.nanoTime());assertTrue(root.mkdirs());return new ContextWrapper(b){@Override public File getFilesDir(){return root;}};}
 private void check(String id,String group,String[] setup,String input,String mode,String expected)throws Exception {
  JSONObject row=new JSONObject().put("id",id).put("group",group).put("setup",new JSONArray(Arrays.asList(setup))).put("input",input).put("mode",mode).put("expected",expected);long started=System.nanoTime();
  try(PersonalEngine e=new PersonalEngine(isolated())){
   for(String text:setup)e.chat(text);
   try{
    JSONObject r=e.testTurn("audit",input,false);String answer=r.getString("response");row.put("engine",r.optString("engine")).put("response",answer).put("status",r.optInt("status",-99));boolean passed;
    if(mode.equals("status"))passed=r.optInt("status",-99)==Integer.parseInt(expected);
    else if(mode.equals("number"))passed=Pattern.compile("(?<![0-9])"+Pattern.quote(expected)+"(?![0-9])").matcher(answer).find();
    else if(mode.equals("exact"))passed=answer.equals(expected);
    else if(mode.equals("lines"))passed=answer.trim().split("\\n").length==Integer.parseInt(expected);
    else if(mode.equals("error"))passed=false;
    else passed=fold(answer).contains(fold(expected));
    row.put("passed",passed).put("explicit_abstention",fold(answer).matches("(?s).*(necesito|no tengo|no puedo|falta|no se|no encontre|no dispongo).*"));
   }catch(Exception failure){row.put("exception",failure.getClass().getSimpleName()+": "+failure.getMessage()).put("passed",mode.equals("error"));}
  }catch(Exception setupFailure){row.put("setup_error",setupFailure.toString()).put("passed",false);}
  row.put("elapsed_ms",(System.nanoTime()-started)/1e6);cases.put(row);
 }
 @Test public void measureCurrentCapabilitiesWithoutChangingTheProduct()throws Exception {
  String[] empty={};
  check("rule-new-name","reasoning",new String[]{"recuerda que alda es humana","aprende regla: si $x es humana entonces $x es mortal"},"¿alda es mortal?","status","1");
  check("why-proof","reasoning",new String[]{"recuerda que alda es humana","aprende regla: si $x es humana entonces $x es mortal"},"por que alda es mortal","contains","alda es humana");
  check("relational-join","reasoning",empty,"resuelve:\nsira tiene dinamo\ndinamo requiere energia\nsi $x tiene $y y $y requiere $z entonces $x necesita $z\n¿sira necesita energia?","status","1");
  check("negative","reasoning",new String[]{"recuerda que alda no es activa"},"¿alda es activa?","status","-1");
  check("conflict","reasoning",new String[]{"recuerda que alda es activa","recuerda que alda no es activa"},"¿alda es activa?","status","2");
  check("withdraw-rule","reasoning",new String[]{"recuerda que alda es humana","aprende regla: si $x es humana entonces $x es mortal","olvida regla: si $x es humana entonces $x es mortal"},"¿alda es mortal?","status","0");
  check("unknown","reasoning",empty,"¿alda es activa?","status","0");
  check("ambiguous-pronoun","context",empty,"¿ella es mortal?","status","5");
  check("clear-stale-context","context",new String[]{"recuerda que alda es mortal","Mi proyecto se llama Neral."},"¿ella es mortal?","status","5");
  check("named-history","context",new String[]{"Mi nave se llama Orenda."},"¿qué dije sobre Orenda?","contains","Mi nave se llama Orenda");
  check("arithmetic-composed","tools",empty,"calcula (31 + 47) * 6 - 12 / 3","number","464");
  check("arithmetic-negative","tools",empty,"calcula -(11+5) * 3","number","-48");
  check("divide-zero","tools",empty,"calcula 13 / 0","error","");
  check("unsafe-rule","reasoning",empty,"aprende regla: si $x es humana entonces $y es mortal","error","");
  StringBuilder route=new StringBuilder("resuelve:\n");for(int i=0;i<12;i++)route.append("sitio").append(i).append(" conecta sitio").append(i+1).append('\n');route.append("ruta desde sitio0 hasta sitio12");
  check("route-13-nodes","planning",empty,route.toString(),"contains","Pasos: 12");
  check("missing-route","planning",empty,"ruta desde sitio0 hasta sitio12","status","0");
  check("missing-goal-visible","cooperation",empty,"resuelve:\n¿alda es activa?\ncalcula 17+26","status","0");
  check("memory-one","memory",new String[]{"memoria guarda baliza 1"},"recupera baliza","contains","baliza es uno");
  check("memory-correction","memory",new String[]{"memoria guarda baliza 1","memoria corrige baliza 0"},"recupera baliza","contains","baliza es cero");
  check("missing-memory","memory",empty,"recupera baliza","status","0");
  check("lesson-bridge","memory",new String[]{"aprende: dinamo\ndefinición: un generador\nrequiere: energia\nfuente: X\npáginas: 1","aprende regla: si $x requiere energia entonces $x es activo"},"¿dinamo es activo?","status","1");
  check("specialist-projection","cooperation",new String[]{"memoria guarda faro 1"},"resuelve:\nrecupera faro\nobserva senal muestra 1763814988\nsi faro es uno y senal es clase0 entonces proyecto es autorizado\n¿proyecto es autorizado?","status","1");
  check("delegated-tools","cooperation",empty,"resuelve:\nconsulta qchat hola\ncalcula 73+19","number","92");
  check("qchat-known","language-model",empty,"qchat hola","exact","Hola X.");
  check("qchat-definition","language-model",empty,"qchat que es memoria","contains","La memoria conserva información");
  check("qchat-unknown","language-model",empty,"qchat que es quasar","contains","Necesito más ejemplos para aprender");
  check("qchat-followup","language-model",new String[]{"qchat que es circuito"},"qchat dime mas","contains","Un circuito aplica puertas");
  check("syllogism-natural","legacy-reasoning",empty,"Todos los sensores son máquinas. Elara es un sensor. ¿Elara es máquina?","contains","elara -> sensor -> maquinas");
  check("poem-four-lines","creative",empty,"Escribe un poema de cuatro versos sobre una guitarra.","lines","4");
  check("poem-paraphrase","creative",empty,"hazme un poema sobre una guitarra","contains","guitarra");
  check("exact-unicode","text",empty,"repite exactamente:\nÓrbita 🎸 137","exact","Órbita 🎸 137");
  // The following are completion probes, not a claim that unrestricted Spanish
  // is supported. Safe refusal is recorded separately from solving the task.
  check("natural-multiplication","open-language",empty,"Tengo 137 cajas con 24 piezas cada una. ¿Cuántas piezas tengo en total?","number","3288");
  check("natural-change","open-language",empty,"Si pago 50 dólares por algo que cuesta 17, ¿cuánto cambio recibo?","number","33");
  check("natural-quantity","open-language",empty,"Había 28 libros y presté 9. Dime cuántos quedan.","number","19");
  check("natural-chain","open-language",new String[]{"recuerda que alda es humana","aprende regla: si $x es humana entonces $x es mortal"},"Con lo que acabas de aprender, dime si alda pertenece a los mortales.","contains","alda es mortal");
  check("natural-multiword-name","open-language",new String[]{"Recuerda que mi nave se llama Luz del Sur."},"¿Cómo se llama mi nave?","contains","Luz del Sur");
  check("natural-route","open-language",empty,"La casa está conectada al parque y el parque a la tienda. Explícame cómo llegar de casa a tienda.","contains","casa → parque → tienda");
  check("natural-two-tools","open-language",empty,"Salúdame y después calcula cuánto es 137 por 24.","number","3288");
  check("natural-correction","open-language",new String[]{"recuerda que alda es activa","Me equivoqué antes: alda ya no está activa. Corrige ese dato."},"¿alda es activa?","status","-1");
  check("mixed-unspecified-format","open-language",empty,"hola\ncalcula 73+19","number","92");
  check("fact-after-correction","reasoning",new String[]{"recuerda que alda es activa","corrige que alda no es activa"},"¿alda es activa?","status","-1");
  check("arithmetic-in-qchat-only","open-language",empty,"qchat calcula 137 por 24","number","3288");
  JSONObject groups=new JSONObject();int passed=0;for(int i=0;i<cases.length();i++){JSONObject r=cases.getJSONObject(i);String g=r.getString("group");JSONObject x=groups.optJSONObject(g);if(x==null){x=new JSONObject().put("passed",0).put("total",0);groups.put(g,x);}x.put("total",x.getInt("total")+1);if(r.getBoolean("passed")){passed++;x.put("passed",x.getInt("passed")+1);}}
  JSONObject report=new JSONObject().put("protocol","BBYQ-0-AUDIT-20261105-1").put("base_commit","6a6a66b301ab6efe1208791f675a18358179e2d6").put("scope","42 descriptive product probes; exact outputs/status and simple completion checks, not an AGI score").put("passed",passed).put("total",cases.length()).put("groups",groups).put("cases",cases);
  assertEquals(42,cases.length());File output=new File(base().getFilesDir(),"BBYQ-capability-audit.json");try(FileOutputStream stream=new FileOutputStream(output)){stream.write(report.toString(2).getBytes(StandardCharsets.UTF_8));}assertTrue(output.length()>1000);
 }
}
