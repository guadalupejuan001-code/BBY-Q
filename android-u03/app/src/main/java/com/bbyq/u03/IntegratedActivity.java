package com.bbyq.u03;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.view.inputmethod.EditorInfo;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.lang.ref.WeakReference;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** BBY Q 0: a personal conversation first, with its model in a second destination. */
public final class IntegratedActivity extends Activity {
    private static final ExecutorService WORKER=Executors.newSingleThreadExecutor();
    private static volatile WeakReference<IntegratedActivity> visible=new WeakReference<>(null);
    private static volatile boolean working=false,ready=false;
    private static volatile String activityLabel="",failure="",pendingText="";
    private static volatile JSONArray messages=new JSONArray();
    private static volatile JSONObject lastResponse;
    private static final int EXPORT_REQUEST=618;

    private SharedPreferences preferences;
    private LinearLayout root,header,transcript,composer,navigation;
    private ScrollView scroll;
    private EditText input;
    private TextView state;
    private Button send,retry;
    private String styleStamp="",renderStamp="",exportPath="";
    private int restoredScroll=-1;
    private boolean creating=false;

    private int dp(float n){return UiKit.dp(this,n);}
    private static JSONObject args(Object... pairs){
        JSONObject o=new JSONObject();
        try{for(int i=0;i<pairs.length;i+=2)o.put(String.valueOf(pairs[i]),pairs[i+1]);}
        catch(Exception e){throw new IllegalArgumentException(e);}
        return o;
    }
    private static JSONObject conversation(Context context,JSONObject args)throws Exception{
        return U03Runtime.operation(context,"conversation",args.toString());
    }
    private static void publish(){
        IntegratedActivity a=visible.get();
        if(a!=null&&!a.isFinishing()&&!a.isDestroyed())a.runOnUiThread(a::render);
    }
    private LinearLayout.LayoutParams margin(int width,int height,int top){
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(width,height);p.topMargin=dp(top);return p;
    }
    private TextView label(String value,int size,int color){return UiKit.text(this,value,size,color);}
    private String owner(){String v=preferences.getString("owner_name","X").trim();return v.isEmpty()?"X":v;}
    private String style(){
        return owner()+"|"+preferences.getFloat("font_scale",1f)+"|"+preferences.getBoolean("show_suggestions",true);
    }

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);preferences=getSharedPreferences(UiKit.PREFS,MODE_PRIVATE);
        if(saved!=null)restoredScroll=saved.getInt("scroll",-1);
        visible=new WeakReference<>(this);buildScreen();
        if(!working)initialize();
    }
    @Override protected void onResume(){
        super.onResume();visible=new WeakReference<>(this);
        if(preferences!=null&&!style().equals(styleStamp)){persistDraft();buildScreen();}
        render();
    }
    @Override protected void onPause(){persistDraft();super.onPause();}
    @Override protected void onStop(){
        if(visible.get()==this)visible=new WeakReference<>(null);
        super.onStop();
    }
    @Override protected void onSaveInstanceState(Bundle out){
        persistDraft();if(scroll!=null)out.putInt("scroll",scroll.getScrollY());super.onSaveInstanceState(out);
    }

    private void buildScreen(){
        creating=true;styleStamp=style();renderStamp="";
        root=UiKit.column(this);root.setId(0x5802000);root.setBackgroundColor(UiKit.BG);
        header=UiKit.column(this);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);
        top.addView(UiKit.brand(this,40));
        LinearLayout title=UiKit.column(this);
        TextView name=label("BBY Q 0",22,UiKit.TEXT);name.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        name.setLetterSpacing(.035f);title.addView(name);
        if(getResources().getConfiguration().orientation!=Configuration.ORIENTATION_LANDSCAPE){
            TextView subtitle=label("PERSONAL  /  "+owner(),10,UiKit.MUTED);subtitle.setLetterSpacing(.12f);title.addView(subtitle);
        }
        LinearLayout.LayoutParams titleParams=new LinearLayout.LayoutParams(0,-2,1);titleParams.leftMargin=dp(12);top.addView(title,titleParams);
        Button menu=UiKit.button(this,"",false);menu.setId(0x5802012);menu.setContentDescription("Opciones de conversación");
        menu.setCompoundDrawablesRelativeWithIntrinsicBounds(UiKit.icon(this,"more",UiKit.MUTED),null,null,null);
        menu.setPadding(dp(13),0,dp(11),0);menu.setOnClickListener(v->showMenu(menu));top.addView(menu,new LinearLayout.LayoutParams(dp(48),dp(48)));
        header.addView(top);
        LinearLayout statusRow=new LinearLayout(this);statusRow.setGravity(Gravity.CENTER_VERTICAL);statusRow.setPadding(dp(3),dp(5),0,dp(4));
        state=label("Preparando tu BBY Q…",11,UiKit.MUTED);state.setId(0x5802001);
        state.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        statusRow.addView(state,new LinearLayout.LayoutParams(0,-2,1));
        retry=UiKit.button(this,"Reintentar",false);retry.setTextSize(UiKit.font(this,12));
        retry.setVisibility(View.GONE);retry.setOnClickListener(v->initialize());
        statusRow.addView(retry,new LinearLayout.LayoutParams(-2,-2));header.addView(statusRow);
        root.addView(header);

        scroll=new ScrollView(this);scroll.setId(0x5802006);scroll.setFillViewport(true);
        scroll.setClipToPadding(false);scroll.setVerticalScrollBarEnabled(false);
        transcript=UiKit.column(this);transcript.setId(0x5802005);transcript.setPadding(0,dp(12),0,dp(12));
        scroll.addView(transcript,new ScrollView.LayoutParams(-1,-2));root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));

        composer=new LinearLayout(this);composer.setId(0x5802007);composer.setGravity(Gravity.BOTTOM);composer.setBaselineAligned(false);
        android.graphics.drawable.GradientDrawable box=UiKit.shape(this,UiKit.SURFACE,20);box.setStroke(dp(1),UiKit.BORDER);
        composer.setBackground(box);composer.setPadding(dp(12),dp(5),dp(5),dp(5));
        input=new EditText(this);input.setId(0x5802003);input.setTextColor(UiKit.TEXT);input.setHintTextColor(UiKit.MUTED);
        input.setTextSize(UiKit.font(this,16));input.setHint("Escribe a BBY Q…");input.setContentDescription("Mensaje para BBY Q");
        input.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_FLAG_CAP_SENTENCES|InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        input.setImeOptions(EditorInfo.IME_ACTION_SEND|EditorInfo.IME_FLAG_NO_EXTRACT_UI);
        input.setMinLines(1);input.setMaxLines(getResources().getConfiguration().orientation==Configuration.ORIENTATION_LANDSCAPE?2:4);
        input.setMinHeight(dp(48));input.setPadding(dp(2),dp(11),dp(4),dp(10));input.setBackgroundColor(android.graphics.Color.TRANSPARENT);
        input.setText(preferences.getString("chat_draft",""));
        int selection=Math.max(0,Math.min(input.length(),preferences.getInt("chat_selection",input.length())));input.setSelection(selection);
        composer.addView(input,new LinearLayout.LayoutParams(0,-2,1));
        send=UiKit.button(this,"",true);send.setId(0x5802004);send.setContentDescription("Enviar mensaje");
        send.setCompoundDrawablesRelativeWithIntrinsicBounds(UiKit.icon(this,"send",UiKit.BG),null,null,null);
        send.setPadding(dp(13),0,dp(11),0);send.setOnClickListener(v->submit());
        LinearLayout.LayoutParams sendParams=new LinearLayout.LayoutParams(dp(48),dp(48));sendParams.leftMargin=dp(6);composer.addView(send,sendParams);
        root.addView(composer,margin(-1,-2,6));

        navigation=new LinearLayout(this);navigation.setGravity(Gravity.CENTER);navigation.setPadding(0,dp(7),0,0);
        Button chat=nav("Conversar","chat",true,0x5802011);
        chat.setOnClickListener(v->{input.requestFocus();});
        Button model=nav("Mi BBY Q","model",false,0x5802010);model.setOnClickListener(v->openModel());
        LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(0,-2,1);cp.rightMargin=dp(4);navigation.addView(chat,cp);
        LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(0,-2,1);mp.leftMargin=dp(4);navigation.addView(model,mp);
        root.addView(navigation);
        setContentView(root);
        boolean landscape=getResources().getConfiguration().orientation==Configuration.ORIENTATION_LANDSCAPE;
        UiKit.applyInsets(getWindow(),root,14,8,14,7,true,navigation,landscape?header:null);
        input.addTextChangedListener(new TextWatcher(){
            public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            public void onTextChanged(CharSequence s,int start,int before,int count){if(!creating)persistDraft();updateSend();}
            public void afterTextChanged(Editable e){}
        });
        input.setOnEditorActionListener((v,id,event)->{if(id==EditorInfo.IME_ACTION_SEND){submit();return true;}return false;});
        creating=false;render();
    }
    private Button nav(String title,String icon,boolean active,int id){
        Button b=UiKit.button(this,title,false);b.setId(id);b.setTextSize(UiKit.font(this,13));b.setTextColor(active?UiKit.ACCENT:UiKit.MUTED);
        b.setBackground(UiKit.shape(this,active?UiKit.SURFACE:UiKit.BG,14));b.setPadding(dp(8),dp(6),dp(8),dp(6));
        b.setCompoundDrawablesRelativeWithIntrinsicBounds(null,UiKit.icon(this,icon,active?UiKit.ACCENT:UiKit.MUTED),null,null);
        b.setCompoundDrawablePadding(dp(3));return b;
    }
    private void persistDraft(){
        if(preferences!=null&&input!=null)preferences.edit().putString("chat_draft",input.getText().toString())
            .putInt("chat_selection",Math.max(0,input.getSelectionStart())).apply();
    }
    private void updateSend(){
        if(send==null||input==null)return;
        boolean pending=!preferences.getString("conversation_pending","").isEmpty();
        send.setEnabled(ready&&!working&&failure.isEmpty()&&!pending&&!input.getText().toString().trim().isEmpty());
        send.setAlpha(send.isEnabled()?1f:.42f);
    }
    private void render(){
        if(root==null)return;
        state.setText(!failure.isEmpty()?"Tu mensaje está guardado · revisa el estado":working?activityLabel:ready?"Disponible · en tu dispositivo":"Preparando tu BBY Q…");
        state.setTextColor(failure.isEmpty()?(ready&&!working?UiKit.ACCENT:UiKit.MUTED):UiKit.AMBER);
        retry.setVisibility(!failure.isEmpty()&&!working?View.VISIBLE:View.GONE);updateSend();
        String stamp=messages.toString()+"|"+pendingText+"|"+working+"|"+styleStamp;
        if(stamp.equals(renderStamp))return;renderStamp=stamp;transcript.removeAllViews();
        if(messages.length()==0&&pendingText.isEmpty())emptyState();
        for(int i=0;i<messages.length();i++){
            JSONObject m=messages.optJSONObject(i);if(m==null)continue;
            bubble(m.optString("role"),m.optString("text"),m);
        }
        if(!pendingText.isEmpty()){
            boolean found=false;
            for(int i=0;i<messages.length();i++){JSONObject m=messages.optJSONObject(i);if(m!=null&&m.optString("role").equals("user")&&m.optString("request_id").equals(preferences.getString("pending_id","")))found=true;}
            if(!found)bubble("user",pendingText,null);
            TextView wait=label(working?"BBY Q está trabajando…":"Mensaje pendiente · puedes reintentarlo",12,UiKit.MUTED);
            transcript.addView(wait,margin(-1,-2,12));
        }
        scroll.post(()->{if(restoredScroll>=0){scroll.scrollTo(0,restoredScroll);restoredScroll=-1;}
            else if(messages.length()==0&&pendingText.isEmpty())scroll.scrollTo(0,0);
            else scroll.fullScroll(View.FOCUS_DOWN);});
    }
    private void emptyState(){
        LinearLayout welcome=UiKit.column(this);welcome.setGravity(Gravity.CENTER);welcome.setPadding(dp(16),dp(24),dp(16),dp(20));
        welcome.addView(UiKit.brand(this,58));
        TextView title=label("Hablemos, "+owner()+".",26,UiKit.TEXT);title.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        title.setGravity(Gravity.CENTER);welcome.addView(title,margin(-1,-2,20));
        TextView description=label("Tu conversación. Tu memoria.\nTu manera de aprender.",15,UiKit.MUTED);
        description.setGravity(Gravity.CENTER);welcome.addView(description,margin(-1,-2,8));
        if(preferences.getBoolean("show_suggestions",true)){
            LinearLayout suggestions=UiKit.column(this);suggestions.setId(0x5802013);
            suggestions.addView(suggestion("Saludar","hola"),margin(-1,-2,18));
            suggestions.addView(suggestion("Resolver una cuenta","¿Cuánto es 7 + 3?"),margin(-1,-2,8));
            Button teach=UiKit.button(this,"Enseñarle algo nuevo",false);teach.setOnClickListener(v->startActivity(new Intent(this,TrainingActivity.class)));
            suggestions.addView(teach,margin(-1,-2,8));welcome.addView(suggestions,new LinearLayout.LayoutParams(-1,-2));
        }
        transcript.addView(welcome,new LinearLayout.LayoutParams(-1,-2));
    }
    private Button suggestion(String title,String prompt){
        Button b=UiKit.button(this,title,false);b.setOnClickListener(v->{input.setText(prompt);input.setSelection(input.length());input.requestFocus();});return b;
    }
    private void bubble(String role,String body,JSONObject data){
        boolean user="user".equals(role);LinearLayout block=UiKit.column(this);
        if(user){block.setBackground(UiKit.shape(this,0xff1e3933,17));block.setPadding(dp(14),dp(11),dp(14),dp(11));}
        else{block.setPadding(dp(3),dp(8),dp(8),dp(10));TextView who=label("BBY Q",11,UiKit.ACCENT);who.setLetterSpacing(.1f);block.addView(who);}
        TextView message=label(body,16,UiKit.TEXT);message.setTextIsSelectable(true);block.addView(message,margin(-1,-2,user?0:5));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.topMargin=dp(user?12:8);p.bottomMargin=dp(6);
        if(user)p.leftMargin=dp(32);else p.rightMargin=dp(8);
        transcript.addView(block,p);
    }
    private void openModel(){
        persistDraft();startActivity(new Intent(this,ModelActivity.class));
    }
    private void initialize(){
        if(working)return;
        working=true;failure="";activityLabel="Abriendo tu conversación…";publish();
        Context app=getApplicationContext();SharedPreferences prefs=preferences;
        WORKER.execute(()->{
            try{
                U03Runtime.start(app);ready=true;
                String pending=prefs.getString("conversation_pending","");
                if(!pending.isEmpty()){
                    JSONObject request=new JSONObject(pending);pendingText=request.optString("text");
                    lastResponse=conversation(app,request);
                    prefs.edit().remove("conversation_pending").remove("pending_id").commit();pendingText="";
                }
                JSONObject h=conversation(app,args("action","history"));messages=h.optJSONArray("messages");if(messages==null)messages=new JSONArray();
            }catch(Exception|LinkageError e){failure=e.toString();}
            finally{working=false;activityLabel="";publish();}
        });
    }
    private void submit(){
        if(working||!ready||!preferences.getString("conversation_pending","").isEmpty())return;
        String text=input.getText().toString().trim();if(text.isEmpty())return;
        String id="personal-chat-"+UUID.randomUUID();
        JSONObject request=args("action","send","request_id",id,"text",text);
        if(!preferences.edit().putString("conversation_pending",request.toString()).putString("pending_id",id).commit()){
            new AlertDialog.Builder(this).setMessage("No se pudo guardar el envío. Inténtalo de nuevo.").setPositiveButton("Entendido",null).show();return;
        }
        input.setText("");pendingText=text;working=true;failure="";activityLabel="BBY Q está trabajando…";publish();
        Context app=getApplicationContext();SharedPreferences prefs=preferences;
        WORKER.execute(()->{
            try{
                JSONObject r=conversation(app,request);lastResponse=r;
                JSONArray m=r.optJSONArray("messages");
                if(m==null)m=conversation(app,args("action","history")).optJSONArray("messages");
                messages=m==null?new JSONArray():m;
                prefs.edit().remove("conversation_pending").remove("pending_id").commit();pendingText="";
            }catch(Exception|LinkageError e){failure=e.toString();}
            finally{working=false;activityLabel="";publish();}
        });
    }
    private void showMenu(View anchor){
        PopupMenu menu=new PopupMenu(this,anchor);menu.getMenu().add("Nueva conversación");menu.getMenu().add("Exportar conversación");
        menu.getMenu().add("Mi BBY Q");menu.getMenu().add("Detalles de la última respuesta");
        menu.setOnMenuItemClickListener(item->{
            String s=item.getTitle().toString();
            if(s.equals("Mi BBY Q"))openModel();
            else if(s.equals("Exportar conversación"))exportConversation();
            else if(s.equals("Nueva conversación"))newConversation();
            else showDetails();
            return true;
        });menu.show();
    }
    private void newConversation(){
        if(working){Toast.makeText(this,"Espera a que termine el mensaje actual.",Toast.LENGTH_SHORT).show();return;}
        if(!preferences.getString("conversation_pending","").isEmpty()){
            Toast.makeText(this,"Reintenta el envío pendiente para conservar su resultado.",Toast.LENGTH_LONG).show();return;
        }
        new AlertDialog.Builder(this).setTitle("Una conversación nueva")
            .setMessage("Abrirás un espacio limpio. Lo aprendido y el historial anterior se conservarán.")
            .setNegativeButton("Volver",null).setPositiveButton("Comenzar",(d,w)->clearView()).show();
    }
    private void clearView(){
        String id="personal-view-"+UUID.randomUUID();JSONObject request=args("action","clear_view","request_id",id);
        if(!preferences.edit().putString("conversation_pending",request.toString()).putString("pending_id",id).commit())return;
        input.setText("");working=true;failure="";activityLabel="Abriendo una conversación nueva…";publish();
        Context app=getApplicationContext();SharedPreferences prefs=preferences;
        WORKER.execute(()->{
            try{conversation(app,request);JSONObject h=conversation(app,args("action","history"));messages=h.optJSONArray("messages");
                if(messages==null)messages=new JSONArray();lastResponse=null;pendingText="";
                prefs.edit().remove("conversation_pending").remove("pending_id").commit();
            }catch(Exception|LinkageError e){failure=e.toString();}
            finally{working=false;activityLabel="";publish();}
        });
    }
    private void showDetails(){
        Dialog d=new Dialog(this,android.R.style.Theme_Material_NoActionBar);
        LinearLayout body=UiKit.column(this);body.setBackgroundColor(UiKit.BG);
        Button back=UiKit.button(this,"Volver a conversar",false);back.setOnClickListener(v->d.dismiss());body.addView(back);
        TextView title=label("Comprobante de la respuesta",22,UiKit.TEXT);body.addView(title,margin(-1,-2,14));
        TextView hint=label("Aquí puedes revisar el origen y la ejecución de la última respuesta.",14,UiKit.MUTED);body.addView(hint,margin(-1,-2,8));
        ScrollView viewport=new ScrollView(this);TextView report=label("",13,UiKit.TEXT);report.setTextIsSelectable(true);
        report.setTypeface(Typeface.MONOSPACE);
        try{report.setText(lastResponse!=null?lastResponse.toString(2):!failure.isEmpty()?failure:"Todavía no hay un comprobante. Envía un mensaje para comenzar.");}
        catch(Exception e){report.setText("No se pudo mostrar el comprobante.");}
        viewport.addView(report);body.addView(viewport,new LinearLayout.LayoutParams(-1,0,1));
        d.setContentView(body);d.show();d.getWindow().setLayout(-1,-1);UiKit.applyInsets(d.getWindow(),body,16,10,16,10,false);
    }
    private void exportConversation(){
        if(working){Toast.makeText(this,"Espera a que termine el mensaje actual.",Toast.LENGTH_SHORT).show();return;}
        working=true;failure="";activityLabel="Preparando tu archivo…";publish();
        Context app=getApplicationContext();
        WORKER.execute(()->{
            try{
                JSONObject r=conversation(app,args("action","export","request_id","personal-export-"+UUID.randomUUID()));
                String path=r.getString("path");File file=new File(path).getCanonicalFile();
                String files=app.getFilesDir().getCanonicalPath()+File.separator,cache=app.getCacheDir().getCanonicalPath()+File.separator;
                if(!(file.getPath().startsWith(files)||file.getPath().startsWith(cache))||!file.isFile())throw new IOException("Destino de exportación no válido");
                IntegratedActivity a=visible.get();
                if(a!=null&&!a.isFinishing())a.runOnUiThread(()->a.chooseExport(path,r.optString("filename","BBY-Q-0-conversacion.json")));
            }catch(Exception|LinkageError e){failure=e.toString();}
            finally{working=false;activityLabel="";publish();}
        });
    }
    private void chooseExport(String path,String filename){
        exportPath=path;preferences.edit().putString("conversation_export_path",path).apply();
        Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("application/json");
        i.putExtra(Intent.EXTRA_TITLE,filename);startActivityForResult(i,EXPORT_REQUEST);
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);
        if(request!=EXPORT_REQUEST||result!=RESULT_OK||data==null||data.getData()==null)return;
        String selected=exportPath.isEmpty()?preferences.getString("conversation_export_path",""):exportPath;
        android.net.Uri uri=data.getData();Context app=getApplicationContext();
        WORKER.execute(()->{
            String message="Conversación exportada.";
            try{
                File source=new File(selected).getCanonicalFile();
                if(!(source.getPath().startsWith(app.getFilesDir().getCanonicalPath()+File.separator)
                        ||source.getPath().startsWith(app.getCacheDir().getCanonicalPath()+File.separator)))throw new IOException("Archivo no válido");
                try(InputStream in=new FileInputStream(source);OutputStream out=app.getContentResolver().openOutputStream(uri,"w")){
                    if(out==null)throw new IOException("El destino no está disponible");byte[] b=new byte[65536];int n;
                    while((n=in.read(b))!=-1)out.write(b,0,n);
                }
            }catch(Exception e){message="No se pudo guardar el archivo. Puedes volver a exportarlo.";}
            String shown=message;IntegratedActivity a=visible.get();if(a!=null)a.runOnUiThread(()->Toast.makeText(a,shown,Toast.LENGTH_LONG).show());
        });
    }
}

