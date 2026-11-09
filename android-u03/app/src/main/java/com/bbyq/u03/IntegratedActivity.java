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
import android.os.Handler;
import android.os.Looper;
import android.text.Editable;
import android.text.InputType;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.lang.ref.WeakReference;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** History, pending requests and drafts are scoped to one durable conversation. */
public final class IntegratedActivity extends Activity implements ConversationUiStore.Observer {
    private static final int EXPORT_REQUEST=618;
    private SharedPreferences preferences;
    private LinearLayout root,header,transcript,composer,navigation;
    private ScrollView scroll;
    private EditText input;
    private TextView state,title;
    private Button send,retry;
    private String conversationId="",styleStamp="",renderStamp="",exportPath="",loadError="";
    private int restoredScroll=-1;
    private long openGeneration=0;
    private boolean creating=false,opening=false,selectOnResume=false,scrollToLatest=false,draftReady=false;
    private final ArrayList<Dialog> dialogs=new ArrayList<>();
    private int dp(float n){return UiKit.dp(this,n);}
    private TextView label(String value,int size,int color){return UiKit.text(this,value,size,color);}
    private LinearLayout.LayoutParams margin(int w,int h,int top){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(w,h);p.topMargin=dp(top);return p;}
    private String owner(){String value=preferences.getString("owner_name","X").trim();return value.isEmpty()?"X":value;}
    private String style(){return owner()+"|"+preferences.getFloat("font_scale",1f)+"|"+preferences.getBoolean("show_suggestions",true);}
    private String draftKey(){return "chat_draft:"+conversationId;}
    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);preferences=getSharedPreferences(UiKit.PREFS,MODE_PRIVATE);
        if(saved!=null){conversationId=saved.getString("conversation_id","");restoredScroll=saved.getInt("scroll",-1);exportPath=saved.getString("export_path","");}
        else{String id=getIntent().getStringExtra("conversation_id");if(id!=null&&!id.isEmpty()){conversationId=id;selectOnResume=true;}}
        buildScreen();ConversationUiStore.ensure(getApplicationContext());
    }
    @Override protected void onResume(){
        super.onResume();ConversationUiStore.observe(this);
        if(!style().equals(styleStamp)){persistDraft();buildScreen();}
        if(!opening){boolean select=selectOnResume;selectOnResume=false;openConversation(conversationId,select);}else render();
    }
    @Override protected void onNewIntent(Intent intent){
        super.onNewIntent(intent);setIntent(intent);String id=intent.getStringExtra("conversation_id");
        if(id!=null&&!id.isEmpty()){persistDraft();bindConversation(id);openConversation(id,true);}
    }
    @Override protected void onPause(){persistDraft();super.onPause();}
    @Override protected void onStop(){ConversationUiStore.unobserve(this);super.onStop();}
    @Override protected void onDestroy(){ConversationUiStore.unobserve(this);for(Dialog d:new ArrayList<>(dialogs))d.dismiss();super.onDestroy();}
    @Override protected void onSaveInstanceState(Bundle out){
        persistDraft();out.putString("conversation_id",conversationId);out.putString("export_path",exportPath);
        if(scroll!=null)out.putInt("scroll",scroll.getScrollY());super.onSaveInstanceState(out);
    }
    @Override public void conversationChanged(){if(!isFinishing()&&!isDestroyed())render();}
    private void buildScreen(){
        creating=true;styleStamp=style();renderStamp="";
        root=UiKit.column(this);root.setId(0x5802000);root.setBackgroundColor(UiKit.BG);
        header=UiKit.column(this);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER_VERTICAL);
        Button chats=UiKit.button(this,"Chats",false);chats.setId(0x5802015);chats.setContentDescription("Ver mis chats");
        chats.setPadding(dp(10),dp(8),dp(10),dp(8));chats.setOnClickListener(v->openChats());top.addView(chats,new LinearLayout.LayoutParams(-2,-2));
        LinearLayout heading=UiKit.column(this);heading.setPadding(dp(10),0,dp(8),0);
        title=label("Tu conversación",19,UiKit.TEXT);title.setId(0x5802014);title.setMaxLines(2);title.setEllipsize(TextUtils.TruncateAt.END);
        title.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));heading.addView(title);
        if(getResources().getConfiguration().orientation!=Configuration.ORIENTATION_LANDSCAPE)heading.addView(label("BBY Q 0  ·  "+owner(),11,UiKit.MUTED));
        top.addView(heading,new LinearLayout.LayoutParams(0,-2,1));
        Button menu=UiKit.button(this,"",false);menu.setId(0x5802012);menu.setContentDescription("Opciones de conversación");
        menu.setCompoundDrawablesRelativeWithIntrinsicBounds(UiKit.icon(this,"more",UiKit.MUTED),null,null,null);
        menu.setPadding(dp(13),0,dp(11),0);menu.setOnClickListener(v->showMenu(menu));top.addView(menu,new LinearLayout.LayoutParams(dp(48),dp(48)));
        header.addView(top);
        LinearLayout statusRow=new LinearLayout(this);statusRow.setGravity(Gravity.CENTER_VERTICAL);statusRow.setPadding(dp(3),dp(5),0,dp(4));
        state=label("Preparando tu BBY Q…",11,UiKit.MUTED);state.setId(0x5802001);
        state.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        statusRow.addView(state,new LinearLayout.LayoutParams(0,-2,1));
        retry=UiKit.button(this,"Reintentar",false);retry.setTextSize(UiKit.font(this,12));
        retry.setVisibility(View.GONE);retry.setOnClickListener(v->retryOpen());
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
        loadDraft();
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
        b.setCompoundDrawablesRelativeWithIntrinsicBounds(null,UiKit.icon(this,icon,active?UiKit.ACCENT:UiKit.MUTED),null,null);b.setCompoundDrawablePadding(dp(3));return b;
    }
    private void bindConversation(String id){
        if(id==null||id.isEmpty())return;
        if(id.equals(conversationId)){if(input!=null&&input.length()==0&&!preferences.getString(draftKey(),"").isEmpty()){creating=true;loadDraft();creating=false;}draftReady=true;return;}
        persistDraft();conversationId=id;creating=true;loadDraft();creating=false;
        draftReady=true;restoredScroll=preferences.getInt("chat_scroll:"+id,-1);renderStamp="";loadError="";
    }
    private void loadDraft(){
        if(input==null)return;draftReady=!conversationId.isEmpty()&&(preferences.contains(draftKey())||ConversationUiStore.ready());input.setText(conversationId.isEmpty()?"":preferences.getString(draftKey(),""));
        input.setSelection(Math.max(0,Math.min(input.length(),preferences.getInt("chat_selection:"+conversationId,input.length()))));
    }
    private void persistDraft(){
        if(preferences!=null&&input!=null&&!conversationId.isEmpty()&&!creating&&draftReady){
            SharedPreferences.Editor edit=preferences.edit().putString(draftKey(),input.getText().toString())
                .putInt("chat_selection:"+conversationId,Math.max(0,input.getSelectionStart()));
            if(scroll!=null)edit.putInt("chat_scroll:"+conversationId,scroll.getScrollY());edit.apply();
        }
    }
    private void openConversation(String id,boolean select){
        opening=true;loadError="";final long generation=++openGeneration;render();WeakReference<IntegratedActivity> ref=new WeakReference<>(this);
        ConversationUiStore.open(getApplicationContext(),id,select,(history,error)->{
            IntegratedActivity a=ref.get();if(a==null||a.isFinishing()||a.isDestroyed()||a.openGeneration!=generation)return;
            a.opening=false;if(error!=null)a.loadError=error;else if(history!=null)a.bindConversation(history.optString("conversation_id"));a.render();
        });
    }
    private void retryOpen(){loadError="";ConversationUiStore.retry(getApplicationContext(),conversationId);openConversation(conversationId,false);}
    private boolean archived(){JSONObject meta=ConversationUiStore.metadata(conversationId);return meta!=null&&meta.optBoolean("archived");}
    private void updateSend(){
        if(send==null||input==null)return;
        boolean enabled=!opening&&ConversationUiStore.history(conversationId)!=null&&!archived()
            &&!ConversationUiStore.hasPending(getApplicationContext(),conversationId)&&loadError.isEmpty()&&!input.getText().toString().trim().isEmpty();
        send.setEnabled(enabled);send.setAlpha(enabled?1f:.42f);input.setEnabled(!opening&&ConversationUiStore.history(conversationId)!=null&&!archived());
    }
    private void render(){
        if(root==null)return;
        JSONObject snapshot=ConversationUiStore.history(conversationId),meta=ConversationUiStore.metadata(conversationId);
        JSONArray messages=snapshot==null?new JSONArray():snapshot.optJSONArray("messages");if(messages==null)messages=new JSONArray();
        JSONArray pending=ConversationUiStore.pending(getApplicationContext(),conversationId);boolean busy=ConversationUiStore.busy(conversationId);
        String error=!loadError.isEmpty()?loadError:ConversationUiStore.error(conversationId);
        title.setText(meta==null?"Tu conversación":meta.optString("title","Nuevo chat"));title.setContentDescription("Chat actual: "+title.getText());
        title.setTag("conversation:"+conversationId);transcript.setTag("conversation:"+conversationId);
        String status=opening?"Abriendo este chat…":!error.isEmpty()?(pending.length()>0?"Mensaje pendiente · puedes reintentarlo":"No se pudo actualizar este chat"):
            busy?"BBY Q está trabajando…":pending.length()>0?"Mensaje pendiente · puedes reintentarlo":snapshot!=null?"Guardado en este dispositivo":"Preparando tu BBY Q…";
        if(archived())status="Chat archivado · recupéralo desde Chats";
        state.setText(status);state.setTextColor(!error.isEmpty()?UiKit.AMBER:snapshot!=null&&!opening&&!busy?UiKit.ACCENT:UiKit.MUTED);
        retry.setVisibility((!error.isEmpty()||pending.length()>0)&&!busy&&!opening?View.VISIBLE:View.GONE);updateSend();
        String stamp=conversationId+"|"+messages+"|"+pending+"|"+(snapshot!=null)+"|"+busy+"|"+styleStamp;
        if(stamp.equals(renderStamp))return;
        boolean atBottom=scroll.getScrollY()+scroll.getHeight()>=transcript.getHeight()-dp(80);int before=scroll.getScrollY();
        renderStamp=stamp;transcript.removeAllViews();
        if(snapshot==null){
            TextView loading=label("Cargando los mensajes guardados…",14,UiKit.MUTED);loading.setPadding(dp(10),dp(20),dp(10),dp(20));transcript.addView(loading);
        }else if(messages.length()==0&&pending.length()==0)emptyState();
        HashSet<String> ids=new HashSet<>();
        for(int i=0;i<messages.length();i++){JSONObject message=messages.optJSONObject(i);if(message!=null){ids.add(message.optString("id"));bubble(message,false);}}
        for(int i=0;i<pending.length();i++){
            JSONObject item=pending.optJSONObject(i);if(item==null)continue;String id=item.optString("request_id")+":user",text=item.optString("text");
            if(!text.isEmpty()&&ids.add(id))bubble(ConversationUiStore.args("id",id,"role","user","text",text),true);
        }
        if(pending.length()>0){TextView wait=label(busy?"BBY Q está respondiendo…":"Envío guardado · reintenta para completarlo",12,UiKit.MUTED);wait.setTag("pending:"+conversationId);transcript.addView(wait,margin(-1,-2,10));}
        final boolean loaded=snapshot!=null,empty=messages.length()==0&&pending.length()==0,latest=scrollToLatest;scrollToLatest=false;
        scroll.post(()->{
            if(!loaded)return;
            if(restoredScroll>=0){scroll.scrollTo(0,restoredScroll);restoredScroll=-1;}
            else if(empty)scroll.scrollTo(0,0);else if(latest||atBottom)scroll.fullScroll(View.FOCUS_DOWN);else scroll.scrollTo(0,before);
        });
    }
    private void emptyState(){
        LinearLayout welcome=UiKit.column(this);welcome.setGravity(Gravity.CENTER);welcome.setPadding(dp(16),dp(24),dp(16),dp(20));welcome.addView(UiKit.brand(this,58));
        TextView heading=label("Hablemos, "+owner()+".",26,UiKit.TEXT);heading.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));heading.setGravity(Gravity.CENTER);welcome.addView(heading,margin(-1,-2,20));
        TextView description=label("Este chat guarda sus mensajes.\nEncuentra los anteriores en Chats.",15,UiKit.MUTED);description.setGravity(Gravity.CENTER);welcome.addView(description,margin(-1,-2,8));
        if(preferences.getBoolean("show_suggestions",true)){
            LinearLayout suggestions=UiKit.column(this);suggestions.setId(0x5802013);
            suggestions.addView(suggestion("Saludar","hola"),margin(-1,-2,18));suggestions.addView(suggestion("Resolver una cuenta","¿Cuánto es 7 + 3?"),margin(-1,-2,8));
            Button teach=UiKit.button(this,"Enseñarle algo nuevo",false);teach.setOnClickListener(v->startActivity(new Intent(this,TrainingActivity.class)));
            suggestions.addView(teach,margin(-1,-2,8));welcome.addView(suggestions,new LinearLayout.LayoutParams(-1,-2));
        }
        transcript.addView(welcome,new LinearLayout.LayoutParams(-1,-2));
    }
    private Button suggestion(String title,String prompt){Button b=UiKit.button(this,title,false);b.setOnClickListener(v->{input.setText(prompt);input.setSelection(input.length());input.requestFocus();});return b;}
    private void bubble(JSONObject data,boolean pending){
        boolean user="user".equals(data.optString("role"));LinearLayout block=UiKit.column(this);block.setTag("message:"+data.optString("id"));
        if(user){block.setBackground(UiKit.shape(this,0xff1e3933,17));block.setPadding(dp(14),dp(11),dp(14),dp(11));}
        else{block.setPadding(dp(3),dp(8),dp(8),dp(10));TextView who=label("BBY Q",11,UiKit.ACCENT);who.setLetterSpacing(.1f);block.addView(who);}
        TextView message=label(data.optString("text"),16,UiKit.TEXT);message.setTextIsSelectable(true);block.addView(message,margin(-1,-2,user?0:5));
        if(pending)block.setContentDescription("Mensaje pendiente: "+data.optString("text"));
        LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(-1,-2);p.topMargin=dp(user?12:8);p.bottomMargin=dp(6);if(user)p.leftMargin=dp(32);else p.rightMargin=dp(8);transcript.addView(block,p);
    }
    private void submit(){
        updateSend();if(!send.isEnabled())return;String text=input.getText().toString().trim();
        if(text.codePointCount(0,text.length())>4096){input.setError("Envía hasta 4096 caracteres por mensaje. El borrador sigue guardado.");return;}
        JSONObject request=ConversationUiStore.args("action","send","request_id","personal-chat-"+UUID.randomUUID(),"conversation_id",conversationId,"text",text);
        if(ConversationUiStore.mutate(getApplicationContext(),request,null)){input.setText("");persistDraft();scrollToLatest=true;loadError="";render();}
        else Toast.makeText(this,"No se pudo guardar el envío. El borrador sigue aquí.",Toast.LENGTH_LONG).show();
    }
    private void openChats(){persistDraft();startActivity(new Intent(this,ChatsActivity.class));}
    private void openModel(){persistDraft();startActivity(new Intent(this,ModelActivity.class));}
    private void showMenu(View anchor){
        PopupMenu menu=new PopupMenu(this,anchor);for(String text:new String[]{"Nuevo chat","Renombrar","Archivar chat","Exportar chat","Mi BBY Q","Detalles de la última respuesta"})menu.getMenu().add(text);
        menu.setOnMenuItemClickListener(item->{String name=item.getTitle().toString();
            if(name.equals("Nuevo chat"))newConversation();else if(name.equals("Renombrar"))rename();else if(name.equals("Archivar chat"))archive();
            else if(name.equals("Exportar chat"))exportConversation();else if(name.equals("Mi BBY Q"))openModel();else showDetails();return true;});menu.show();
    }
    private void newConversation(){
        if(ConversationUiStore.changingChats(getApplicationContext()))return;
        persistDraft();final long generation=openGeneration;WeakReference<IntegratedActivity> ref=new WeakReference<>(this);
        ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","create","request_id","create-chat-"+UUID.randomUUID()),(result,error)->{
            IntegratedActivity a=ref.get();if(a==null||a.isFinishing()||a.isDestroyed()||a.openGeneration!=generation)return;
            if(error!=null){Toast.makeText(a,"No se pudo crear el chat. Puedes reintentarlo.",Toast.LENGTH_LONG).show();return;}
            a.bindConversation(result.optString("active_conversation_id"));a.openConversation(a.conversationId,false);
        });
    }
    private void rename(){
        JSONObject meta=ConversationUiStore.metadata(conversationId);if(meta==null)return;final String id=conversationId;
        EditText edit=new EditText(this);edit.setId(0x5807009);edit.setSingleLine(true);edit.setFilters(new android.text.InputFilter[]{new android.text.InputFilter.LengthFilter(120)});edit.setText(meta.optString("title"));edit.setSelectAllOnFocus(true);edit.setContentDescription("Título del chat");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Renombrar chat").setView(edit).setNegativeButton("Cancelar",null).setPositiveButton("Guardar",null).create();
        dialog.setOnShowListener(d->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{String value=edit.getText().toString().trim();if(value.isEmpty()){edit.setError("Escribe un título");return;}
            if(ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","rename","request_id","rename-chat-"+UUID.randomUUID(),"conversation_id",id,"title",value),null))dialog.dismiss();}));showDialog(dialog);
    }
    private void archive(){
        if(conversationId.isEmpty())return;
        if(ConversationUiStore.hasPending(getApplicationContext(),conversationId)){Toast.makeText(this,"Completa o reintenta el mensaje pendiente antes de archivar.",Toast.LENGTH_LONG).show();return;}
        final String id=conversationId;AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Archivar este chat")
            .setMessage("Lo encontrarás en Chats → Archivados. Sus mensajes y tu borrador seguirán guardados.")
            .setNegativeButton("Cancelar",null).setPositiveButton("Archivar",(d,w)->{
                persistDraft();WeakReference<IntegratedActivity> ref=new WeakReference<>(this);
                ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","archive","request_id","archive-chat-"+UUID.randomUUID(),"conversation_id",id),(result,error)->{
                    IntegratedActivity a=ref.get();if(a==null||a.isFinishing()||a.isDestroyed()||!a.conversationId.equals(id))return;
                    if(error!=null){Toast.makeText(a,"No se pudo archivar el chat.",Toast.LENGTH_LONG).show();return;}
                    a.bindConversation(result.optString("active_conversation_id"));a.openConversation(a.conversationId,false);
                });
            }).create();showDialog(dialog);
    }
    private void showDialog(Dialog dialog){dialogs.add(dialog);dialog.setOnDismissListener(d->dialogs.remove(dialog));dialog.show();}
    private void showDetails(){
        Dialog dialog=new Dialog(this,android.R.style.Theme_Material_NoActionBar);LinearLayout body=UiKit.column(this);body.setBackgroundColor(UiKit.BG);
        Button back=UiKit.button(this,"Volver a conversar",false);back.setOnClickListener(v->dialog.dismiss());body.addView(back);
        body.addView(label("Comprobante de este chat",22,UiKit.TEXT),margin(-1,-2,14));
        body.addView(label("Origen y ejecución de la última respuesta de esta conversación.",14,UiKit.MUTED),margin(-1,-2,8));
        ScrollView viewport=new ScrollView(this);TextView report=label("",13,UiKit.TEXT);report.setTextIsSelectable(true);report.setTypeface(Typeface.MONOSPACE);
        JSONObject receipt=ConversationUiStore.receipt(conversationId);
        try{report.setText(receipt==null?ConversationUiStore.error(conversationId).isEmpty()?"Todavía no hay un comprobante en este chat.":ConversationUiStore.error(conversationId):receipt.toString(2));}
        catch(Exception e){report.setText("No se pudo mostrar el comprobante.");}
        viewport.addView(report);body.addView(viewport,new LinearLayout.LayoutParams(-1,0,1));dialog.setContentView(body);showDialog(dialog);
        dialog.getWindow().setLayout(-1,-1);UiKit.applyInsets(dialog.getWindow(),body,16,10,16,10,false);
    }
    private void exportConversation(){
        if(conversationId.isEmpty())return;WeakReference<IntegratedActivity> ref=new WeakReference<>(this);
        ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","export","conversation_id",conversationId,"request_id","export-chat-"+UUID.randomUUID()),(result,error)->{
            IntegratedActivity a=ref.get();if(a==null||a.isFinishing()||a.isDestroyed())return;
            if(error!=null){Toast.makeText(a,"No se pudo preparar el archivo de este chat.",Toast.LENGTH_LONG).show();return;}
            a.chooseExport(result.optString("path"),result.optString("filename","BBY-Q-0-chat.json"));
        });
    }
    private void chooseExport(String path,String filename){
        exportPath=path;preferences.edit().putString("conversation_export_path",path).apply();Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType("application/json");intent.putExtra(Intent.EXTRA_TITLE,filename);startActivityForResult(intent,EXPORT_REQUEST);
    }
    @Override protected void onActivityResult(int request,int result,Intent data){
        super.onActivityResult(request,result,data);if(request!=EXPORT_REQUEST||result!=RESULT_OK||data==null||data.getData()==null)return;
        String selected=exportPath.isEmpty()?preferences.getString("conversation_export_path",""):exportPath;android.net.Uri destination=data.getData();
        Context app=getApplicationContext();WeakReference<IntegratedActivity> ref=new WeakReference<>(this);
        ConversationUiStore.QUEUE.execute(()->{
            String message="Chat exportado.";try{
                File source=new File(selected).getCanonicalFile();
                if(!(source.getPath().startsWith(app.getFilesDir().getCanonicalPath()+File.separator)||source.getPath().startsWith(app.getCacheDir().getCanonicalPath()+File.separator)))throw new IOException("Archivo no válido");
                try(InputStream in=new FileInputStream(source);OutputStream out=app.getContentResolver().openOutputStream(destination,"w")){
                    if(out==null)throw new IOException("El destino no está disponible");byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1)out.write(b,0,n);
                }
            }catch(Exception e){message="No se pudo guardar el archivo. Puedes volver a exportarlo.";}
            String shown=message;ConversationUiStore.MAIN.post(()->{IntegratedActivity a=ref.get();if(a!=null&&!a.isDestroyed())Toast.makeText(a,shown,Toast.LENGTH_LONG).show();});
        });
    }
}

