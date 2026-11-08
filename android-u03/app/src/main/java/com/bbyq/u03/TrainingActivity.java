package com.bbyq.u03;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.lang.ref.WeakReference;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** A guided, offline training workspace over the same native BBY Q runtime. */
public final class TrainingActivity extends Activity {
    private static final int BG=0xff101820, PANEL=0xff1b2a34, FG=0xffeef6f4,
        MUTED=0xffb2c4ca, ACCENT=0xff82e0c2, AMBER=0xffffce86, RED=0xffffaaa5;
    private static final int EXPORT_REQUEST=617;
    private static final ExecutorService WORKER=Executors.newSingleThreadExecutor();
    private static volatile boolean working=false;
    private static volatile String workLabel="", lastAction="", lastError="", resolvedSessionId="";
    private static volatile JSONObject lastOutcome, lastStatus;
    private static volatile WeakReference<TrainingActivity> visible=new WeakReference<>(null);

    private SharedPreferences preferences;
    private LinearLayout root, content, navigation;
    private ScrollView scroll;
    private TextView status;
    private ProgressBar progress;
    private int page=0;
    private String sessionId="", exportPath="", episodeId="";
    private JSONObject episode;
    private final Map<String,EditText> fields=new LinkedHashMap<>();
    private final String[] pages={"Sesión","Enseñar","Probar","Guardar"};

