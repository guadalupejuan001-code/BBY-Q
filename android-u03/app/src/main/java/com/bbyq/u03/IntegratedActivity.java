package com.bbyq.u03;

import android.app.*;
import android.content.*;
import android.os.Bundle;
import android.os.Build;
import android.graphics.Insets;
import android.graphics.Typeface;
import android.view.Gravity;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowManager;
import android.widget.*;
import org.json.*;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;

/** All displayed cycle actions invoke executable native/mobile routes. */
public final class IntegratedActivity extends Activity {
    private static final int BG=0xff10151e,FG=0xffedf6f5,PANEL=0xff1d2936,ACCENT=0xff7adbc4,MUTED=0xff9aafc0;
    private final ExecutorService queue=Executors.newSingleThreadExecutor();
    private LinearLayout transcript;
    private ScrollView scroll;
    private EditText input;
    private Spinner mode;
    private TextView state;
    private Button execute;
    private boolean busy=false,ready=false;
    private String exportText="";
    private final String[] labels={"Conversación XI","Memoria C09","Planificar C10","Demostrar C10","Semántica C06","Evidencia C07 / C08","Transporte C01","Persistencia C02","Aprendizaje C11","Entre bloques C12","Probar candidato C11 / C12","Caché C13","Perfil y ablaciones C14","Estrés Android C15","Capacidades conectadas","Informes de esta sesión","Diagnóstico de bibliotecas"};
    private final String[] actions={"chat","memory","plan","prove","semantic","evidence","transport","persistence","c11","c12","candidate","cache","profile","stress","capabilities","reports","diagnostics"};
    private int dp(int x){return Math.round(x*getResources().getDisplayMetrics().density);}
    private TextView text(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
    private Button button(String s){Button b=new Button(this);b.setText(s);b.setAllCaps(false);b.setTextSize(12);b.setSingleLine(true);b.setMinWidth(0);b.setMinimumWidth(0);b.setPadding(dp(4),dp(4),dp(4),dp(4));b.setTextColor(FG);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PANEL));return b;}
    private LinearLayout vertical(){LinearLayout x=new LinearLayout(this);x.setOrientation(LinearLayout.VERTICAL);return x;}
    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        LinearLayout root=vertical();root.setBackgroundColor(BG);root.setPadding(dp(14),dp(14),dp(14),dp(12));
        // Android 15 enforces edge-to-edge at target 35: keep real controls
        // above navigation/keyboard and below status bar, not underneath them.
        if(Build.VERSION.SDK_INT>=30){
            getWindow().setDecorFitsSystemWindows(false);
            root.setOnApplyWindowInsetsListener((view,insets)->{
                Insets bars=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
                Insets ime=insets.getInsets(WindowInsets.Type.ime());
                view.setPadding(dp(14)+bars.left,dp(14)+bars.top,dp(14)+bars.right,dp(12)+Math.max(bars.bottom,ime.bottom));
                return insets;
            });
        }else root.setFitsSystemWindows(true);
        TextView title=text("BBY Q · U03 Integrado",23,FG);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);root.addView(title);
        state=text("Verificando núcleo, checkpoints y bibliotecas…",12,MUTED);state.setId(0x5802001);root.addView(state);
        mode=new Spinner(this);mode.setId(0x5802002);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,labels);
        mode.setAdapter(adapter);root.addView(mode,new LinearLayout.LayoutParams(-1,dp(48)));
        scroll=new ScrollView(this);transcript=vertical();scroll.addView(transcript);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout shortcuts=new LinearLayout(this);
        for(String name:new String[]{"Misión","Aprender","Ciclos","Exportar"}){
            Button b=button(name);shortcuts.addView(b,new LinearLayout.LayoutParams(0,dp(48),1));
            b.setOnClickListener(v->{
                if(name.equals("Misión")){mode.setSelection(0);input.setText("guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3");}
                else if(name.equals("Aprender")){mode.setSelection(0);input.setText("aprende de la última tarea");}
                else if(name.equals("Ciclos")){mode.setSelection(14);input.setText("{}");}
                else export();
            });
        }root.addView(shortcuts);
        input=new EditText(this);input.setId(0x5802003);input.setTextColor(FG);input.setHintTextColor(MUTED);input.setTextSize(14);
        input.setMinLines(2);input.setMaxLines(5);input.setHint("Escribe una petición XI");root.addView(input,new LinearLayout.LayoutParams(-1,-2));
        execute=button("Ejecutar");execute.setId(0x5802004);execute.setTextColor(BG);execute.setBackgroundTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        root.addView(execute,new LinearLayout.LayoutParams(-1,dp(48)));execute.setOnClickListener(v->submit());
        setContentView(root);root.requestApplyInsets();
        mode.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(AdapterView<?> p){}
            public void onItemSelected(AdapterView<?> p,View v,int index,long id){preset(index);}
        });
        add("Integración","Memoria, planificación y análisis tienen rutas reales. Los laboratorios C11–C15 trabajan en bases separadas; no sustituyen tu modelo personal.");
        queue.execute(()->{
            try{JSONObject s=U03Runtime.start(getApplicationContext());ready=true;
                runOnUiThread(()->{state.setText("U02 + C03–C10 listos · 7 bancos autenticados");state.setTextColor(ACCENT);});
            }catch(Exception|LinkageError e){
                exportText=U03Runtime.diagnostics(getApplicationContext()).toString();
                runOnUiThread(()->{state.setText("Arranque fallido: abre Diagnóstico de bibliotecas");state.setTextColor(0xffffa0a0);add("Error real",e.toString());mode.setSelection(16);});
            }
        });
    }
    private void preset(int index){
        String a=actions[index];
        if(a.equals("chat")){input.setText("");input.setHint("calcula 7 + 3");}
        else if(a.equals("plan"))input.setText("{\"observation\":\"Nara\",\"association\":\"Faro Azul\",\"position\":3}");
        else if(a.equals("prove"))input.setText("{\"observation\":\"Nara\"}");
        else if(a.equals("semantic"))input.setText("{\"text\":\"define Prisma no Brisa\"}");
        else if(a.equals("evidence"))input.setText("{\"query\":{\"subject\":\"Móvil\",\"predicate\":\"operativo\"},\"evidence\":[]}");
        else if(a.equals("candidate"))input.setText("{\"cycle\":\"c12\",\"text\":\"calcula 7 + 3\"}");
        else input.setText("{}");
    }
    private void add(String name,String body){
        TextView t=text(name+"\n"+body,14,FG);t.setTextIsSelectable(true);t.setPadding(dp(10),dp(10),dp(10),dp(10));
        t.setBackgroundColor(PANEL);LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.setMargins(0,dp(8),0,dp(4));transcript.addView(t,p);
        scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));
    }
    private void submit(){
        if(busy)return;
        String action=actions[mode.getSelectedItemPosition()];
        String content=input.getText().toString().trim();
        if(!action.equals("diagnostics")&&!ready){add("Estado","El núcleo aún no está listo. El diagnóstico funciona aunque falle una biblioteca.");return;}
        if(action.equals("chat")&&content.isEmpty())return;
        if(!action.equals("chat"))try{new JSONObject(content.isEmpty()?"{}":content);}catch(JSONException e){add("Entrada","Los argumentos deben ser un objeto JSON válido; no se ejecutó ninguna operación.");return;}
        busy=true;execute.setEnabled(false);state.setText("Ejecutando "+labels[mode.getSelectedItemPosition()]+"…");
        add("Solicitud",action.equals("chat")?content:labels[mode.getSelectedItemPosition()]);
        queue.execute(()->{
            try{
                JSONObject r;
                if(action.equals("diagnostics"))r=U03Runtime.diagnostics(getApplicationContext());
                else if(action.equals("chat"))r=U03Runtime.turn(getApplicationContext(),UUID.randomUUID().toString(),content,"");
                else r=U03Runtime.operation(getApplicationContext(),action,content.isEmpty()?"{}":content);
                exportText=r.toString(2);
                String show=action.equals("chat")?r.optString("reply")+"\n\nSemántica C06: "+r.optJSONObject("C06")+"\nMemoria C09: "+r.optJSONObject("C09"):exportText;
                runOnUiThread(()->add("Resultado real",show));
            }catch(Exception|LinkageError e){exportText=e.toString()+"\n"+U03Runtime.diagnostics(getApplicationContext());runOnUiThread(()->add("Error de ejecución",e.toString()));}
            finally{runOnUiThread(()->{busy=false;execute.setEnabled(true);state.setText(ready?"Disponible · informes exportables · sin promoción automática":"Abre Diagnóstico de bibliotecas");});}
        });
    }
    private void export(){
        if(exportText.isEmpty())exportText=U03Runtime.diagnostics(this).toString();
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");i.putExtra(Intent.EXTRA_TITLE,"BBY-Q-diagnostico.json");startActivityForResult(i,510);
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if(request==510&&result==RESULT_OK&&data!=null&&data.getData()!=null){
            try(OutputStream out=getContentResolver().openOutputStream(data.getData())){if(out==null)throw new java.io.IOException("Sin destino");out.write(exportText.getBytes(StandardCharsets.UTF_8));add("Exportado","El informe se guardó en el destino elegido.");}
            catch(Exception e){add("Error de exportación",e.toString());}
        }
    }
    @Override protected void onDestroy(){super.onDestroy();queue.shutdown();}
}