/** Serialized durable requests. Only full history responses may replace a chat snapshot. */
final class ConversationUiStore {
    interface Observer {void conversationChanged();}
    interface Callback {void complete(JSONObject result,String error);}
    static final ExecutorService QUEUE=Executors.newSingleThreadExecutor();
    static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final Object LOCK=new Object();
    private static final String OUTBOX="conversation_outbox_v1";
    private static final ArrayList<WeakReference<Observer>> observers=new ArrayList<>();
    private static final Map<String,JSONObject> histories=new ConcurrentHashMap<>(),receipts=new ConcurrentHashMap<>();
    private static final Map<String,String> errors=new ConcurrentHashMap<>();
    private static final Set<String> running=ConcurrentHashMap.newKeySet();
    private static volatile JSONArray chats=new JSONArray();
    private static volatile String activeId="",listError="";
    private static volatile boolean initialized=false,initializing=false,listLoading=false;
    private ConversationUiStore(){}
    static JSONObject args(Object... pairs){
        JSONObject object=new JSONObject();try{for(int i=0;i<pairs.length;i+=2)object.put(String.valueOf(pairs[i]),pairs[i+1]);}catch(Exception e){throw new IllegalArgumentException(e);}return object;
    }
    private static SharedPreferences prefs(Context app){return app.getSharedPreferences(UiKit.PREFS,Context.MODE_PRIVATE);}
    private static JSONObject call(Context app,JSONObject request)throws Exception{return U03Runtime.operation(app,"conversation",request.toString());}
    static void observe(Observer observer){synchronized(LOCK){removeObserver(observer);observers.add(new WeakReference<>(observer));}}
    static void unobserve(Observer observer){synchronized(LOCK){removeObserver(observer);}}
    private static void removeObserver(Observer observer){observers.removeIf(ref->ref.get()==null||ref.get()==observer);}
    private static void publish(){
        MAIN.post(()->{ArrayList<Observer> live=new ArrayList<>();synchronized(LOCK){observers.removeIf(ref->ref.get()==null);for(WeakReference<Observer> ref:observers)if(ref.get()!=null)live.add(ref.get());}
            for(Observer observer:live)observer.conversationChanged();});
    }
    static JSONObject history(String id){return id==null?null:histories.get(id);}
    static JSONObject metadata(String id){
        if(id==null||id.isEmpty())return null;JSONArray rows=chats;
        for(int i=0;i<rows.length();i++){JSONObject row=rows.optJSONObject(i);if(row!=null&&id.equals(row.optString("conversation_id",row.optString("id"))))return row;}
        JSONObject h=history(id);return h==null?null:h.optJSONObject("conversation");
    }
    static JSONArray conversations(){return chats;}
    static String activeId(){return activeId;}
    static boolean ready(){return initialized;}
    static boolean loadingList(){return listLoading||initializing;}
    static String listError(){return listError;}
    static String error(String id){return errors.getOrDefault(id==null?"":id,"");}
    static boolean busy(String id){return running.contains(id==null?"":id);}
    static JSONObject receipt(String id){
        JSONObject receipt=receipts.get(id);if(receipt!=null)return receipt;
        JSONObject h=history(id);JSONArray messages=h==null?null:h.optJSONArray("messages");
        if(messages!=null)for(int i=messages.length()-1;i>=0;i--){JSONObject m=messages.optJSONObject(i);if(m!=null&&m.optString("role").equals("assistant"))return m;}return null;
    }
    private static JSONArray outbox(Context app){synchronized(LOCK){try{return new JSONArray(prefs(app).getString(OUTBOX,"[]"));}catch(Exception e){return new JSONArray();}}}
    private static boolean addOutbox(Context app,JSONObject request){
        synchronized(LOCK){
            JSONArray all=outbox(app);String id=request.optString("request_id");
            for(int i=0;i<all.length();i++){JSONObject row=all.optJSONObject(i);if(row!=null&&id.equals(row.optString("request_id")))return true;}
            all.put(request);return prefs(app).edit().putString(OUTBOX,all.toString()).commit();
        }
    }
    private static void removeOutbox(Context app,String requestId){
        synchronized(LOCK){
            JSONArray before=outbox(app),after=new JSONArray();
            for(int i=0;i<before.length();i++){JSONObject row=before.optJSONObject(i);if(row!=null&&!requestId.equals(row.optString("request_id")))after.put(row);}
            prefs(app).edit().putString(OUTBOX,after.toString()).commit();
        }
    }
    static JSONArray pending(Context app,String id){
        JSONArray result=new JSONArray();if(id==null||id.isEmpty())return result;HashSet<String> seen=new HashSet<>();JSONArray requests=outbox(app);
        for(int i=0;i<requests.length();i++){
            JSONObject request=requests.optJSONObject(i);if(request==null||!"send".equals(request.optString("action"))||!id.equals(request.optString("conversation_id")))continue;
            result.put(args("request_id",request.optString("request_id"),"text",request.optString("text"),"conversation_id",id,"request",request));seen.add(request.optString("request_id"));
        }
        JSONObject h=history(id);JSONArray nativePending=h==null?null:h.optJSONArray("pending_requests");
        if(nativePending!=null)for(int i=0;i<nativePending.length();i++){JSONObject row=nativePending.optJSONObject(i);if(row!=null&&seen.add(row.optString("request_id")))result.put(row);}return result;
    }
    static boolean hasPending(Context app,String id){
        if(id==null||id.isEmpty())return false;JSONArray all=outbox(app);
        for(int i=0;i<all.length();i++){JSONObject row=all.optJSONObject(i);if(row!=null&&id.equals(row.optString("conversation_id")))return true;}return pending(app,id).length()>0;
    }
    static boolean changingChats(Context app){
        JSONArray all=outbox(app);for(int i=0;i<all.length();i++){JSONObject row=all.optJSONObject(i);if(row!=null&&Arrays.asList("create","select","rename","archive","restore").contains(row.optString("action")))return true;}return false;
    }
    static void ensure(Context context){
        Context app=context.getApplicationContext();synchronized(LOCK){if(initialized||initializing)return;initializing=true;}publish();
        QUEUE.execute(()->{try{
            U03Runtime.start(app);
            JSONObject original=refreshHistory(app,"");String originalId=original.optString("conversation_id");SharedPreferences settings=prefs(app);
            if(settings.contains("chat_draft")&&!originalId.isEmpty()){
                SharedPreferences.Editor edit=settings.edit();String key="chat_draft:"+originalId;
                if(!settings.contains(key))edit.putString(key,settings.getString("chat_draft","")).putInt("chat_selection:"+originalId,settings.getInt("chat_selection",0));
                edit.remove("chat_draft").remove("chat_selection").commit();
            }
            String legacy=settings.getString("conversation_pending","");
            if(!legacy.isEmpty()){JSONObject request=new JSONObject(legacy);if(addOutbox(app,request))prefs(app).edit().remove("conversation_pending").remove("pending_id").commit();}
            replay(app);refreshList(app);refreshHistory(app,"");initialized=true;listError="";
        }catch(Exception|LinkageError e){listError=e.toString();}finally{initializing=false;publish();}});
    }
    static void reloadList(Context context){
        Context app=context.getApplicationContext();ensure(app);listLoading=true;publish();
        QUEUE.execute(()->{try{refreshList(app);initialized=true;listError="";}catch(Exception|LinkageError e){listError=e.toString();}finally{listLoading=false;publish();}});
    }
    static void open(Context context,String requested,boolean select,Callback callback){
        Context app=context.getApplicationContext();ensure(app);
        if(select&&requested!=null&&!requested.isEmpty()){
            boolean saved=mutate(app,args("action","select","request_id","select-chat-"+UUID.randomUUID(),"conversation_id",requested),(result,error)->callback.complete(error==null?history(requested):null,error));
            if(!saved)MAIN.post(()->callback.complete(null,"No se pudo guardar la selección del chat."));return;
        }
        QUEUE.execute(()->{
            JSONObject h=null;String error=null;
            try{h=refreshHistory(app,requested);initialized=true;errors.remove(requested==null?"":requested);}
            catch(Exception|LinkageError e){error=e.toString();errors.put(requested==null?"":requested,error);}
            JSONObject value=h;String failure=error;publish();MAIN.post(()->callback.complete(value,failure));
        });
    }
    static boolean mutate(Context context,JSONObject request,Callback callback){
        Context app=context.getApplicationContext();if(!addOutbox(app,request))return false;
        String id=request.optString("conversation_id");errors.remove(id);publish();
        QUEUE.execute(()->{
            JSONObject result=null;String error=null;
            try{result=process(app,request);}catch(Exception|LinkageError e){error=e.toString();errors.put(id,error);listError=error;}
            JSONObject value=result;String failure=error;publish();if(callback!=null)MAIN.post(()->callback.complete(value,failure));
        });return true;
    }
    static void retry(Context context,String id){
        Context app=context.getApplicationContext();errors.remove(id);listError="";
        QUEUE.execute(()->{try{
            JSONObject h=history(id);JSONArray nativePending=h==null?null:h.optJSONArray("pending_requests");
            if(nativePending!=null)for(int i=0;i<nativePending.length();i++){JSONObject row=nativePending.optJSONObject(i),request=row==null?null:row.optJSONObject("request");if(request!=null)addOutbox(app,request);}
            replay(app);refreshList(app);refreshHistory(app,id);initialized=true;
        }catch(Exception|LinkageError e){errors.put(id,e.toString());listError=e.toString();}finally{publish();}});
    }
    private static void replay(Context app)throws Exception{
        JSONArray all=outbox(app);for(int i=0;i<all.length();i++){JSONObject request=all.optJSONObject(i);if(request!=null)process(app,request);}
    }
    private static JSONObject process(Context app,JSONObject request)throws Exception{
        String requested=request.optString("conversation_id"),action=request.optString("action");running.add(requested);publish();
        try{
            JSONObject receipt=call(app,request);String id=receipt.optString("conversation_id",requested);JSONObject affected=receipt.optJSONObject("conversation");
            if(affected!=null)id=affected.optString("conversation_id",affected.optString("id",id));
            if(action.equals("send")&&!id.isEmpty())receipts.put(id,receipt);
            // send.messages is only a receipt pair. Fetch the full history for that exact thread.
            if(!id.isEmpty())refreshHistory(app,id);
            refreshList(app);if(!activeId.isEmpty()&&!activeId.equals(id))refreshHistory(app,activeId);
            removeOutbox(app,request.optString("request_id"));errors.remove(requested);if(!id.isEmpty())errors.remove(id);listError="";initialized=true;return receipt;
        }finally{running.remove(requested);publish();}
    }
    private static void refreshList(Context app)throws Exception{
        JSONObject result=call(app,args("action","list","include_archived",true));JSONArray rows=result.optJSONArray("conversations");
        if(rows==null)throw new IOException("No se recibió la lista de chats completa.");chats=rows;activeId=result.optString("active_conversation_id",activeId);
    }
    private static JSONObject refreshHistory(Context app,String requested)throws Exception{
        JSONObject query=args("action","history");if(requested!=null&&!requested.isEmpty())query.put("conversation_id",requested);
        JSONObject result=call(app,query);String id=result.optString("conversation_id");JSONArray messages=result.optJSONArray("messages");
        if(id.isEmpty()||messages==null||(requested!=null&&!requested.isEmpty()&&!requested.equals(id)))throw new IOException("No se recibió el historial completo de este chat.");
        JSONObject previous=histories.get(id);JSONArray older=previous==null?null:previous.optJSONArray("messages");
        if(older!=null){
            if(messages.length()<older.length())throw new IOException("El historial recibido está incompleto. Conservamos los mensajes que ya estaban abiertos.");
            for(int i=0;i<older.length();i++)if(!older.getJSONObject(i).optString("id").equals(messages.getJSONObject(i).optString("id")))throw new IOException("El historial recibido no coincide con este chat.");
        }
        histories.put(id,result);activeId=result.optString("active_conversation_id",activeId);return result;
    }
}