    private int dp(int value){return Math.round(value*getResources().getDisplayMetrics().density);}
    private LinearLayout column(){LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);return v;}
    private TextView text(String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setLineSpacing(dp(3),1);return t;}
    private GradientDrawable background(int color,int radius){GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));return d;}
    private LinearLayout.LayoutParams margin(int w,int h,int top){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w,h);p.topMargin=dp(top);return p;}
    private Button button(String title,int id,boolean primary,Runnable action){
        Button b=new Button(this);b.setText(title);b.setAllCaps(false);b.setTextSize(15);b.setMinHeight(dp(50));
        b.setTextColor(primary?BG:FG);b.setBackgroundTintList(ColorStateList.valueOf(primary?ACCENT:PANEL));
        if(id!=0)b.setId(id);b.setContentDescription(title);b.setOnClickListener(v->action.run());return b;
    }
    private void addButton(LinearLayout area,String label,int id,boolean primary,Runnable action){
        area.addView(button(label,id,primary,action),margin(-1,-2,8));
    }
    private LinearLayout card(String eyebrow,String title,String body){
        LinearLayout card=column();card.setBackground(background(PANEL,16));card.setPadding(dp(16),dp(15),dp(16),dp(15));
        if(!eyebrow.isEmpty()){TextView small=text(eyebrow,11,ACCENT);small.setLetterSpacing(.12f);card.addView(small);}
        TextView heading=text(title,21,FG);heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);card.addView(heading,margin(-1,-2,5));
        if(!body.isEmpty())card.addView(text(body,15,MUTED),margin(-1,-2,8));
        content.addView(card,margin(-1,-2,12));return card;
    }
    private EditText input(LinearLayout area,String key,String label,String hint,String initial,int id,boolean numeric){
        area.addView(text(label,13,MUTED),margin(-1,-2,12));
        EditText value=new EditText(this);value.setSingleLine(true);value.setTextColor(FG);value.setHintTextColor(MUTED);
        value.setTextSize(16);value.setMinHeight(dp(50));value.setPadding(dp(10),dp(8),dp(10),dp(8));
        value.setBackground(background(BG,8));value.setHint(hint);value.setContentDescription(label);
        value.setInputType(numeric?InputType.TYPE_CLASS_NUMBER:InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        value.setText(preferences.getString("draft_"+key,initial));if(id!=0)value.setId(id);
        area.addView(value,margin(-1,-2,5));fields.put(key,value);return value;
    }
    private static JSONObject args(Object... pairs){
        JSONObject result=new JSONObject();try{for(int i=0;i<pairs.length;i+=2)result.put(String.valueOf(pairs[i]),pairs[i+1]);}catch(Exception e){throw new IllegalArgumentException(e);}
        return result;
    }
    private String value(String key){EditText e=fields.get(key);return e==null?preferences.getString("draft_"+key,""):e.getText().toString().trim();}
    private boolean required(String... names){
        for(String name:names)if(value(name).isEmpty()){EditText e=fields.get(name);if(e!=null){e.setError("Completa este campo");e.requestFocus();}return false;}return true;
    }
    private int number(String key,int minimum,int maximum){
        try{long n=Long.parseLong(value(key));if(n<minimum||n>maximum)throw new NumberFormatException();return (int)n;}
        catch(NumberFormatException e){EditText field=fields.get(key);if(field!=null){field.setError("Usa un número de "+minimum+" a "+maximum);field.requestFocus();}throw new IllegalArgumentException("Revisa el número indicado.");}
    }

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);preferences=getSharedPreferences("bbyq-training-ui",MODE_PRIVATE);
        sessionId=resolvedSessionId.isEmpty()?preferences.getString("session_id",""):resolvedSessionId;page=preferences.getInt("page",0);
        exportPath=preferences.getString("export_path","");episodeId=preferences.getString("episode_id","");
        try{String raw=preferences.getString("episode","");if(!raw.isEmpty())episode=new JSONObject(raw);}catch(Exception ignored){}
        if(saved!=null)page=saved.getInt("page",page);
        visible=new WeakReference<>(this);
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        root=column();root.setBackgroundColor(BG);root.setPadding(dp(16),dp(10),dp(16),dp(8));
        root.setOnApplyWindowInsetsListener((view,insets)->{
            if(android.os.Build.VERSION.SDK_INT>=30){android.graphics.Insets bars=insets.getInsets(android.view.WindowInsets.Type.systemBars());view.setPadding(dp(16)+bars.left,dp(10)+bars.top,dp(16)+bars.right,dp(8)+bars.bottom);}
            else view.setPadding(dp(16)+insets.getSystemWindowInsetLeft(),dp(10)+insets.getSystemWindowInsetTop(),dp(16)+insets.getSystemWindowInsetRight(),dp(8)+insets.getSystemWindowInsetBottom());
            return insets;
        });
        LinearLayout header=new LinearLayout(this);header.setGravity(Gravity.CENTER_VERTICAL);
        TextView heading=text("Entrenar BBY Q",23,FG);heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        header.addView(heading,new LinearLayout.LayoutParams(0,-2,1));
        header.addView(button("Guía",0x5803002,false,this::showGuide),new LinearLayout.LayoutParams(dp(82),dp(50)));
        root.addView(header);
        status=text("Preparando tu espacio…",13,MUTED);status.setId(0x5803001);status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        root.addView(status,margin(-1,-2,5));
        progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setIndeterminate(true);progress.setProgressTintList(ColorStateList.valueOf(ACCENT));root.addView(progress,margin(-1,dp(3),8));
        scroll=new ScrollView(this);scroll.setFillViewport(true);content=column();scroll.addView(content);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        navigation=new LinearLayout(this);navigation.setPadding(0,dp(8),0,0);root.addView(navigation);
        for(int i=0;i<pages.length;i++){final int destination=i;Button b=button(pages[i],0x5803020+i,false,()->switchPage(destination));b.setTextSize(12);b.setPadding(dp(2),0,dp(2),0);navigation.addView(b,new LinearLayout.LayoutParams(0,dp(52),1));}
        setContentView(root);render();
        if(!working){
            String pending=preferences.getString("pending_request","");
            if(!pending.isEmpty())try{call("resume",new JSONObject(pending),preferences.getString("pending_label","Reanudando el paso guardado"));}catch(Exception e){preferences.edit().remove("pending_request").apply();call("status",args(),"Revisando las sesiones guardadas");}
            else call("status",args(),"Revisando las sesiones guardadas");
        }else updateWorking();
    }
    private void persist(){
        SharedPreferences.Editor edit=preferences.edit().putString("session_id",sessionId).putInt("page",page).putString("export_path",exportPath).putString("episode_id",episodeId);
        if(episode!=null)edit.putString("episode",episode.toString());else edit.remove("episode");
        for(Map.Entry<String,EditText> item:fields.entrySet())edit.putString("draft_"+item.getKey(),item.getValue().getText().toString());edit.apply();
    }
    @Override protected void onPause(){persist();super.onPause();}
    @Override protected void onSaveInstanceState(Bundle out){persist();out.putInt("page",page);super.onSaveInstanceState(out);}
    @Override protected void onDestroy(){if(visible.get()==this)visible=new WeakReference<>(null);super.onDestroy();}
    private void switchPage(int destination){persist();page=destination;render();scroll.scrollTo(0,0);}
    private void render(){
        content.removeAllViews();fields.clear();
        for(int i=0;i<navigation.getChildCount();i++){Button b=(Button)navigation.getChildAt(i);b.setTextColor(page==i?BG:FG);b.setBackgroundTintList(ColorStateList.valueOf(page==i?ACCENT:PANEL));}
        if(page==0)sessionPage();else if(page==1)teachPage();else if(page==2)practicePage();else savePage();
        outcomeCard();updateWorking();
    }
    private JSONObject currentSession(){
        if(lastStatus==null)return null;
        JSONObject selected=lastStatus.optJSONObject("session");
        if(selected!=null&&(sessionId.isEmpty()||sessionId.equals(selected.optString("id",selected.optString("session_id")))))return selected;
        JSONArray all=lastStatus.optJSONArray("sessions");
        if(all!=null)for(int i=0;i<all.length();i++){JSONObject item=all.optJSONObject(i);if(item!=null&&sessionId.equals(item.optString("id",item.optString("session_id"))))return item;}
        return null;
    }
    private void sessionPage(){
        LinearLayout intro=card("TU ESPACIO DE APRENDIZAJE","Enséñale. Comprueba. Conserva.","Trabaja en una sesión guardada. Primero enseñamos; después hacemos pruebas. Cuando el resultado esté comprobado, podrás usarlo en la conversación.");
        addButton(intro,"Leer la guía con dibujos",0,false,this::showGuide);
        JSONArray sessions=lastStatus==null?null:lastStatus.optJSONArray("sessions");
        if(sessions!=null&&sessions.length()>0){
            LinearLayout existing=card("CONTINUAR","Tus sesiones",sessionSummary());
            String[] titles=new String[sessions.length()];String[] ids=new String[sessions.length()];int selected=0;
            for(int i=0;i<sessions.length();i++){JSONObject s=sessions.optJSONObject(i);if(s==null)continue;ids[i]=s.optString("id",s.optString("session_id"));titles[i]=s.optString("title","Sesión "+(i+1));if(ids[i].equals(sessionId))selected=i;}
            Spinner selector=new Spinner(this);selector.setId(0x5803012);selector.setContentDescription("Sesión de entrenamiento");
            ArrayAdapter<String> adapter=new ArrayAdapter<String>(this,android.R.layout.simple_spinner_item,titles){
                @Override public View getView(int p,View v,android.view.ViewGroup parent){TextView t=(TextView)super.getView(p,v,parent);t.setTextColor(FG);t.setTextSize(16);return t;}
                @Override public View getDropDownView(int p,View v,android.view.ViewGroup parent){TextView t=(TextView)super.getDropDownView(p,v,parent);t.setTextColor(BG);t.setBackgroundColor(0xffedf6f2);t.setMinHeight(dp(50));return t;}
            };
            adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);selector.setAdapter(adapter);selector.setSelection(selected,false);existing.addView(selector,margin(-1,dp(54),3));
            selector.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){public void onNothingSelected(AdapterView<?> p){}public void onItemSelected(AdapterView<?> p,View v,int position,long id){if(!working&&!ids[position].equals(sessionId)){sessionId=ids[position];episodeId="";episode=null;preferences.edit().putBoolean("teacher_revealed",false).apply();persist();call("status",args(),"Abriendo la sesión");}}});
            addButton(existing,"Continuar enseñando",0,true,()->switchPage(1));
        }
        LinearLayout fresh=card("PASO 1","Crea una sesión","Ponle un nombre que explique qué quieres enseñarle, como «Nara y sus reglas».");
        input(fresh,"name","Nombre de la sesión","Nara y sus reglas","Mi primer entrenamiento",0x5803010,false);
        addButton(fresh,"Crear sesión",0x5803011,true,()->{if(required("name"))call("create",args("title",value("name")),"Creando una copia para entrenar");});
        addButton(content,"Actualizar sesiones",0,false,()->call("status",args(),"Revisando las sesiones guardadas"));
        addButton(content,"Volver a la conversación",0,false,this::finish);
    }
    private boolean requireSession(){if(sessionId.isEmpty()){Toast.makeText(this,"Primero crea o elige una sesión.",Toast.LENGTH_LONG).show();switchPage(0);return false;}return true;}
    private String sessionSummary(){
        JSONObject s=currentSession();if(s==null)return "Elige una sesión para continuar.";
        return "Pasos de enseñanza: "+s.optInt("training_count")+" · Pruebas reservadas: "+s.optInt("holdout_count")+(s.optBoolean("active")?"\nEste entrenamiento está activo en la conversación.":"");
    }
    private void sessionCaption(){JSONObject s=currentSession();TextView t=text((s==null?"Sesión guardada":s.optString("title","Tu sesión"))+"\n"+sessionSummary(),13,ACCENT);content.addView(t,margin(-1,-2,10));}
    private void teachPage(){
        if(sessionId.isEmpty()){card("ANTES DE EMPEZAR","Elige una sesión","La sesión conserva tus lecciones, pruebas y cambios de aprendizaje.");addButton(content,"Crear o elegir sesión",0,true,()->switchPage(0));return;}
        sessionCaption();
        if(!episodeId.isEmpty())card("EJERCICIO PENDIENTE","Termina esta vuelta","Ya hay una predicción registrada. Revela su clase y enseña la corrección, o descarta ese ejercicio antes de añadir otras lecciones.");
        LinearLayout fact=card("PASO 2 · MEMORIA","Enseña un hecho","Ejemplo: Nara es robot. BBY Q guardará la relación en su memoria para usarla al responder.");
        input(fact,"subject","Sujeto","Nara","Nara",0x5803030,false);
        input(fact,"property","Es…","robot","robot",0x5803031,false);
        addButton(fact,"Guardar este hecho",0x5803032,true,()->{if(required("subject","property"))call("fact",args("subject",value("subject"),"property",value("property")),"Enseñando el hecho a BBY Q");});
        LinearLayout rule=card("CONECTA DOS IDEAS","Enseña una regla","Ejemplo: si alguien es robot, entonces es máquina. Después podrás preguntar si Nara es máquina.");
        input(rule,"kind","Si es…","robot","robot",0x5803033,false);
        input(rule,"goal","Entonces es…","máquina","máquina",0x5803034,false);
        addButton(rule,"Guardar esta regla",0x5803035,true,()->{if(required("kind","goal"))call("rule",args("antecedent",value("kind"),"consequence",value("goal")),"Enseñando la regla a BBY Q");});
        LinearLayout joint=card("PASO 3 · APRENDIZAJE CONJUNTO","Un ejercicio para los motores","Aquí BBY Q predice una muestra numérica y recibe una corrección. Este paso ajusta sus parámetros. Al comprobar, la app utilizará ejercicios reservados diferentes a los que entrenaste.");
        input(joint,"sample_id","Número de muestra","2023144612","2023144612",0x5803050,true);
        input(joint,"rule_value","Regla del ejercicio: 0 o 1","1","1",0x5803051,true);
        input(joint,"position","Posición de partida: de 0 a 6","3","3",0x5803052,true);
        addButton(joint,"Primero, pedir una predicción",0x5803053,true,()->{
            try{call("joint_prepare",args("seed",number("sample_id",0,Integer.MAX_VALUE),"rule",number("rule_value",0,1),"position",number("position",0,6)),"Ejecutando la predicción conjunta");}catch(IllegalArgumentException ignored){}
        });
        if(episode!=null&&!episodeId.isEmpty()){
            TextView prediction=text(jointPrediction(episode),15,FG);prediction.setId(0x5803054);joint.addView(prediction,margin(-1,-2,12));
            final TextView correct=text(preferences.getBoolean("teacher_revealed",false)?teacherAnswer(episode):"La respuesta correcta se revela después de la predicción.",14,MUTED);
            correct.setId(0x5803056);joint.addView(correct,margin(-1,-2,10));
            addButton(joint,"Ver la clase correcta del ejercicio",0x5803055,false,()->{
                correct.setText(teacherAnswer(episode));correct.setTextColor(ACCENT);
                preferences.edit().putBoolean("teacher_revealed",true).apply();
                View teach=findViewById(0x5803057);if(teach!=null)teach.setEnabled(!working);
            });
            Button teach=button("Enseñar esta corrección",0x5803057,true,()->{
                if(!preferences.getBoolean("teacher_revealed",false))return;
                call("joint_feedback",args("exercise_id",episodeId),"Aprendiendo de la corrección comprobada");
            });
            teach.setEnabled(preferences.getBoolean("teacher_revealed",false)&&!working);joint.addView(teach,margin(-1,-2,8));
            addButton(joint,"Descartar este ejercicio",0x5803058,false,()->call("joint_discard",args("exercise_id",episodeId),"Recuperando el estado previo al ejercicio"));
        }
        addButton(content,"Pasar a las pruebas",0,false,()->switchPage(2));
    }
    private String teacherAnswer(JSONObject r){
        JSONObject teacher=r.optJSONObject("teacher");
        return teacher==null?"La respuesta correcta no está disponible.":"Clase correcta del ejercicio: "+teacher.optInt("class")+". Se enseñará esta corrección registrada.";
    }
    private String jointPrediction(JSONObject r){
        JSONObject prediction=r.optJSONObject("prediction");if(prediction==null)prediction=r.optJSONObject("mission");if(prediction==null)prediction=r;
        String label=prediction.has("class")?String.valueOf(prediction.optInt("class")):prediction.optString("predicted_class","pendiente");
        String action=prediction.optString("action_label",prediction.has("action")?String.valueOf(prediction.optInt("action")):"");
        return "Predicción registrada: clase "+label+(action.isEmpty()?"":". Acción: "+action)+".\nComprueba la respuesta antes de enseñar la corrección.";
    }
    private void practicePage(){
        if(sessionId.isEmpty()){card("PASO 4","Hace falta una sesión","Crea una sesión para probar lo que aprenda BBY Q.");addButton(content,"Ir a Sesión",0,true,()->switchPage(0));return;}
        sessionCaption();
        LinearLayout query=card("PRUEBA SIN ENSEÑAR","Haz una pregunta nueva","Si enseñaste «Nara es robot» y «robot implica máquina», pregunta «es Nara máquina». La pregunta prueba la sesión; no la corrige.");
        input(query,"question","Pregunta de prueba","es Nara máquina","es Nara máquina",0x5803040,false);
        CheckBox heldout=new CheckBox(this);heldout.setId(0x5803043);heldout.setText("Guardar como prueba reservada");heldout.setTextSize(14);heldout.setTextColor(FG);heldout.setButtonTintList(ColorStateList.valueOf(ACCENT));heldout.setChecked(preferences.getBoolean("holdout",true));heldout.setMinHeight(dp(48));query.addView(heldout,margin(-1,-2,10));
        query.addView(text("Una prueba reservada se compara con el estado inicial y no se usa para enseñar. Para reservarla, escribe «es Nara máquina» o «dime si Nara es máquina».",13,MUTED),margin(-1,-2,5));
        Spinner expected=new Spinner(this);expected.setId(0x5803044);expected.setContentDescription("Resultado esperado de la prueba");
        String[] outcomes={"Debe poder demostrarlo","No tiene evidencia para demostrarlo"};
        ArrayAdapter<String> choices=new ArrayAdapter<String>(this,android.R.layout.simple_spinner_item,outcomes){
            @Override public View getView(int p,View v,android.view.ViewGroup group){TextView t=(TextView)super.getView(p,v,group);t.setTextColor(FG);t.setTextSize(13);return t;}
            @Override public View getDropDownView(int p,View v,android.view.ViewGroup group){TextView t=(TextView)super.getDropDownView(p,v,group);t.setTextColor(BG);t.setBackgroundColor(0xffedf6f2);t.setTextSize(14);t.setMinHeight(dp(50));return t;}
        };
        choices.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);expected.setAdapter(choices);expected.setSelection(preferences.getInt("expected_status_choice",0));query.addView(expected,margin(-1,dp(54),5));
        addButton(query,"Probar la respuesta",0x5803041,true,()->{
            if(!required("question"))return;
            preferences.edit().putBoolean("holdout",heldout.isChecked()).putInt("expected_status_choice",expected.getSelectedItemPosition()).apply();
            JSONObject request=args("text",value("question"),"split",heldout.isChecked()?"holdout":"practice");
            try{if(heldout.isChecked())request.put("expected_status",expected.getSelectedItemPosition()==0?1:0);}catch(Exception ignored){}
            call("query",request,"Probando sin entrenar");
        });
        LinearLayout validation=card("COMPARA CON EL INICIO","Comprobar el entrenamiento","La app revisará tus lecciones, las preguntas que reservaste y las capacidades anteriores. Si entrenaste los motores, también usará ejercicios numéricos reservados automáticamente. Verás los aciertos antes de activar los cambios.");
        addButton(validation,"Ejecutar comprobación",0x5803042,true,()->call("validate",args(),"Comparando el estado inicial y el entrenado"));
        addButton(content,"Ver resultados y guardar",0,false,()->switchPage(3));
    }
    private boolean validated(){
        JSONObject selected=currentSession();
        if(selected==null||lastStatus==null)return false;
        JSONObject validation=lastStatus.optJSONObject("validation");
        if(validation==null)validation=selected.optJSONObject("validation");
        return !selected.optBoolean("active",false)&&validation!=null&&validation.optBoolean("passed",false)&&validation.optBoolean("activation_allowed",false);
    }
    private void savePage(){
        if(sessionId.isEmpty()){card("PASO 5","Guarda el trabajo comprobado","Primero crea una sesión y enséñale algo.");addButton(content,"Ir a Sesión",0,true,()->switchPage(0));return;}
        sessionCaption();
        boolean alreadyActive=currentSession()!=null&&currentSession().optBoolean("active",false);
        LinearLayout activation=card("LLEVARLO A LA CONVERSACIÓN","Usar lo que aprendió",alreadyActive?"Este entrenamiento ya está activo. Puedes volver a la conversación para usar lo que aprendió.":validated()?"La comprobación está aprobada. Al activar, BBY Q usará el estado entrenado en la conversación. Se conserva una copia del estado anterior.":"Ejecuta la comprobación en Probar. La activación estará disponible cuando sus resultados permitan aplicar los cambios.");
        Button activate=button(alreadyActive?"Este entrenamiento está en uso":"Usar este entrenamiento",0x5803060,true,()->call("activate",args(),"Activando el estado comprobado"));activate.setEnabled(validated()&&!working);activation.addView(activate,margin(-1,-2,10));
        addButton(activation,"Ir a comprobar",0,false,()->switchPage(2));
        LinearLayout export=card("PARA EVALUARLO DESPUÉS","Exporta tu sesión","Guarda un archivo con tus lecciones, predicciones, correcciones, pruebas y estado entrenado. Incluye también la memoria de partida de esta sesión. Después puedes adjuntarlo en el chat para evaluar tus resultados.");
        addButton(export,"Exportar entrenamiento",0x5803061,true,()->call("export",args(),"Preparando el archivo de entrenamiento"));
        export.addView(text("Tú eliges dónde guardarlo. Se comparte cuando tú adjuntas el archivo.",13,MUTED),margin(-1,-2,8));
        String backup=preferences.getString("backup_"+sessionId,"");
        if(!backup.isEmpty()){
            LinearLayout recovery=card("ESTADO ANTERIOR","Recuperar el punto de partida","La copia anterior a la activación sigue guardada. Si la recuperas, la conversación volverá a ese momento.");
            addButton(recovery,"Recuperar estado anterior",0x5803063,false,()->new android.app.AlertDialog.Builder(this)
                .setTitle("Recuperar el estado anterior")
                .setMessage("La conversación volverá al punto anterior a la activación. Los cambios nuevos de la conversación posteriores a esa activación se descartarán. La sesión de entrenamiento seguirá guardada.")
                .setNegativeButton("Cancelar",null).setPositiveButton("Recuperar",(dialog,which)->call("restore",args("backup_id",backup,"confirm_discard_new_activity",true),"Recuperando el estado anterior")).show());
        }
        addButton(content,"Volver a conversar",0x5803062,false,this::finish);
    }
    private void outcomeCard(){
        if(!lastError.isEmpty()){
            LinearLayout c=card("EL PASO NO TERMINÓ","Revisa este detalle",lastError);c.setBackground(background(0xff38262b,14));
            addButton(c,"Volver a mis sesiones",0,false,()->switchPage(0));return;
        }
        JSONObject r=lastOutcome;if(r==null||"status".equals(lastAction))return;
        String title="Resultado del último paso",body=r.optString("message","");
        if("create".equals(lastAction)){title="Sesión creada";if(body.isEmpty())body="Ya puedes guardar hechos y reglas, entrenar con ejercicios y hacer pruebas.";}
        if("fact".equals(lastAction)||"rule".equals(lastAction)){title="Lección guardada";if(body.isEmpty())body="La lección quedó en esta sesión. Ahora comprueba una pregunta que use lo que enseñaste.";}
        if("query".equals(lastAction)){title="Respuesta de la sesión";body=queryReply(r,body);}
        if("joint_prepare".equals(lastAction)){title="Predicción completada";body=jointPrediction(r);}
        if("joint_feedback".equals(lastAction)){title="Corrección procesada";int changed=r.optInt("changed_regions",-1);if(body.isEmpty())body="Se ejecutó el aprendizaje y se guardaron los comprobantes.";if(changed>=0)body+="\nRegiones de parámetros que cambiaron: "+changed+".";}
        if("validate".equals(lastAction)){
            JSONObject v=r.optJSONObject("validation");if(v==null)v=r;
            boolean pass=v.optBoolean("passed",false);title=pass?"Comprobación aprobada":"Revisa la comprobación";
            if(body.isEmpty())body=pass?"El resultado permite pasar al paso Guardar.":"La sesión conserva tu trabajo. Revisa sus resultados antes de seguir enseñando.";
            for(String key:new String[]{"baseline","candidate","lessons","regression","heldout"}){
                JSONObject score=v.optJSONObject(key);if(score==null)continue;
                if(score.has("correct")&&score.has("total"))body+="\n"+scoreLabel(key)+": "+score.optInt("correct")+" / "+score.optInt("total")+" aciertos.";
            }
            JSONArray failures=v.optJSONArray("reasons");if(failures!=null&&failures.length()>0)body+="\nPor revisar: "+failures.optString(0);
        }
        if("activate".equals(lastAction)){title="Entrenamiento activado";if(body.isEmpty())body="La conversación ya usa el estado entrenado y comprobado.";}
        if("joint_discard".equals(lastAction)){title="Ejercicio descartado";if(body.isEmpty())body="La sesión recuperó el estado previo a la predicción. Puedes elegir otra muestra.";}
        if("restore".equals(lastAction)){title="Estado anterior recuperado";if(body.isEmpty())body="La conversación volvió al estado anterior. Tu sesión de entrenamiento sigue guardada.";}
        if("export_saved".equals(lastAction))title="Entrenamiento guardado";
        if("export".equals(lastAction)){title="Archivo preparado";if(body.isEmpty())body="Elige un destino para guardar tu entrenamiento.";}
        if(body.isEmpty())body="El paso terminó. Los detalles quedan guardados para la exportación.";
        LinearLayout c=card("COMPROBANTE",title,body);c.setId(0x5803070);c.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
    }
    private String queryReply(JSONObject result,String fallback){
        JSONObject receipt=result.optJSONObject("receipt");JSONArray rows=receipt==null?null:receipt.optJSONArray("results");
        if(rows!=null)for(int i=0;i<rows.length();i++){
            JSONObject row=rows.optJSONObject(i);if(row==null||!row.optString("kind").equals("query"))continue;
            int status=row.optInt("status",-99);
            if(status==1)return "Sí: BBY Q pudo demostrar la afirmación con las lecciones de esta sesión.";
            if(status==0)return "Con las lecciones actuales, BBY Q no tiene evidencia suficiente para demostrar esa afirmación.";
            if(status==-1)return "BBY Q encontró evidencia contraria a esa afirmación en la sesión.";
        }
        return result.optString("reply",result.optString("answer",fallback));
    }
    private String scoreLabel(String key){if(key.equals("baseline"))return "Estado inicial";if(key.equals("candidate"))return "Estado entrenado";if(key.equals("lessons"))return "Tus lecciones";if(key.equals("regression"))return "Capacidades previas";return "Pruebas reservadas";}
    private void updateWorking(){
        progress.setVisibility(working?View.VISIBLE:View.INVISIBLE);
        if(working)status.setText(workLabel+"…\nPuedes consultar la guía mientras termina.");
        else if(!lastError.isEmpty())status.setText("La guía sigue disponible. Tu sesión permanece guardada.");
        else{JSONObject s=currentSession();status.setText(s==null?"Guía disponible sin conexión":"Sesión: "+s.optString("title","Tu entrenamiento"));}
        disableDuringWork(content);
    }
    private void disableDuringWork(android.view.ViewGroup group){
        for(int i=0;i<group.getChildCount();i++){
            View v=group.getChildAt(i);
            if(v instanceof Button){boolean enabled=!working;if(v.getId()==0x5803060)enabled=enabled&&validated();if(v.getId()==0x5803057)enabled=enabled&&preferences.getBoolean("teacher_revealed",false);if(v.getId()==0x5803032||v.getId()==0x5803035||v.getId()==0x5803053)enabled=enabled&&episodeId.isEmpty();v.setEnabled(enabled);}
            else if(v instanceof EditText||v instanceof Spinner||v instanceof CheckBox)v.setEnabled(!working);
            else if(v instanceof android.view.ViewGroup)disableDuringWork((android.view.ViewGroup)v);
        }
    }
    private void call(String action,JSONObject arguments,String label){
        if(working)return;
        final boolean resuming=action.equals("resume");final String operation=resuming?arguments.optString("action","status"):action;
        if(!resuming&&!operation.equals("status")&&!operation.equals("create")&&!requireSession())return;
        persist();final String selected=resuming?arguments.optString("session_id",sessionId):sessionId;final Context app=getApplicationContext();
        try{if(!resuming){arguments.put("action",operation);arguments.put("request_id",UUID.randomUUID().toString());if(!selected.isEmpty())arguments.put("session_id",selected);}}catch(Exception e){return;}
        final String request=arguments.toString();if(!operation.equals("status"))preferences.edit().putString("pending_request",request).putString("pending_label",label).commit();working=true;workLabel=label;lastError="";updateWorking();
        WORKER.execute(()->{
            try{
                JSONObject response=U03Runtime.operation(app,"training",request);lastOutcome=response;lastAction=operation;
                String next=response.optString("session_id",selected);JSONObject s=response.optJSONObject("session");if(s!=null)next=s.optString("id",s.optString("session_id",next));
                if(next.isEmpty())next=response.optString("id",selected);
                if(!next.isEmpty()){resolvedSessionId=next;app.getSharedPreferences("bbyq-training-ui",MODE_PRIVATE).edit().putString("session_id",next).apply();}
                try{
                    JSONObject listing=(operation.equals("status")&&response.has("sessions"))?response:U03Runtime.operation(app,"training",args("action","status").toString());
                    if(!next.isEmpty()){
                        JSONObject detail=(operation.equals("status")&&response.has("session"))?response:U03Runtime.operation(app,"training",args("action","status","session_id",next).toString());
                        java.util.Iterator<String> keys=detail.keys();while(keys.hasNext()){String key=keys.next();listing.put(key,detail.get(key));}
                    }
                    lastStatus=listing;
                }catch(Exception ignored){}
                app.getSharedPreferences("bbyq-training-ui",MODE_PRIVATE).edit().remove("pending_request").remove("pending_label").commit();lastError="";
            }catch(Exception|LinkageError e){lastError=e.getMessage()==null?"No se pudo completar el paso.":e.getMessage().split("\\n",2)[0];app.getSharedPreferences("bbyq-training-ui",MODE_PRIVATE).edit().remove("pending_request").remove("pending_label").commit();}
            finally{
                working=false;TrainingActivity a=visible.get();if(a!=null)a.runOnUiThread(a::receive);
            }
        });
    }
    private void receive(){
        if(isFinishing()||isDestroyed())return;
        if(!resolvedSessionId.isEmpty())sessionId=resolvedSessionId;persist();
        if(lastError.isEmpty()&&lastOutcome!=null){
            if(lastAction.equals("create")){page=1;episode=null;episodeId="";}
            else if(lastAction.equals("joint_prepare")){
                episode=lastOutcome;episodeId=lastOutcome.optString("exercise_id",lastOutcome.optString("id",""));
                preferences.edit().putBoolean("teacher_revealed",false).apply();
            }else if(lastAction.equals("joint_feedback")||lastAction.equals("joint_discard")){episode=null;episodeId="";}
            else if(lastAction.equals("validate"))page=3;
            else if(lastAction.equals("activate")){preferences.edit().putString("backup_"+sessionId,lastOutcome.optString("backup_id","")).apply();}
            else if(lastAction.equals("restore")){preferences.edit().remove("backup_"+sessionId).apply();}
        }
        if(lastStatus!=null&&currentSession()!=null){
            JSONObject pending=lastStatus.optJSONObject("pending_exercise");
            if(pending!=null){episode=pending;episodeId=pending.optString("exercise_id",lastStatus.optString("pending_exercise_id",episodeId));}
            else if(lastStatus.has("pending_exercise")&&lastStatus.isNull("pending_exercise")){episode=null;episodeId="";}
        }
        persist();render();if(!lastAction.equals("status")&&!lastAction.equals("create"))scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));
        if(lastError.isEmpty()&&lastAction.equals("export")&&lastOutcome!=null)saveExport(lastOutcome);
    }
    private void saveExport(JSONObject result){
        exportPath=result.optString("path",result.optString("export_path",""));JSONObject item=result.optJSONObject("export");if(exportPath.isEmpty()&&item!=null)exportPath=item.optString("path","");
        if(exportPath.isEmpty()){lastError="El archivo de entrenamiento no está disponible. Intenta exportar otra vez.";render();return;}
        persist();Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType("application/zip");
        intent.putExtra(Intent.EXTRA_TITLE,result.optString("filename","BBY-Q-mi-entrenamiento.zip"));startActivityForResult(intent,EXPORT_REQUEST);
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(request!=EXPORT_REQUEST||result!=RESULT_OK||data==null||data.getData()==null)return;
        final android.net.Uri destination=data.getData();final String source=exportPath;final Context app=getApplicationContext();
        working=true;workLabel="Guardando tu entrenamiento";updateWorking();
        WORKER.execute(()->{
            try{
                File file=new File(source).getCanonicalFile();String real=file.getPath();String files=app.getFilesDir().getCanonicalPath()+File.separator;String cache=app.getCacheDir().getCanonicalPath()+File.separator;
                if(!(real.startsWith(files)||real.startsWith(cache))||!file.isFile())throw new IOException("El archivo de entrenamiento no está disponible.");
                try(InputStream in=new FileInputStream(file);OutputStream out=app.getContentResolver().openOutputStream(destination)){
                    if(out==null)throw new IOException("No se pudo abrir el destino.");byte[] buffer=new byte[65536];int n;while((n=in.read(buffer))!=-1)out.write(buffer,0,n);
                }
                lastOutcome=args("message","Entrenamiento guardado. Adjunta ese archivo cuando quieras que evaluemos tus resultados.");lastAction="export_saved";lastError="";
            }catch(Exception e){lastError=e.getMessage()==null?"No se pudo guardar el archivo.":e.getMessage();}
            finally{working=false;TrainingActivity a=visible.get();if(a!=null)a.runOnUiThread(a::receive);}
        });
    }
    @Override public void onBackPressed(){
        if(working){Toast.makeText(this,"Espera a que termine este paso. Tu progreso se está guardando.",Toast.LENGTH_LONG).show();return;}
        super.onBackPressed();
    }
    private void showGuide(){
        try{
            String html;try(InputStream in=getAssets().open("training-guide.html");ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] data=new byte[8192];int n;while((n=in.read(data))!=-1)out.write(data,0,n);html=out.toString(StandardCharsets.UTF_8.name());}
            Dialog dialog=new Dialog(this);dialog.requestWindowFeature(android.view.Window.FEATURE_NO_TITLE);LinearLayout container=column();container.setBackgroundColor(BG);container.setPadding(dp(8),dp(8),dp(8),dp(8));
            Button close=button("Volver al entrenamiento",0x5803090,true,dialog::dismiss);container.addView(close,new LinearLayout.LayoutParams(-1,dp(52)));
            WebView guide=new WebView(this);guide.setId(0x5803091);guide.setContentDescription("Guía ilustrada para entrenar BBY Q");guide.setBackgroundColor(0xfff3f7f3);
            guide.getSettings().setJavaScriptEnabled(false);guide.getSettings().setAllowFileAccess(false);guide.getSettings().setAllowContentAccess(false);
            guide.getSettings().setBlockNetworkLoads(true);guide.getSettings().setDomStorageEnabled(false);guide.getSettings().setDefaultTextEncodingName("UTF-8");
            guide.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){return !"bbyq.invalid".equals(request.getUrl().getHost());}});
            container.addView(guide,new LinearLayout.LayoutParams(-1,0,1));dialog.setContentView(container);dialog.setOnDismissListener(d->guide.destroy());dialog.show();
            if(dialog.getWindow()!=null)dialog.getWindow().setLayout(-1,-1);
            guide.loadDataWithBaseURL("https://bbyq.invalid/",html,"text/html","UTF-8",null);
        }catch(Exception e){Toast.makeText(this,"No se pudo abrir la guía: "+e.getMessage(),Toast.LENGTH_LONG).show();}
    }
}
