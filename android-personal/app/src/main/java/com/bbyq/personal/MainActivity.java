package com.bbyq.personal;

import android.app.*;
import android.os.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.content.*;
import android.view.*;
import android.view.inputmethod.InputMethodManager;
import android.widget.*;
import android.text.InputType;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;

public final class MainActivity extends Activity {
 private static final int BG=0xff101419,PANEL=0xff1a222b,INK=0xffeef5f5,MUTED=0xffa1afb9,ACCENT=0xff72dbc8;
 private static final ExecutorService WORK=Executors.newSingleThreadExecutor();
 private static final AtomicBoolean BUSY=new AtomicBoolean();
 private LinearLayout messages;
 private ScrollView scroll;
 private EditText input;
 private Button send;
 private TextView status;
 private PersonalEngine engine;
 private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
 private TextView text(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
 private GradientDrawable shape(int color,int radius){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(radius));return g;}
 private LinearLayout vertical(){LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);return v;}
 private Button button(String title){Button b=new Button(this);b.setText(title);b.setAllCaps(false);b.setTextSize(13);b.setTextColor(INK);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PANEL));return b;}
 @Override public void onCreate(Bundle saved){
  super.onCreate(saved);
  getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
  LinearLayout root=vertical();root.setBackgroundColor(BG);root.setPadding(dp(16),dp(12),dp(16),dp(12));
  if(Build.VERSION.SDK_INT>=30){
   getWindow().setDecorFitsSystemWindows(false);
   root.setOnApplyWindowInsetsListener((v,insets)->{
    android.graphics.Insets bars=insets.getInsets(WindowInsets.Type.systemBars()),ime=insets.getInsets(WindowInsets.Type.ime());
    v.setPadding(dp(16)+bars.left,dp(10)+bars.top,dp(16)+bars.right,dp(10)+Math.max(bars.bottom,ime.bottom));return insets;
   });
  }else{root.setFitsSystemWindows(true);getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);}
  LinearLayout head=new LinearLayout(this);head.setGravity(Gravity.CENTER_VERTICAL);head.setPadding(dp(2),dp(4),dp(2),dp(10));
  TextView mark=text("Q",25,BG);mark.setTypeface(Typeface.DEFAULT,Typeface.BOLD);mark.setGravity(Gravity.CENTER);mark.setBackground(shape(ACCENT,14));head.addView(mark,new LinearLayout.LayoutParams(dp(48),dp(48)));
  LinearLayout names=vertical();names.setPadding(dp(12),0,0,0);
  TextView title=text("BBY Q",24,INK);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);names.addView(title);names.addView(text("Tu espacio, X",12,MUTED));
  head.addView(names,new LinearLayout.LayoutParams(0,-2,1));
  Button menu=button("•••");menu.setContentDescription("Opciones");head.addView(menu,new LinearLayout.LayoutParams(dp(52),dp(48)));menu.setOnClickListener(v->showMenu(menu));
  root.addView(head);
  status=text("Preparando tu memoria…",12,MUTED);status.setId(R.id.engine_status);root.addView(status,new LinearLayout.LayoutParams(-1,dp(28)));
  scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setClipToPadding(false);
  messages=vertical();messages.setId(R.id.message_list);messages.setPadding(0,dp(8),0,dp(14));scroll.addView(messages);
  root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
  LinearLayout chips=new LinearLayout(this);
  for(String label:new String[]{"Ingreso","Calcular","Enseñar"}){
   Button b=button(label);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(44),1);p.setMargins(dp(2),0,dp(2),dp(8));chips.addView(b,p);
   b.setOnClickListener(v->{if(label.equals("Enseñar")){input.setText("aprende: mi proyecto\ndefinición: escribe aquí lo que quieres recordar\nrequiere: memoria\nfuente: X\npáginas: 1");input.requestFocus();((InputMethodManager)getSystemService(INPUT_METHOD_SERVICE)).showSoftInput(input,InputMethodManager.SHOW_IMPLICIT);}else{input.setText(label.equals("Ingreso")?"que es ingreso y que requiere?":"calcula 17 + 25");sendMessage();}});
  }root.addView(chips);
  LinearLayout composer=new LinearLayout(this);composer.setGravity(Gravity.BOTTOM);composer.setPadding(dp(8),dp(4),dp(4),dp(4));composer.setBackground(shape(PANEL,22));
  input=new EditText(this);input.setId(R.id.message_input);input.setHint("Habla con BBY Q…");input.setHintTextColor(MUTED);input.setTextColor(INK);input.setTextSize(16);input.setBackgroundColor(Color.TRANSPARENT);input.setMinLines(1);input.setMaxLines(6);input.setPadding(dp(6),dp(10),dp(6),dp(10));input.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_MULTI_LINE|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
  composer.addView(input,new LinearLayout.LayoutParams(0,-2,1));
  send=button("↑");send.setId(R.id.send_button);send.setContentDescription("Enviar mensaje");send.setTextSize(25);send.setTextColor(BG);send.setBackgroundTintList(android.content.res.ColorStateList.valueOf(ACCENT));composer.addView(send,new LinearLayout.LayoutParams(dp(52),dp(52)));send.setOnClickListener(v->sendMessage());
  root.addView(composer);setContentView(root);send.setEnabled(false);
  if(saved!=null)input.setText(saved.getString("draft",""));
  WORK.execute(()->{try{engine=PersonalEngine.get(this);JSONArray history=engine.messages();runOnUiThread(()->{if(isDestroyed())return;messages.removeAllViews();if(history.length()==0)addBubble("BBY Q","Hola, X. Tu conversación, lecciones y agentes comparten esta sesión. Puedes consultar lo aprendido, enseñar una lección o guardar una asociación binaria.");else for(int i=0;i<history.length();i++){JSONObject m=history.optJSONObject(i);addBubble(m.optString("role").equals("user")?"X":"BBY Q",m.optString("text"));}send.setEnabled(!BUSY.get());status.setText("● Disponible sin conexión");status.setTextColor(ACCENT);});}catch(Exception e){showError(e);}});
 }
 private void addBubble(String role,String message){
  LinearLayout bubble=vertical();bubble.setPadding(dp(14),dp(12),dp(14),dp(12));boolean user=role.equals("X");bubble.setBackground(shape(user?0xff213c3b:PANEL,18));
  TextView label=text(role,11,user?ACCENT:MUTED);label.setTypeface(Typeface.DEFAULT,Typeface.BOLD);bubble.addView(label);
  TextView body=text(message,16,INK);body.setTextIsSelectable(true);body.setPadding(0,dp(5),0,0);bubble.addView(body);
  LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(user?dp(32):0,dp(6),user?0:dp(18),dp(6));messages.addView(bubble,p);
  scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));
 }
 private void sendMessage(){
  String message=input.getText().toString().trim();if(message.isEmpty()||engine==null||!BUSY.compareAndSet(false,true))return;
  input.setText("");send.setEnabled(false);addBubble("X",message);status.setText("Pensando…");status.setTextColor(MUTED);
  WORK.execute(()->{try{String reply=engine.chat(message);runOnUiThread(()->{if(!isDestroyed())addBubble("BBY Q",reply);});}catch(Exception e){runOnUiThread(()->{if(!isDestroyed()){if(messages.getChildCount()>0)messages.removeViewAt(messages.getChildCount()-1);input.setText(message);}});showError(e);}finally{BUSY.set(false);runOnUiThread(()->{if(!isDestroyed()){send.setEnabled(true);status.setText("● Disponible sin conexión");status.setTextColor(ACCENT);}});}});
 }
 private void showError(Exception e){runOnUiThread(()->{if(!isDestroyed()){status.setText("No se completó la operación");new AlertDialog.Builder(this).setTitle("BBY Q").setMessage(e.getMessage()).setPositiveButton("Entendido",null).show();}});}
 private void showMenu(View anchor){
  PopupMenu menu=new PopupMenu(this,anchor);for(String s:new String[]{"Qué puedo hacer","Mis agentes","Mi sesión","Exportar conversación","Acerca de"})menu.getMenu().add(s);
  menu.setOnMenuItemClickListener(item->{String s=item.getTitle().toString();
   if(s.equals("Mis agentes"))showAgents();
   else if(s.equals("Mi sesión"))WORK.execute(()->{try{if(engine==null)return;JSONObject state=engine.sessionStatus();runOnUiThread(()->{if(!isDestroyed())new AlertDialog.Builder(this).setTitle("Tu sesión").setMessage("Lecciones: "+state.optInt("lessons")+"\nTurnos confirmados: "+state.optLong("generation")+"\nAsociaciones binarias: "+state.optInt("binary_memories")+"\nIntegridad: "+state.optString("integrity")).setPositiveButton("Cerrar",null).show();});}catch(Exception e){showError(e);}});
   else if(s.equals("Exportar conversación")){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.setType("text/plain");i.addCategory(Intent.CATEGORY_OPENABLE);i.putExtra(Intent.EXTRA_TITLE,"BBYQ-X-conversacion.txt");startActivityForResult(i,71);}
   else if(s.equals("Acerca de"))new AlertDialog.Builder(this).setTitle("BBY Q · X").setMessage("Edición X10 · 2.0\nUna sesión local para conversación, lecciones, QChat100, memoria binaria y VQC3/QRL3.\nMotor XI/Ether propio. Los modelos entrenados se conservan.").setPositiveButton("Cerrar",null).show();
   else new AlertDialog.Builder(this).setTitle("Qué puedes decirle").setMessage("que es ingreso y que requiere?\n\ncalcula 17 + 25\n\n¿qué dije antes?\n\nmemoria guarda faro 1\nmemoria consulta faro\nmemoria corrige faro 0\n\nquantum v3 estado\nquantum v3 planea 3 6\n\nqchat hola\n\nPara enseñar una lección, usa Enseñar y completa sus campos.").setPositiveButton("Cerrar",null).show();return true;});menu.show();
 }
 private void showAgents(){
  if(engine==null||!BUSY.compareAndSet(false,true))return;status.setText("Leyendo los agentes…");
  WORK.execute(()->{try{JSONObject s=engine.quantumStatus();runOnUiThread(()->{
   if(isDestroyed())return;
   new AlertDialog.Builder(this).setTitle("Tus agentes")
    .setMessage("VQC3 · 1.000 cúbits\n"+s.optInt("vqc_episodes")+" ejemplos entrenados\n\nQRL3 · 1.000 cúbits\n"+s.optInt("qrl_episodes")+" episodios entrenados\n\nEstado original conservado, sin MPS. La conversación utiliza su motor XI actual.")
    .setPositiveButton("Probar política",(d,w)->quantumJob(false))
    .setNeutralButton("Entrenar 1 episodio",(d,w)->quantumJob(true)).setNegativeButton("Cerrar",null).show();
  });}catch(Exception e){showError(e);}finally{BUSY.set(false);runOnUiThread(()->status.setText("● Disponible sin conexión"));}});
 }
 private void quantumJob(boolean train){
  if(!BUSY.compareAndSet(false,true))return;status.setText(train?"Entrenando un episodio…":"Probando la política…");
  WORK.execute(()->{try{JSONObject result=train?engine.trainEpisode():engine.quantumAction();runOnUiThread(()->{if(!isDestroyed())new AlertDialog.Builder(this).setTitle(train?"Episodio guardado":"Política QRL3").setMessage(train?"Episodios de QRL3: "+result.optInt("qrl_episodes"):"Posición inicial: 3\nObjetivo: 6\n\nAcción elegida: "+(result.optInt("action")==1?"derecha":"izquierda")+"\nProbabilidad de ir a la derecha: "+String.format(java.util.Locale.ROOT,"%.1f %%",100*result.optDouble("probability_right"))).setPositiveButton("Cerrar",null).show();});}catch(Exception e){showError(e);}finally{BUSY.set(false);runOnUiThread(()->status.setText("● Disponible sin conexión"));}});
 }
 @Override protected void onSaveInstanceState(Bundle out){out.putString("draft",input.getText().toString());super.onSaveInstanceState(out);}
 @Override protected void onActivityResult(int request,int result,Intent data){
  super.onActivityResult(request,result,data);
  if(request==71&&result==RESULT_OK&&data!=null&&engine!=null)WORK.execute(()->{try(OutputStream out=getContentResolver().openOutputStream(data.getData())){out.write(engine.exportHistory().getBytes(StandardCharsets.UTF_8));runOnUiThread(()->Toast.makeText(this,"Conversación exportada",Toast.LENGTH_SHORT).show());}catch(Exception e){showError(e);}});
 }
}
