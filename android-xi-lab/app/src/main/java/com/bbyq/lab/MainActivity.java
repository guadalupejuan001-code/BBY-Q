package com.bbyq.lab;

import android.app.Activity;
import android.os.Bundle;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.content.res.ColorStateList;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.text.InputType;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Small real Android runtime for native XI experiments; no simulated buttons. */
public final class MainActivity extends Activity {
    private static final int BG=Color.rgb(9,13,24),PANEL=Color.rgb(20,27,43),
        LINE=Color.rgb(46,59,83),INK=Color.rgb(237,241,250),MUTED=Color.rgb(153,169,193),
        ACCENT=Color.rgb(112,197,216),ACTION=Color.rgb(46,75,105);
    private final ExecutorService engine=Executors.newSingleThreadExecutor();
    private final AtomicBoolean busy=new AtomicBoolean(false);
    private LabEngine lab;
    private EditText command,topic,reward;
    private Spinner action;
    private TextView console;
    private int dp(float value){return (int)(getResources().getDisplayMetrics().density*value+0.5f);}
    private GradientDrawable shape(int color,int radius,boolean border) {
        GradientDrawable g=new GradientDrawable();
        g.setColor(color);
        g.setCornerRadius(dp(radius));
        if(border)g.setStroke(dp(1),LINE);
        return g;
    }
    private TextView label(String text,int size,int color,boolean bold) {
        TextView v=new TextView(this);
        v.setText(text);v.setTextSize(size);v.setTextColor(color);
        if(bold)v.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        return v;
    }
    private LinearLayout vertical(){
        LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);return v;
    }
    private LinearLayout.LayoutParams margin(int top){
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.topMargin=dp(top);return p;
    }
    private EditText input(String value,String hint){
        EditText e=new EditText(this);e.setText(value);e.setHint(hint);e.setSingleLine(false);
        e.setTextSize(15);e.setTextColor(INK);e.setHintTextColor(MUTED);
        e.setBackground(shape(PANEL,12,true));e.setPadding(dp(14),dp(12),dp(14),dp(12));
        return e;
    }
    private Button button(String name,boolean primary){
        Button b=new Button(this);
        b.setText(name);b.setAllCaps(false);b.setTextColor(INK);b.setTextSize(13);
        b.setBackgroundTintList(ColorStateList.valueOf(primary?ACTION:PANEL));
        b.setPadding(dp(6),dp(4),dp(6),dp(4));b.setMinHeight(dp(46));
        return b;
    }
    private void addLine(LinearLayout parent,String text,int top,int color,int size,boolean bold){
        parent.addView(label(text,size,color,bold),margin(top));
    }
    private void quick(LinearLayout card,String first,String second){
        LinearLayout row=new LinearLayout(this);row.setOrientation(LinearLayout.HORIZONTAL);
        for(String text:new String[]{first,second}){
            Button b=button(text,false);
            LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(48),1);
            p.setMargins(dp(2),dp(4),dp(2),0);
            row.addView(b,p);
            b.setOnClickListener(v->{
                String cmd="quantum "+text;
                command.setText(cmd);runCmd(cmd);
            });
        }
        card.addView(row,margin(0));
    }
    private LinearLayout card(LinearLayout parent){
        LinearLayout c=vertical();
        c.setBackground(shape(PANEL,16,true));c.setPadding(dp(16),dp(12),dp(16),dp(16));
        parent.addView(c,margin(16));return c;
    }
    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        lab=new LabEngine(this);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(BG);
        LinearLayout root=vertical();root.setPadding(dp(18),dp(22),dp(18),dp(28));
        scroll.addView(root);setContentView(scroll);
        addLine(root,"REVERSE / BBY Q",2,ACCENT,13,true);
        addLine(root,"XI LAB",6,INK,31,true);
        addLine(root,"C13 · Ejecución nativa Android · Estado Ether privado",3,MUTED,12,false);
        LinearLayout commands=card(root);
        addLine(commands,"MOTORES VQC + QRL",2,INK,15,true);
        addLine(commands,"Las órdenes se interpretan en XI. Los botones ejecutan programas reales.",5,MUTED,12,false);
        command=input("quantum estado","Escribe un comando XI");
        commands.addView(command,margin(12));
        Button execute=button("Ejecutar comando",true);
        commands.addView(execute,margin(8));
        execute.setOnClickListener(v->runCmd(command.getText().toString()));
        quick(commands,"estado","entrena xor");
        quick(commands,"evalua","entrena agente");
        quick(commands,"clasifica 0 1","planea 1 0");
        quick(commands,"entrena xnor","ayuda");

        LinearLayout cognitive=card(root);
        addLine(cognitive,"POLÍTICA C12 · OBSERVACIÓN",2,INK,15,true);
        addLine(cognitive,"P01 reconoce la intención. XI aprende una puntuación Q, pero no modifica respuestas.",5,MUTED,12,false);
        topic=input("Explícame el estado cuántico.","Texto que deseas evaluar");
        cognitive.addView(topic,margin(12));
        Button observe=button("Consultar ruta sugerida",true);
        cognitive.addView(observe,margin(8));
        observe.setOnClickListener(v->runJob("Observación de política",()->lab.observe(topic.getText().toString())));
        addLine(cognitive,"Retroalimentación explícita (no automática)",14,MUTED,12,false);
        LinearLayout row=new LinearLayout(this);row.setGravity(Gravity.CENTER_VERTICAL);
        action=new Spinner(this);action.setBackground(shape(BG,8,true));
        String[] options={"X10 (0)","Memoria P05 (1)","Razón P03 (2)","Componer P04 (3)"};
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,options);
        action.setAdapter(adapter);
        LinearLayout.LayoutParams ap=new LinearLayout.LayoutParams(0,dp(50),3);
        row.addView(action,ap);
        reward=input("80","0–100");reward.setInputType(InputType.TYPE_CLASS_NUMBER);reward.setSingleLine(true);
        LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,dp(50),1);
        rp.leftMargin=dp(8);row.addView(reward,rp);
        cognitive.addView(row,margin(8));
        Button train=button("Entrenar decisión en XI",false);
        cognitive.addView(train,margin(9));
        train.setOnClickListener(v->runJob("Feedback explícito",()->{
            final int r=Integer.parseInt(reward.getText().toString());
            return lab.feedback(topic.getText().toString(),action.getSelectedItemPosition(),r);
        }));

        LinearLayout output=card(root);
        addLine(output,"RESULTADOS / MEMORIA",2,INK,15,true);
        console=label("Listo para ejecutar el núcleo XI. Ningún modelo externo conectado.",13,INK,false);
        console.setTextIsSelectable(true);console.setPadding(dp(4),dp(12),dp(4),dp(4));
        output.addView(console,margin(3));
        addLine(root,"LABORATORIO — No es aún BBY Q X10 completo. El estado aquí no sustituye sesiones del escritorio.",14,MUTED,12,false);
        runJob("C13 BOOT",()->lab.command("quantum estado")); // Safe read-only native preflight.
    }
    private interface Task {String call()throws Exception;}
    private void runCmd(String value){runJob("XI / "+value,()->lab.command(value));}
    private void runJob(String title,Task task){
        if(!busy.compareAndSet(false,true))return;
        console.setText(title+"\nEjecutando el simulador y los programas XI...");
        engine.submit(()->{
            String result;
            try{result=task.call();}
            catch(Exception e){result="ERROR (sin publicar estado): "+e.getMessage();}
            // Android smoke markers carry NO user text or data.
            if(title.equals("C13 BOOT")&&result.startsWith("VQC2 ")&&result.contains("QRL2"))
                android.util.Log.i("BBYQ_XI_C13","BOOT_NATIVE_OK");
            if(title.equals("XI / quantum entrena xor")&&result.startsWith("VQC2 entrenado en XI"))
                android.util.Log.i("BBYQ_XI_C13","VQC_TRAIN_OK");
            if(title.equals("XI / quantum clasifica 0 1")&&result.startsWith("VQC2 Bell"))
                android.util.Log.i("BBYQ_XI_C13","VQC_CLASSIFY_OK");
            if(title.equals("XI / quantum entrena agente")&&result.startsWith("QRL2 XI entrenado"))
                android.util.Log.i("BBYQ_XI_C13","QRL_TRAIN_OK");
            if(title.equals("XI / quantum planea 1 0")&&result.startsWith("QRL2: objetivo=1"))
                android.util.Log.i("BBYQ_XI_C13","QRL_PLAN_OK");
            final String message=title+"\n\n"+result;
            runOnUiThread(()->{console.setText(message);busy.set(false);});
        });
    }
    @Override protected void onDestroy(){
        super.onDestroy();
        engine.shutdown(); // Never interrupt a partially computed but not yet committed transaction.
    }
}
