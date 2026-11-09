package com.bbyq.u03;

import android.app.Activity;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Personal model, memory and development controls, separate from the conversation. */
public final class ModelActivity extends Activity {
    private static final int EXPORT_REPORT=718;
    private final ExecutorService queue=Executors.newSingleThreadExecutor();
    private LinearLayout root,content,navigation;
    private TextView stateLabel;
    private JSONObject modelState,trainingState;
    private String exportText="",exportName="BBY-Q-0-estado.json";
    private boolean loading=false;
    private final ArrayList<Dialog> openDialogs=new ArrayList<>();

    private int dp(float n){return UiKit.dp(this,n);}
    private TextView text(String value,int size,int color){return UiKit.text(this,value,size,color);}
    private LinearLayout column(){return UiKit.column(this);}
    private LinearLayout.LayoutParams gap(int w,int h,int top){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w,h);p.topMargin=dp(top);return p;}
    private SharedPreferences settings(){return getSharedPreferences("bbyq-personal",MODE_PRIVATE);}
    private static JSONObject object(Object... pairs){JSONObject r=new JSONObject();try{for(int i=0;i<pairs.length;i+=2)r.put(String.valueOf(pairs[i]),pairs[i+1]);}catch(Exception e){throw new IllegalArgumentException(e);}return r;}
    private Button button(String title,int id,boolean primary,Runnable onClick){Button b=UiKit.button(this,title,primary);if(id!=0)b.setId(id);b.setContentDescription(title);b.setOnClickListener(v->onClick.run());return b;}
    private void action(LinearLayout parent,String title,int id,boolean primary,Runnable onClick){parent.addView(button(title,id,primary,onClick),gap(-1,-2,10));}
    private LinearLayout card(LinearLayout parent,String title,String detail){
        LinearLayout c=UiKit.card(this);TextView heading=text(title,19,UiKit.TEXT);heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);c.addView(heading);
        if(!detail.isEmpty())c.addView(text(detail,14,UiKit.MUTED),gap(-1,-2,7));parent.addView(c,gap(-1,-2,12));return c;
    }

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);if(saved!=null){exportText=saved.getString("export_text","");exportName=saved.getString("export_name",exportName);}
        build();
    }
    @Override protected void onResume(){super.onResume();refresh();}
    @Override protected void onSaveInstanceState(Bundle out){out.putString("export_text",exportText);out.putString("export_name",exportName);super.onSaveInstanceState(out);}
    @Override protected void onDestroy(){for(Dialog dialog:new ArrayList<>(openDialogs))dialog.dismiss();queue.shutdown();super.onDestroy();}
    private void build(){
        root=column();root.setId(0x5804000);root.setBackgroundColor(UiKit.BG);
        LinearLayout header=new LinearLayout(this);header.setGravity(Gravity.CENTER_VERTICAL);
        header.addView(UiKit.brand(this,38),new LinearLayout.LayoutParams(dp(38),dp(38)));
        LinearLayout titles=column();titles.setPadding(dp(12),0,0,0);
        TextView title=text("Mi BBY Q",23,UiKit.TEXT);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);titles.addView(title);
        titles.addView(text("El espacio personal de "+settings().getString("owner_name","X"),12,UiKit.MUTED));header.addView(titles,new LinearLayout.LayoutParams(0,-2,1));root.addView(header,gap(-1,-2,0));
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setId(0x5804008);content=column();scroll.addView(content);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        navigation=new LinearLayout(this);navigation.setPadding(0,dp(8),0,0);
        Button chat=button("Conversar",0x5804007,false,this::openConversation);Button model=button("Mi BBY Q",0x5804009,true,()->{});
        chat.setMinHeight(dp(52));model.setMinHeight(dp(52));LinearLayout.LayoutParams left=new LinearLayout.LayoutParams(0,-2,1);left.rightMargin=dp(8);navigation.addView(chat,left);navigation.addView(model,new LinearLayout.LayoutParams(0,-2,1));root.addView(navigation);
        setContentView(root);UiKit.applyInsets(getWindow(),root,16,12,16,8,true,navigation);render();
    }
    private void render(){
        content.removeAllViews();
        LinearLayout identity=card(content,"BBY Q 0","Tu modelo y lo que aprende contigo, en este dispositivo.");
        stateLabel=text(loading?"Leyendo el estado guardado…":"Preparando el modelo…",14,UiKit.MUTED);stateLabel.setId(0x5804006);stateLabel.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);identity.addView(stateLabel,gap(-1,-2,12));
        if(modelState!=null){
            JSONObject active=trainingState==null?null:trainingState.optJSONObject("active");String activeTitle="Modelo inicial con tu memoria personal";
            JSONArray sessions=sessions();int lessons=0;for(int i=0;i<sessions.length();i++){JSONObject s=sessions.optJSONObject(i);if(s==null)continue;lessons+=s.optInt("training_count");if(s.optBoolean("active"))activeTitle="En uso: "+s.optString("title","Tu entrenamiento");}
            stateLabel.setText(activeTitle);stateLabel.setTextColor(UiKit.ACCENT);
            LinearLayout counts=new LinearLayout(this);counts.setPadding(0,dp(14),0,0);stat(counts,String.valueOf(sessions.length()),"sesiones");stat(counts,String.valueOf(lessons),"pasos de aprendizaje");stat(counts,active==null?"Inicial":"Personal","estado en uso");identity.addView(counts);
        }
        LinearLayout learn=card(content,"Enseñarle algo","Hechos, reglas y ejercicios guiados. Comprueba los cambios antes de usarlos en la conversación.");
        action(learn,"Entrenar BBY Q",0x5804001,true,()->openTraining(0,null,false));
        action(learn,"Guía ilustrada",0x5804011,false,()->openTraining(0,null,true));
        LinearLayout memory=card(content,"Lo que recuerda","Consulta los hechos y reglas del modelo que estás usando. Busca por nombre o por una palabra.");
        action(memory,"Abrir memoria",0x5804002,false,this::showMemory);
        LinearLayout progress=card(content,"Tu aprendizaje","Continúa una sesión, revisa sus pruebas, recupera una copia o exporta el trabajo para evaluarlo después.");
        JSONArray sessions=sessions();
        for(int i=0;i<Math.min(3,sessions.length());i++){
            JSONObject s=sessions.optJSONObject(i);if(s==null)continue;
            String title=s.optString("title","Sesión"),id=s.optString("session_id");
            LinearLayout row=column();row.setPadding(0,dp(11),0,dp(3));TextView name=text(title,15,UiKit.TEXT);name.setTypeface(Typeface.DEFAULT,Typeface.BOLD);row.addView(name);
            row.addView(text(sessionState(s)+" · "+s.optInt("training_count")+" pasos · "+s.optInt("holdout_count")+" pruebas",12,UiKit.MUTED));
            Button open=button(s.optBoolean("active")?"Ver resultados y copia":"Continuar",0,false,()->openTraining(s.optBoolean("active")?3:0,id,false));row.addView(open,gap(-1,-2,6));progress.addView(row);
        }
        action(progress,"Sesiones, copias y exportación",0x5804003,false,this::showSessions);
        LinearLayout preferences=card(content,"A tu manera","Ajusta la lectura y consulta el estado de tu modelo.");
        action(preferences,"Preferencias",0x5804004,false,this::showPreferences);
        action(content,"Herramientas avanzadas",0x5804005,false,this::showAdvanced);
        TextView foot=text("Los informes técnicos y el panel de ciclos están en Herramientas avanzadas.",12,UiKit.MUTED);foot.setPadding(dp(4),dp(8),dp(4),dp(16));content.addView(foot);
    }
    private void stat(LinearLayout parent,String count,String label){LinearLayout cell=column();TextView n=text(count,22,UiKit.TEXT);n.setTypeface(Typeface.DEFAULT,Typeface.BOLD);cell.addView(n);cell.addView(text(label,11,UiKit.MUTED));parent.addView(cell,new LinearLayout.LayoutParams(0,-2,1));}
    private JSONArray sessions(){return trainingState==null?new JSONArray():trainingState.optJSONArray("sessions")==null?new JSONArray():trainingState.optJSONArray("sessions");}
    private String sessionState(JSONObject s){if(s.optBoolean("active"))return "En la conversación";String status=s.optString("state");if(status.equals("validated"))return "Comprobada";if(status.equals("restored"))return "Estado anterior recuperado";if(status.equals("activated"))return "Versión conservada";return s.optInt("training_count")>0?"En entrenamiento":"Lista para enseñar";}
    private void refresh(){
        if(loading||isDestroyed())return;loading=true;if(stateLabel!=null)stateLabel.setText("Leyendo el estado guardado…");
        queue.execute(()->{try{JSONObject state=U03Runtime.status(getApplicationContext());runOnUiThread(()->{if(isDestroyed())return;modelState=state;trainingState=state.optJSONObject("personal_training");loading=false;render();});}
            catch(Exception|LinkageError error){runOnUiThread(()->{if(isDestroyed())return;loading=false;stateLabel.setText("El modelo no terminó de abrir. Puedes consultar la guía o revisar el diagnóstico en Herramientas avanzadas.");stateLabel.setTextColor(UiKit.AMBER);});}});
    }
    private void openConversation(){Intent i=new Intent(this,IntegratedActivity.class);i.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);startActivity(i);finish();}
    private void openTraining(int page,String id,boolean guide){Intent i=new Intent(this,TrainingActivity.class).putExtra("training_page",page).putExtra("open_training_guide",guide);if(id!=null&&!id.isEmpty())i.putExtra("training_session_id",id);startActivity(i);}

    private final class Sheet {
        final Dialog dialog;final LinearLayout container,body;final ScrollView scroll;final TextView status;
        Sheet(String title){
            dialog=new Dialog(ModelActivity.this,android.R.style.Theme_Material_NoActionBar);dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);container=column();container.setBackgroundColor(UiKit.BG);
            LinearLayout header=new LinearLayout(ModelActivity.this);header.setGravity(Gravity.CENTER_VERTICAL);TextView heading=text(title,21,UiKit.TEXT);heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);header.addView(heading,new LinearLayout.LayoutParams(0,-2,1));
            header.addView(button("Cerrar",0,false,dialog::dismiss),new LinearLayout.LayoutParams(dp(88),-2));container.addView(header);
            status=text("",13,UiKit.MUTED);status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);container.addView(status,gap(-1,-2,4));
            scroll=new ScrollView(ModelActivity.this);scroll.setFillViewport(true);body=column();scroll.addView(body);container.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
            dialog.setContentView(container);
            dialog.setOnDismissListener(d->openDialogs.remove(dialog));
        }
        void show(){openDialogs.add(dialog);dialog.show();if(dialog.getWindow()!=null){dialog.getWindow().setLayout(-1,-1);UiKit.applyInsets(dialog.getWindow(),container,16,10,16,10,true);}}
    }
    private interface Result {void accept(JSONObject value)throws Exception;}
    private void run(Sheet sheet,String label,Callable<JSONObject> work,Result result){
        sheet.status.setText(label+"…");queue.execute(()->{try{JSONObject value=work.call();runOnUiThread(()->{if(isDestroyed()||!sheet.dialog.isShowing())return;try{sheet.status.setText("");result.accept(value);}catch(Exception e){sheet.status.setText(message(e));}});}
            catch(Exception|LinkageError error){runOnUiThread(()->{if(isDestroyed()||!sheet.dialog.isShowing())return;sheet.status.setText(message(error));sheet.status.setTextColor(UiKit.AMBER);});}});
    }
    private String message(Throwable error){String raw=error.getMessage();if(raw==null||raw.trim().isEmpty())return "No se pudo completar la consulta. Puedes intentarlo otra vez.";return raw.split("\\n",2)[0];}
    private EditText field(LinearLayout parent,String label,String hint,String value,boolean multiline){
        parent.addView(text(label,13,UiKit.MUTED),gap(-1,-2,10));EditText e=new EditText(this);e.setTextColor(UiKit.TEXT);e.setHintTextColor(UiKit.MUTED);e.setTextSize(UiKit.font(this,16));e.setBackground(UiKit.shape(this,UiKit.RAISED,10));e.setPadding(dp(12),dp(10),dp(12),dp(10));e.setMinHeight(dp(50));e.setHint(hint);e.setText(value);e.setContentDescription(label);
        e.setInputType(InputType.TYPE_CLASS_TEXT|(multiline?InputType.TYPE_TEXT_FLAG_MULTI_LINE:InputType.TYPE_TEXT_FLAG_CAP_SENTENCES));e.setSingleLine(!multiline);if(multiline){e.setMinLines(3);e.setMaxLines(7);}parent.addView(e,gap(-1,-2,4));return e;
    }
    private void showMemory(){
        Sheet sheet=new Sheet("Memoria personal");EditText search=field(sheet.body,"Buscar","Nombre o palabra","",false);search.setId(0x5804020);
        LinearLayout results=column();Button find=button("Buscar en la memoria",0x5804021,true,()->loadMemory(sheet,results,search.getText().toString().trim()));sheet.body.addView(find,gap(-1,-2,8));sheet.body.addView(results,gap(-1,-2,5));
        sheet.show();loadMemory(sheet,results,"");
    }
    private void loadMemory(Sheet sheet,LinearLayout target,String query){
        run(sheet,"Consultando la memoria actual",()->U03Runtime.operation(getApplicationContext(),"conversation",object("action","personal_memory","query",query).toString()),data->{
            target.removeAllViews();JSONArray facts=data.optJSONArray("facts"),rules=data.optJSONArray("rules");int nf=facts==null?0:facts.length(),nr=rules==null?0:rules.length();
            target.addView(text(nf+" hechos · "+nr+" reglas",13,UiKit.ACCENT),gap(-1,-2,10));
            if(nf+nr==0){card(target,"Aún no hay recuerdos aquí",query.isEmpty()?"Puedes enseñarle un hecho o una regla desde Entrenar.":"Prueba con otra palabra o consulta la memoria sin filtro.");return;}
            for(int i=0;i<nf;i++){
                JSONObject f=facts.optJSONObject(i);if(f==null)continue;boolean predicted=f.optString("source").equals("native_VQC_projection");
                String body=f.optString("text");if(body.isEmpty())body=f.optString("subject")+" "+f.optString("predicate")+" "+String.valueOf(f.opt("value"));
                card(target,body,predicted?"Resultado calculado por el modelo; no equivale a un dato verificado del mundo.":"Hecho guardado en la memoria que estás usando.");
            }
            for(int i=0;i<nr;i++){JSONObject rule=rules.optJSONObject(i);if(rule==null)continue;card(target,rule.optString("text","Si es "+rule.optString("antecedent")+", entonces es "+rule.optString("consequence")),"Regla guardada.");}
        });
    }
    private void showSessions(){
        Sheet sheet=new Sheet("Sesiones y copias");sheet.show();
        run(sheet,"Leyendo tus sesiones",()->U03Runtime.operation(getApplicationContext(),"training",object("action","status").toString()),data->{
            JSONArray rows=data.optJSONArray("sessions");sheet.body.removeAllViews();
            if(rows==null||rows.length()==0)card(sheet.body,"Tu primera sesión","Crea una sesión para enseñarle algo. Sus lecciones y resultados quedarán guardados aquí.");
            else for(int i=0;i<rows.length();i++){
                JSONObject s=rows.optJSONObject(i);if(s==null)continue;String id=s.optString("session_id");
                LinearLayout c=card(sheet.body,s.optString("title","Sesión"),sessionState(s)+"\n"+s.optInt("training_count")+" pasos de enseñanza · "+s.optInt("holdout_count")+" pruebas reservadas");
                action(c,"Abrir sesión",0,false,()->{sheet.dialog.dismiss();openTraining(0,id,false);});
                action(c,"Resultados, copia y exportación",0,false,()->{sheet.dialog.dismiss();openTraining(3,id,false);});
            }
            action(sheet.body,"Crear una sesión",0,true,()->{sheet.dialog.dismiss();openTraining(0,null,false);});
        });
    }
    private void showPreferences(){
        Sheet sheet=new Sheet("Preferencias");sheet.container.setId(0x5804034);LinearLayout read=card(sheet.body,"Tamaño del texto","Este ajuste cambia la lectura de la conversación, el modelo y el entrenamiento.");
        RadioGroup sizes=new RadioGroup(this);sizes.setOrientation(RadioGroup.VERTICAL);float current=settings().getFloat("font_scale",1f);String[] labels={"Normal","Grande","Muy grande"};float[] factors={1f,1.15f,1.3f};
        for(int i=0;i<labels.length;i++){RadioButton b=new RadioButton(this);b.setId(0x5804030+i);b.setText(labels[i]);b.setTextSize(UiKit.font(this,16));b.setTextColor(UiKit.TEXT);b.setMinHeight(dp(50));b.setButtonTintList(android.content.res.ColorStateList.valueOf(UiKit.ACCENT));sizes.addView(b);if(Math.abs(current-factors[i])<.05f)b.setChecked(true);}
        read.addView(sizes,gap(-1,-2,8));sizes.setOnCheckedChangeListener((group,id)->{int at=id-0x5804030;if(at>=0&&at<factors.length){settings().edit().putFloat("font_scale",factors[at]).apply();sheet.dialog.dismiss();build();}});
        LinearLayout details=card(sheet.body,"Informe de mi modelo","Exporta el estado y sus comprobantes para revisar una incidencia o comparar versiones. Los entrenamientos completos se exportan desde cada sesión.");
        action(details,"Exportar informe del modelo",0x5804033,false,()->exportModelReport(sheet));
        sheet.show();
    }
    private void exportModelReport(Sheet sheet){
        run(sheet,"Preparando el informe",()->{JSONObject state=U03Runtime.status(getApplicationContext());return object("schema","BBYQ-0-personal-model-report-v1","name","BBY Q 0","owner",settings().getString("owner_name","X"),"created_at_ms",System.currentTimeMillis(),"state",state,"diagnostics",U03Runtime.diagnostics(getApplicationContext()));},report->{exportText=report.toString(2);exportName="BBY-Q-0-informe-del-modelo.json";saveReport();});
    }
    private void showAdvanced(){
        Sheet sheet=new Sheet("Herramientas avanzadas");sheet.container.setId(0x5804045);
        card(sheet.body,"Estado y comprobantes","Estas herramientas muestran los detalles del modelo y ejecutan pruebas concretas. Los experimentos conservan su alcance indicado.");
        action(sheet.body,"Panel completo C00–C17",0x5804040,false,this::showCycles);
        action(sheet.body,"Estado técnico del modelo",0,false,()->run(sheet,"Consultando el estado",()->U03Runtime.status(getApplicationContext()),r->showReport("Estado técnico",r)));
        action(sheet.body,"Diagnóstico de bibliotecas",0x5804041,false,()->showReport("Diagnóstico de bibliotecas",U03Runtime.diagnostics(getApplicationContext())));
        action(sheet.body,"Informes de ejecución",0,false,()->run(sheet,"Leyendo informes",()->U03Runtime.operation(getApplicationContext(),"reports","{}"),r->showReport("Informes de ejecución",r)));
        action(sheet.body,"Laboratorios y operaciones",0x5804042,false,this::showTools);
        action(sheet.body,"Exportar informe del modelo",0,false,()->exportModelReport(sheet));sheet.show();
    }
    private void showCycles(){
        Sheet sheet=new Sheet("Panel C00–C17");
        String[][] rows={
            {"C00 · Auditoría","Medición de ejecución y comprobantes."},
            {"C01 · Runtime XI","Ejecución nativa y pruebas de transporte."},
            {"C02 · Persistencia","Laboratorio de guardado transaccional y recuperación."},
            {"C03 · Caché","Caché autenticada en las sesiones."},
            {"C04 · Planificador","Apertura de los bancos que requiere cada tarea."},
            {"C05 · Codificador","Representación auxiliar junto al lector original."},
            {"C06 · Semántica","Análisis adicional; su salida no sustituye al lector principal."},
            {"C07 · Metacognición","Evaluación de evidencia estructurada disponible a petición."},
            {"C08 · Aprendizaje activo","Comparación del candidato y petición de verificación; sin activación automática."},
            {"C09 · Memoria","Consulta de la misma memoria personal."},
            {"C10 · Razonamiento","Planificación y demostración nativas disponibles en operaciones aisladas."},
            {"C11 · Aprendizaje conjunto","Correcciones nativas en sesiones de entrenamiento."},
            {"C12 · Entre bloques","Ejercicios y comparación de resultados del aprendizaje."},
            {"C13 · Optimización","Experimento de caché; no habilitado globalmente."},
            {"C14 · Evaluación","Laboratorio de perfilado y comparación al retirar componentes."},
            {"C15 · Concurrencia","Laboratorio de lectores, escritores y recuperación."},
            {"C16 · Android","Integración móvil de las capacidades y laboratorios."},
            {"C17 · Entrenamiento personal","Sesiones, pruebas, activación explícita, copias y exportación."}
        };
        for(String[] row:rows)card(sheet.body,row[0],row[1]);
        card(sheet.body,"Conexiones pendientes","La GPU virtual y QSSD no están conectadas al cálculo de esta aplicación. Los experimentos no se activan como modelo personal por el simple hecho de existir.");
        sheet.show();
    }
    private void showTools(){
        Sheet sheet=new Sheet("Operaciones y laboratorios");
        String[] labels={"Memoria C09 · diagnóstico","Planificar C10","Demostrar C10","Semántica C06","Evidencia C07 / C08","Transporte C01","Persistencia C02","Aprendizaje C11 · laboratorio","Entre bloques C12 · laboratorio","Probar candidato C11 / C12","Caché C13","Perfil y ablaciones C14","Estrés Android C15","Capacidades conectadas"};
        String[] names={"memory","plan","prove","semantic","evidence","transport","persistence","c11","c12","candidate","cache","profile","stress","capabilities"};
        Spinner choose=new Spinner(this);choose.setId(0x5804043);choose.setContentDescription("Operación avanzada");ArrayAdapter<String> list=new ArrayAdapter<String>(this,android.R.layout.simple_spinner_item,labels){
            @Override public View getView(int p,View v,android.view.ViewGroup g){TextView t=(TextView)super.getView(p,v,g);t.setTextColor(UiKit.TEXT);t.setTextSize(UiKit.font(ModelActivity.this,14));t.setSingleLine(false);t.setMinHeight(dp(54));return t;}
            @Override public View getDropDownView(int p,View v,android.view.ViewGroup g){TextView t=(TextView)super.getDropDownView(p,v,g);t.setTextColor(UiKit.TEXT);t.setBackgroundColor(UiKit.RAISED);t.setTextSize(UiKit.font(ModelActivity.this,14));t.setSingleLine(false);t.setMinHeight(dp(50));return t;}
        };list.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);choose.setAdapter(list);sheet.body.addView(choose,gap(-1,-2,8));
        EditText input=field(sheet.body,"Argumentos técnicos (JSON)","{}","{}",true);
        TextView note=text("C11–C15 aquí ejecutan experimentos aislados. Para enseñar a tu modelo y activarlo en la conversación, usa Entrenar BBY Q.",13,UiKit.MUTED);sheet.body.addView(note,gap(-1,-2,8));
        Button execute=button("Ejecutar operación",0x5804044,false,()->{
            final int selection=choose.getSelectedItemPosition();final String name=names[selection],title=labels[selection];final String request=input.getText().toString().trim().isEmpty()?"{}":input.getText().toString().trim();
            try{new JSONObject(request);}catch(Exception e){input.setError("Escribe un objeto JSON válido.");return;}
            run(sheet,"Ejecutando "+title,()->U03Runtime.operation(getApplicationContext(),name,request),r->showReport(title,r));
        });sheet.body.addView(execute,gap(-1,-2,12));
        choose.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){public void onNothingSelected(AdapterView<?> p){}public void onItemSelected(AdapterView<?> p,View v,int at,long id){String name=names[at];JSONObject preset=object();if(name.equals("plan"))preset=object("observation","Nara","association","Faro Azul","position",3);else if(name.equals("prove"))preset=object("observation","Nara");else if(name.equals("semantic"))preset=object("text","define Prisma no Brisa");else if(name.equals("evidence"))preset=object("query",object("subject","Móvil","predicate","operativo"),"evidence",new JSONArray());else if(name.equals("candidate"))preset=object("cycle","c12","text","calcula 7 + 3");input.setText(preset.toString());}});
        sheet.show();
    }
    private void showReport(String title,JSONObject report){
        Sheet sheet=new Sheet(title);TextView body=text(pretty(report),13,UiKit.TEXT);body.setTypeface(Typeface.MONOSPACE);body.setTextIsSelectable(true);sheet.body.addView(body,gap(-1,-2,10));
        action(sheet.body,"Exportar este informe",0,false,()->{exportText=pretty(report);exportName="BBY-Q-0-informe.json";saveReport();});sheet.show();
    }
    private String pretty(JSONObject value){try{return value.toString(2);}catch(Exception e){return value.toString();}}
    private void saveReport(){Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,exportName);startActivityForResult(i,EXPORT_REPORT);}
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request!=EXPORT_REPORT||result!=RESULT_OK||data==null||data.getData()==null)return;
        final android.net.Uri destination=data.getData();final String document=exportText;final Context app=getApplicationContext();queue.execute(()->{
            try(OutputStream out=app.getContentResolver().openOutputStream(destination)){if(out==null)throw new java.io.IOException("No se pudo abrir el destino.");out.write(document.getBytes(StandardCharsets.UTF_8));runOnUiThread(()->Toast.makeText(this,"Informe guardado en el destino elegido.",Toast.LENGTH_LONG).show());}
            catch(Exception e){runOnUiThread(()->Toast.makeText(this,"No se pudo guardar el informe: "+message(e),Toast.LENGTH_LONG).show());}
        });
    }
}
