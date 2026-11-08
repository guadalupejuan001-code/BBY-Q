package com.bbyq.u03;

import android.app.Activity;
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
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Functional native BBY Q U03 Android console (not the historical E02 app). */
public final class MainActivity extends Activity {
    private static final int BG=0xff10151e, PANEL=0xff1b2632, BORDER=0xff2b3e4a;
    private static final int WHITE=0xffeff8f7, MUTED=0xff9db3c0, ACCENT=0xff70e0c5;
    private final ExecutorService queue=Executors.newSingleThreadExecutor();
    private final AtomicBoolean running=new AtomicBoolean(false);
    private LinearLayout log;
    private ScrollView scroll;
    private TextView status;
    private EditText entry;
    private Button send;
    private String lastOriginalJson;
    private boolean ready=false;

    private int dp(float v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private GradientDrawable background(int color,int radius) {
        GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(radius));
        return d;
    }
    private TextView txt(String content,int size,int color) {
        TextView t=new TextView(this);t.setText(content);t.setTextColor(color);t.setTextSize(size);return t;
    }
    private LinearLayout col() {
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);return box;
    }
    private Button button(String name){
        Button b=new Button(this);b.setText(name);b.setAllCaps(false);b.setTextSize(13);
        b.setTextColor(WHITE);b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PANEL));
        return b;
    }
    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        LinearLayout root=col();root.setBackgroundColor(BG);
        root.setPadding(dp(14),dp(12),dp(14),dp(12));
        LinearLayout header=new LinearLayout(this);
        header.setGravity(Gravity.CENTER_VERTICAL);header.setPadding(dp(4),dp(2),dp(4),dp(14));
        TextView emblem=txt("Q",26,BG);emblem.setGravity(Gravity.CENTER);
        emblem.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        emblem.setBackground(background(ACCENT,14));
        header.addView(emblem,new LinearLayout.LayoutParams(dp(48),dp(48)));
        LinearLayout title=col();title.setPadding(dp(12),0,0,0);
        TextView name=txt("BBY Q",24,WHITE);name.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        title.addView(name);title.addView(txt("U03 · XI / Ether · C00–C15",12,MUTED));
        header.addView(title,new LinearLayout.LayoutParams(0,-2,1));
        Button info=button("Estado");
        info.setContentDescription("Ver estado real XI y siete bancos");
        header.addView(info,new LinearLayout.LayoutParams(dp(88),dp(45)));
        info.setOnClickListener(v->showNativeStatus());
        root.addView(header);
        status=txt("Preparando runtime U02 auténtico…",12,MUTED);
        status.setId(0x5801001);
        root.addView(status);
        scroll=new ScrollView(this);
        scroll.setFillViewport(true);
        log=col();log.setPadding(0,dp(15),0,dp(20));
        scroll.addView(log);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));

        LinearLayout examples=new LinearLayout(this);
        examples.setGravity(Gravity.CENTER);
        for(String label:new String[]{"Misión","Calcular","Aprender","Ciclos"}){
            Button b=button(label);
            LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(46),1);
            p.setMargins(dp(2),0,dp(2),dp(9));examples.addView(b,p);
            b.setOnClickListener(v->{
                if(label.equals("Ciclos"))showCycles();
                else if(label.equals("Misión"))entry.setText("guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3");
                else if(label.equals("Calcular"))entry.setText("calcula 7 + 3");
                else entry.setText("aprende de la última tarea");
            });
        }
        root.addView(examples);
        LinearLayout composer=new LinearLayout(this);
        composer.setGravity(Gravity.CENTER_VERTICAL);
        composer.setPadding(dp(8),dp(4),dp(6),dp(4));
        composer.setBackground(background(PANEL,19));
        entry=new EditText(this);
        entry.setHint("Escribe una petición XI para BBY Q…");
        entry.setTextColor(WHITE);entry.setHintTextColor(MUTED);
        entry.setTextSize(15);entry.setBackgroundColor(Color.TRANSPARENT);
        entry.setMinLines(1);entry.setMaxLines(5);
        entry.setId(0x5801002);
        composer.addView(entry,new LinearLayout.LayoutParams(0,-2,1));
        send=button("Enviar");
        send.setTextColor(BG);
        send.setBackgroundTintList(android.content.res.ColorStateList.valueOf(ACCENT));
        send.setId(0x5801003);
        composer.addView(send,new LinearLayout.LayoutParams(dp(92),dp(52)));
        send.setOnClickListener(v->send());
        root.addView(composer);
        setContentView(root);
        send.setEnabled(false);
        if(saved!=null)entry.setText(saved.getString("draft",""));
        bubble("Sistema","Esta edición ejecuta U02 real con siete bancos XI. C11 y C12 se conservaron como ensayos no promocionados; GPU-VIRTUAL aún no se conectó al cálculo.",false);
        queue.execute(()->{
            try {
                JSONObject report=U03Runtime.start(getApplicationContext());
                ready=true;
                runOnUiThread(()->{
                    if(isDestroyed())return;
                    status.setText("● U02 original · "+report.optInt("banks")+" bancos XI · estado SHA verificado");
                    status.setTextColor(ACCENT);send.setEnabled(true);
                    bubble("BBY Q","Motor original U02 listo. Puedes consultar, clasificar, resolver misiones y aplicar aprendizaje supervisado explícito.",false);
                });
            } catch(Exception e) {
                runOnUiThread(()->{
                    status.setText("Error al iniciar U02: "+e.getMessage());
                    status.setTextColor(0xffff9090);
                    bubble("Error","La identidad original o el runtime XI no se pudo verificar: "+e.getMessage(),false);
                });
            }
        });
    }
    @Override protected void onSaveInstanceState(Bundle b) {
        b.putString("draft",entry==null?"":entry.getText().toString());
        super.onSaveInstanceState(b);
    }
    private void bubble(String who,String body,boolean user) {
        LinearLayout item=col();item.setPadding(dp(13),dp(10),dp(13),dp(10));
        item.setBackground(background(user?BORDER:PANEL,13));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);
        p.setMargins(user?dp(40):0,0,user?0:dp(28),dp(10));
        TextView speaker=txt(who,12,user?ACCENT:MUTED);
        speaker.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        item.addView(speaker);
        TextView content=txt(body,15,WHITE);content.setPadding(0,dp(4),0,0);
        content.setTextIsSelectable(true);
        item.addView(content);
        log.addView(item,p);
        scroll.post(()->scroll.fullScroll(View.FOCUS_DOWN));
    }
    private void updateBusy(boolean busy,String label) {
        running.set(busy);
        runOnUiThread(()->{
            send.setEnabled(!busy && ready);
            status.setText(busy?label:"● U02 XI disponible sin conexión");
        });
    }
    private void send() {
        if(!ready || !running.compareAndSet(false,true))return;
        String msg=entry.getText().toString().trim();
        if(msg.isEmpty()){running.set(false);return;}
        entry.setText("");
        bubble("Tú",msg,true);
        send.setEnabled(false);
        status.setText("Calculando con C1 · VQC · QRL · QMemory · Entity · QChat…");
        String id=UUID.randomUUID().toString();
        queue.execute(()->{
            try {
                JSONObject out=U03Runtime.turn(getApplicationContext(),id,msg,"");
                lastOriginalJson=out.toString(2);
                runOnUiThread(()->bubble("BBY Q · XI",out.optString("reply","Sin respuesta XI"),false));
            } catch(Exception e) {
                runOnUiThread(()->bubble("Error XI","Falló la operación original: "+e.getMessage()+
                    ". No se fabricó una respuesta y SQLite debe permanecer coherente.",false));
            } finally {updateBusy(false,"");}
        });
    }
    private void showNativeStatus() {
        if(!ready){bubble("Sistema","U02 todavía no está inicializado.",false);return;}
        queue.execute(()->{
            try {
                JSONObject s=U03Runtime.status(getApplicationContext());
                JSONObject snapshot=s.getJSONObject("snapshot");
                String msg="Modelo: "+s.optString("entity")+
                    "\n7 bancos XI: "+s.optInt("bank_count")+
                    "\nRevisión SQLite: "+snapshot.optInt("revision")+
                    "\nTareas: "+snapshot.optInt("tasks")+
                    "\nFeedback: "+snapshot.optInt("feedback")+
                    "\nC11/C12: experimentales, sin promoción"+
                    "\nC13: caché desactivada"+
                    "\nGPU virtual: aún no adaptada al backend de IA";
                runOnUiThread(()->bubble("Estado real",msg,false));
            } catch(Exception e){runOnUiThread(()->bubble("Error",e.toString(),false));}
        });
    }
    private void showCycles() {
        queue.execute(()->{
            try {
                String p=U03Runtime.panel(getApplicationContext());
                runOnUiThread(()->new AlertDialog.Builder(this)
                    .setTitle("C00–C15 · Evidencia histórica")
                    .setMessage(p.length()>9500?p.substring(0,9500):p)
                    .setPositiveButton("Cerrar",(d,w)->{})
                    .setNeutralButton("Copiar",(d,w)->{
                        ((android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE))
                            .setPrimaryClip(ClipData.newPlainText("BBY Q U03",p));
                    }).show());
            } catch(Exception e){runOnUiThread(()->bubble("Error",e.toString(),false));}
        });
    }
    @Override protected void onDestroy(){super.onDestroy();queue.shutdown();}
}
