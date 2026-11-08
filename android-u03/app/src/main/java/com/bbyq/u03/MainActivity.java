package com.bbyq.u03;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.*;
import org.json.JSONObject;
import org.json.JSONArray;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.atomic.AtomicBoolean;

/** UI actions are connected to their actual U03 modules, not merely source files. */
public final class MainActivity extends Activity {
 private static final int BG=0xff10151e,PANEL=0xff1b2632,INK=0xffeff8f7,MUTED=0xff9db3c0,ACCENT=0xff70e0c5;
 private static final ExecutorService WORK=Executors.newSingleThreadExecutor();
 private static final AtomicBoolean BUSY=new AtomicBoolean();
 private TextView status;private EditText input;private Button send;private LinearLayout log;private ScrollView scroll;
 private volatile boolean ready=false;
 private int dp(float x){return Math.round(x*getResources().getDisplayMetrics().density);}
 private GradientDrawable shape(int color){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(15));return d;}
 private LinearLayout col(){LinearLayout x=new LinearLayout(this);x.setOrientation(LinearLayout.VERTICAL);return x;}
 private TextView text(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
 private Button button(String s){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(12);b.setTextColor(INK);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PANEL));return b;}
 private void ui(Runnable r){runOnUiThread(()->{if(!isDestroyed())r.run();});}
 @Override public void onCreate(Bundle state){
  super.onCreate(state);getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
  LinearLayout root=col();root.setBackgroundColor(BG);root.setPadding(dp(14),dp(12),dp(14),dp(12));root.setFitsSystemWindows(true);
  LinearLayout head=new LinearLayout(this);head.setGravity(Gravity.CENTER_VERTICAL);
  LinearLayout label=col();TextView title=text("BBY Q U03",24,INK);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);label.addView(title);label.addView(text("XI / Ether · integración ejecutable",12,MUTED));
  head.addView(label,new LinearLayout.LayoutParams(0,-2,1));Button menu=button("Herramientas");menu.setId(0x5801010);head.addView(menu);menu.setOnClickListener(v->menu());root.addView(head);
  status=text("Verificando bibliotecas y checkpoints…",12,MUTED);status.setPadding(0,dp(10),0,dp(8));status.setId(0x5801001);root.addView(status);
  scroll=new ScrollView(this);log=col();scroll.addView(log);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  LinearLayout shortcuts=new LinearLayout(this);
  for(String name:new String[]{"Misión","Memoria","Planificar","Aprendizaje"}){
   Button b=button(name);shortcuts.addView(b,new LinearLayout.LayoutParams(0,dp(46),1));
   b.setOnClickListener(v->{if(name.equals("Misión"))input.setText("guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3");else if(name.equals("Memoria"))action("MEMORY","{}",false);else if(name.equals("Planificar"))planForm();else learningMenu();});
  }
  root.addView(shortcuts);
  LinearLayout composer=new LinearLayout(this);composer.setGravity(Gravity.CENTER_VERTICAL);composer.setBackground(shape(PANEL));composer.setPadding(dp(7),dp(4),dp(5),dp(4));
  input=new EditText(this);input.setId(0x5801002);input.setTextColor(INK);input.setHintTextColor(MUTED);input.setHint("Escribe una petición para XI…");input.setTextSize(15);input.setMaxLines(5);input.setMinLines(1);input.setBackgroundColor(Color.TRANSPARENT);
  composer.addView(input,new LinearLayout.LayoutParams(0,-2,1));send=button("Enviar");send.setId(0x5801003);send.setTextColor(BG);send.setBackgroundTintList(android.content.res.ColorStateList.valueOf(ACCENT));send.setOnClickListener(v->send());composer.addView(send,new LinearLayout.LayoutParams(dp(85),dp(48)));root.addView(composer);setContentView(root);send.setEnabled(false);
  if(state!=null)input.setText(state.getString("draft",""));
  bubble("Sistema","La conversación y memoria usan una sesión U03. Los candidatos se pueden ejecutar en el laboratorio sin reemplazar tu modelo ni tus datos.",false);
  WORK.execute(()->{
   try{
    JSONObject result=U03Runtime.start(getApplicationContext());ready=true;
    JSONArray history=new JSONArray(U03Runtime.history(getApplicationContext()));
    ui(()->{status.setText("● Siete bancos XI verificados · módulos conectados");status.setTextColor(ACCENT);send.setEnabled(!BUSY.get());bubble("BBY Q","Listo. Historial conservado: "+history.length()+" recibos recientes. Herramientas permite ejecutar cada ciclo y ver su evidencia.",false);});
   }catch(Throwable error){error("Inicio U03",error);}
  });
 }
 @Override protected void onSaveInstanceState(Bundle b){b.putString("draft",input.getText().toString());super.onSaveInstanceState(b);}
 private void bubble(String who,String message,boolean user){
  LinearLayout box=col();box.setPadding(dp(12),dp(10),dp(12),dp(10));box.setBackground(shape(user?0xff29404a:PANEL));TextView title=text(who,12,user?ACCENT:MUTED);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);box.addView(title);
  TextView body=text(message,15,INK);body.setTextIsSelectable(true);body.setPadding(0,dp(4),0,0);box.addView(body);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(user?dp(28):0,dp(8),user?0:dp(18),dp(4));log.addView(box,p);scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));
 }
 private void error(String where,Throwable t){ui(()->{status.setText(where+": no verificado");status.setTextColor(0xffff9898);bubble("Error real",String.valueOf(t)+"\nAbre Herramientas → Diagnóstico para copiar la causa completa.",false);});}
 private boolean begin(String name){if(!ready){bubble("Sistema","El núcleo aún no está disponible. El diagnóstico de bibliotecas sigue accesible.",false);return false;}if(!BUSY.compareAndSet(false,true)){bubble("Sistema","Hay una operación XI en curso; no iniciaré otra sobre tu memoria.",false);return false;}send.setEnabled(false);status.setText("Ejecutando "+name+"…");return true;}
 private void end(){BUSY.set(false);ui(()->{send.setEnabled(ready);status.setText("● U03 disponible · sin conexión a internet");});}
 private void send(){String prompt=input.getText().toString().trim();if(prompt.isEmpty()||!begin("turno XI"))return;input.setText("");bubble("Tú",prompt,true);String id=UUID.randomUUID().toString();WORK.execute(()->{try{JSONObject r=U03Runtime.turn(getApplicationContext(),id,prompt,"");ui(()->bubble("BBY Q · XI",r.optString("reply"),false));}catch(Throwable e){error("Turno",e);}finally{end();}});}
 private void report(String title,String content){
  ScrollView pane=new ScrollView(this);TextView body=text(content,13,INK);body.setTextIsSelectable(true);body.setPadding(dp(16),dp(12),dp(16),dp(12));pane.setBackgroundColor(BG);pane.addView(body);
  new AlertDialog.Builder(this).setTitle(title).setView(pane).setPositiveButton("Cerrar",null).setNeutralButton("Copiar evidencia",(d,w)->((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE)).setPrimaryClip(ClipData.newPlainText(title,content))).show();
 }
 private void action(String name,String payload,boolean confirm){
  if(confirm){new AlertDialog.Builder(this).setTitle("Laboratorio "+name).setMessage("Esta prueba ejecuta XI en copias privadas. Puede usar CPU y almacenamiento. No reemplaza tu modelo ni escribe en tu memoria personal. El informe conservará los fallos reales.").setNegativeButton("Cancelar",null).setPositiveButton("Ejecutar",(d,w)->action(name,payload,false)).show();return;}
  if(!begin(name))return;
  WORK.execute(()->{try{JSONObject result=U03Runtime.action(getApplicationContext(),name,payload);String value=result.toString(2);ui(()->{bubble("Ciclo "+name,"Ejecución terminada. Consulta la evidencia; terminar no implica mejorar la precisión.",false);report(name+" · resultado real",value);});}catch(Throwable e){error(name,e);}finally{end();}});
 }
 private void learningMenu(){new AlertDialog.Builder(this).setTitle("Aprendizaje").setItems(new String[]{"Feedback de mi última tarea (sesión personal)","C11: entrenar y auditar copia aislada","C12: cooperación y comparación aislada"},(d,w)->{if(w==0)new AlertDialog.Builder(this).setTitle("Feedback explícito").setMessage("El motor original actualizará los parámetros de tu última tarea cuando disponga de supervisión verificada. Esto sí modifica tu sesión personal.").setNegativeButton("Cancelar",null).setPositiveButton("Preparar feedback",(x,y)->input.setText("aprende de la última tarea")).show();else action(w==1?"C11":"C12","{}",true);}).show();}
 private void planForm(){
  LinearLayout form=col();form.setPadding(dp(16),0,dp(16),0);EditText observation=new EditText(this),association=new EditText(this),position=new EditText(this);observation.setHint("Observación existente");observation.setText("Nara");association.setHint("Regla existente");association.setText("Faro Azul");position.setHint("Posición de la tarea (0–6)");position.setText("3");form.addView(observation);form.addView(association);form.addView(position);
  new AlertDialog.Builder(this).setTitle("C10 · Plan nativo desde C09").setView(form).setNegativeButton("Cancelar",null).setPositiveButton("Planificar",(d,w)->{try{JSONObject p=new JSONObject().put("observation",observation.getText().toString()).put("association",association.getText().toString()).put("position",Integer.parseInt(position.getText().toString()));action("PLAN",p.toString(),false);}catch(Exception e){error("Datos del plan",e);}}).show();
 }
 private void evidenceForm(){
  EditText editor=new EditText(this);editor.setText("{\"query\":{\"subject\":\"Componente\",\"predicate\":\"operativo\"},\"evidence\":[]}");editor.setMinLines(5);
  new AlertDialog.Builder(this).setTitle("C07/C08 · Evidencia tipada").setMessage("Esquema experimental, no una comprobación de verdad general. Sin evidencia debe abstenerse.").setView(editor).setNegativeButton("Cancelar",null).setNeutralButton("Ejemplo sintético",(d,w)->action("EVIDENCE_DEMO","{}",false)).setPositiveButton("Evaluar",(d,w)->action("EVIDENCE",editor.getText().toString(),false)).show();
 }
 private void menu(){
  String[] items={"Estado y funciones realmente conectadas","Diagnóstico de bibliotecas (sin Python)","C01 · Comparar transporte XI","C02 · Persistencia optimista","C06 · Analizar el texto del editor","C07/C08 · Evidencia y preguntas","C09 · Inspeccionar memoria","C10 · Planificar","C11/C12 · Aprendizaje aislado","C13 · Comparar caché experimental","C14 · Ejecutar ablaciones","C15 · Estrés y recuperación móvil","Auditar 159 archivos","Última evidencia","Panel histórico C00–C17"};
  new AlertDialog.Builder(this).setTitle("Ciclos U03").setItems(items,(d,w)->{
   if(w==1){report("Diagnóstico JNI",U03Runtime.diagnostics(this).toString());return;}
   if(w==2||w==3||w==9||w==10||w==11){action(w==2?"C01":w==3?"C02":w==9?"C13":w==10?"C14":"C15","{}",true);return;}
   if(w==4){try{action("SEMANTIC",new JSONObject().put("prompt",input.getText().toString()).toString(),false);}catch(Exception e){error("Semántica",e);}return;}
   if(w==5){evidenceForm();return;}if(w==6){action("MEMORY","{}",false);return;}if(w==7){planForm();return;}if(w==8){learningMenu();return;}if(w==12){action("AUDIT","{}",false);return;}
   WORK.execute(()->{try{String value=w==0?U03Runtime.status(getApplicationContext()).toString(2):w==13?U03Runtime.lastReport(getApplicationContext()):U03Runtime.panel(getApplicationContext());ui(()->report(items[w],value));}catch(Throwable e){error(items[w],e);}});
  }).show();
 }
}
