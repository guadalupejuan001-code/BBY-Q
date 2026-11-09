package com.bbyq.u03;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Intent;
import android.graphics.Typeface;
import android.os.Bundle;
import android.text.Editable;
import android.text.InputFilter;
import android.text.InputType;
import android.text.TextUtils;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.View;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.lang.ref.WeakReference;
import java.text.Normalizer;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.UUID;

/** Searchable, reversible organization of the user's actual saved conversations. */
public final class ChatsActivity extends Activity implements ConversationUiStore.Observer {
    private LinearLayout root,list;
    private ScrollView scroll;
    private EditText search;
    private TextView status;
    private Button create,active,archived,retry;
    private boolean showArchived=false,building=false;
    private String query="",renderStamp="";
    private final ArrayList<Dialog> dialogs=new ArrayList<>();
    private int dp(float n){return UiKit.dp(this,n);}
    private TextView text(String value,int size,int color){return UiKit.text(this,value,size,color);}
    private LinearLayout.LayoutParams gap(int width,int height,int top){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(width,height);p.topMargin=dp(top);return p;}

    @Override public void onCreate(Bundle saved){
        super.onCreate(saved);if(saved!=null){query=saved.getString("query","");showArchived=saved.getBoolean("archived",false);}build();
    }
    @Override protected void onResume(){super.onResume();ConversationUiStore.observe(this);ConversationUiStore.reloadList(getApplicationContext());render();}
    @Override protected void onStop(){ConversationUiStore.unobserve(this);super.onStop();}
    @Override protected void onDestroy(){ConversationUiStore.unobserve(this);for(Dialog d:new ArrayList<>(dialogs))d.dismiss();super.onDestroy();}
    @Override protected void onSaveInstanceState(Bundle out){out.putString("query",query);out.putBoolean("archived",showArchived);super.onSaveInstanceState(out);}
    @Override public void conversationChanged(){if(!isFinishing()&&!isDestroyed())render();}
    private void build(){
        building=true;root=UiKit.column(this);root.setId(0x5807000);root.setBackgroundColor(UiKit.BG);
        LinearLayout toolbar=new LinearLayout(this);toolbar.setGravity(Gravity.CENTER_VERTICAL);
        Button back=UiKit.button(this,"Conversar",false);back.setId(0x5807001);back.setOnClickListener(v->backToChat());toolbar.addView(back,new LinearLayout.LayoutParams(-2,-2));
        TextView title=text("Tus chats",21,UiKit.TEXT);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);title.setPadding(dp(12),0,0,0);
        title.setMaxLines(2);toolbar.addView(title,new LinearLayout.LayoutParams(0,-2,1));root.addView(toolbar);
        TextView subtitle=text("Retoma una conversación o empieza otra.",14,UiKit.MUTED);root.addView(subtitle,gap(-1,-2,12));
        create=UiKit.button(this,"Nuevo chat",true);create.setId(0x5807002);create.setOnClickListener(v->newChat());root.addView(create,gap(-1,-2,12));
        search=new EditText(this);search.setId(0x5807003);search.setSingleLine(true);search.setTextSize(UiKit.font(this,15));
        search.setTextColor(UiKit.TEXT);search.setHintTextColor(UiKit.MUTED);search.setHint("Título o último mensaje");search.setContentDescription("Buscar chats por título o último mensaje");
        search.setInputType(InputType.TYPE_CLASS_TEXT);search.setBackground(UiKit.shape(this,UiKit.SURFACE,12));search.setMinHeight(dp(48));search.setPadding(dp(12),dp(10),dp(12),dp(10));search.setText(query);
        search.setImeOptions(android.view.inputmethod.EditorInfo.IME_ACTION_SEARCH|android.view.inputmethod.EditorInfo.IME_FLAG_NO_EXTRACT_UI);
        search.setOnEditorActionListener((view,action,event)->{if(action==android.view.inputmethod.EditorInfo.IME_ACTION_SEARCH){
            android.view.inputmethod.InputMethodManager keyboard=(android.view.inputmethod.InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);if(keyboard!=null)keyboard.hideSoftInputFromWindow(search.getWindowToken(),0);return true;}return false;});
        root.addView(search,gap(-1,-2,12));
        LinearLayout filters=new LinearLayout(this);active=UiKit.button(this,"Chats",true);active.setId(0x5807004);archived=UiKit.button(this,"Archivados",false);archived.setId(0x5807005);
        active.setOnClickListener(v->{showArchived=false;renderStamp="";render();});archived.setOnClickListener(v->{showArchived=true;renderStamp="";render();});
        LinearLayout.LayoutParams a=new LinearLayout.LayoutParams(0,-2,1);a.rightMargin=dp(6);filters.addView(active,a);filters.addView(archived,new LinearLayout.LayoutParams(0,-2,1));root.addView(filters,gap(-1,-2,10));
        LinearLayout stateRow=new LinearLayout(this);stateRow.setGravity(Gravity.CENTER_VERTICAL);status=text("Leyendo tus chats…",12,UiKit.MUTED);status.setId(0x5807006);
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);stateRow.addView(status,new LinearLayout.LayoutParams(0,-2,1));
        retry=UiKit.button(this,"Reintentar",false);retry.setVisibility(View.GONE);retry.setOnClickListener(v->{ConversationUiStore.retry(getApplicationContext(),ConversationUiStore.activeId());ConversationUiStore.reloadList(getApplicationContext());});
        stateRow.addView(retry,new LinearLayout.LayoutParams(-2,-2));root.addView(stateRow,gap(-1,-2,8));
        scroll=new ScrollView(this);scroll.setId(0x5807007);scroll.setFillViewport(true);list=UiKit.column(this);list.setId(0x5807008);list.setPadding(0,0,0,dp(12));scroll.addView(list);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);boolean landscape=getResources().getConfiguration().orientation==android.content.res.Configuration.ORIENTATION_LANDSCAPE;
        UiKit.applyInsets(getWindow(),root,16,10,16,10,true,subtitle,create,landscape?toolbar:null,landscape?filters:null,landscape?stateRow:null);
        search.addTextChangedListener(new TextWatcher(){public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            public void onTextChanged(CharSequence s,int start,int before,int count){if(!building){query=s.toString();renderStamp="";render();}}
            public void afterTextChanged(Editable e){}});
        building=false;render();
    }
    private void render(){
        if(root==null)return;
        boolean changing=ConversationUiStore.changingChats(getApplicationContext()),loading=ConversationUiStore.loadingList();
        create.setEnabled(ConversationUiStore.ready()&&!changing);
        active.setSelected(!showArchived);archived.setSelected(showArchived);
        active.setTextColor(showArchived?UiKit.TEXT:UiKit.BG);archived.setTextColor(showArchived?UiKit.BG:UiKit.TEXT);
        active.setBackgroundTintList(android.content.res.ColorStateList.valueOf(showArchived?UiKit.RAISED:UiKit.ACCENT));
        archived.setBackgroundTintList(android.content.res.ColorStateList.valueOf(showArchived?UiKit.ACCENT:UiKit.RAISED));
        String error=ConversationUiStore.listError();
        status.setText(!error.isEmpty()?"No se pudo completar la actualización":changing?"Guardando el cambio…":loading?"Actualizando tus chats…":showArchived?"Puedes recuperar cualquier chat archivado.":"Cada chat conserva sus mensajes y su borrador.");
        status.setTextColor(error.isEmpty()?UiKit.MUTED:UiKit.AMBER);retry.setVisibility(error.isEmpty()?View.GONE:View.VISIBLE);
        updateControls(list,!changing);
        JSONArray conversations=ConversationUiStore.conversations();String stamp=conversations+"|"+query+"|"+showArchived+"|"+ConversationUiStore.activeId();
        if(stamp.equals(renderStamp))return;renderStamp=stamp;int oldScroll=scroll.getScrollY();list.removeAllViews();int count=0;String term=fold(query.trim());
        for(int i=0;i<conversations.length();i++){
            JSONObject conversation=conversations.optJSONObject(i);if(conversation==null||conversation.optBoolean("archived")!=showArchived)continue;
            if(!term.isEmpty()&&!fold(conversation.optString("title")+" "+conversation.optString("preview")).contains(term))continue;
            row(conversation,changing);count++;
        }
        if(count==0){
            LinearLayout empty=UiKit.card(this);TextView heading=text(!term.isEmpty()?"No hay coincidencias":showArchived?"Sin chats archivados":loading?"Cargando tus conversaciones…":"Tu siguiente conversación",19,UiKit.TEXT);
            heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);empty.addView(heading);
            empty.addView(text(!term.isEmpty()?"Prueba con otra palabra del título o del último mensaje.":showArchived?"Cuando archives un chat, aparecerá aquí con sus mensajes y borrador.":"Toca Nuevo chat para empezar. Los chats anteriores se conservan en esta lista.",14,UiKit.MUTED),gap(-1,-2,8));list.addView(empty,gap(-1,-2,8));
        }
        scroll.post(()->scroll.scrollTo(0,oldScroll));
    }
    private void row(JSONObject conversation,boolean changing){
        String id=conversation.optString("conversation_id",conversation.optString("id")),title=conversation.optString("title","Nuevo chat");
        boolean isArchived=conversation.optBoolean("archived"),isActive=id.equals(ConversationUiStore.activeId());
        LinearLayout card=UiKit.card(this);card.setTag("conversation:"+id);
        if(isActive&&!isArchived){android.graphics.drawable.GradientDrawable shape=UiKit.shape(this,UiKit.SURFACE,18);shape.setStroke(dp(1),UiKit.ACCENT);card.setBackground(shape);}
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.TOP);
        LinearLayout copy=UiKit.column(this);TextView heading=text(title,17,UiKit.TEXT);heading.setTypeface(Typeface.DEFAULT,Typeface.BOLD);heading.setMaxLines(2);heading.setEllipsize(TextUtils.TruncateAt.END);copy.addView(heading);
        String date=new SimpleDateFormat("d MMM yyyy · HH:mm",new Locale("es")).format(new Date(conversation.optLong("updated_at_ms",conversation.optLong("created_at_ms"))));
        copy.addView(text((isActive&&!isArchived?"Abierto · ":"")+date,11,isActive&&!isArchived?UiKit.ACCENT:UiKit.MUTED),gap(-1,-2,5));top.addView(copy,new LinearLayout.LayoutParams(0,-2,1));
        Button options=UiKit.button(this,"",false);options.setTag("conversation_options:"+id);options.setContentDescription("Opciones de "+title);
        options.setCompoundDrawablesRelativeWithIntrinsicBounds(UiKit.icon(this,"more",UiKit.MUTED),null,null,null);options.setPadding(dp(13),0,dp(11),0);options.setEnabled(!changing);
        options.setOnClickListener(v->options(options,conversation));LinearLayout.LayoutParams op=new LinearLayout.LayoutParams(dp(48),dp(48));op.leftMargin=dp(8);top.addView(options,op);card.addView(top);
        String preview=conversation.optString("preview");TextView last=text(preview.isEmpty()?"Sin mensajes todavía":preview,14,UiKit.MUTED);last.setMaxLines(2);last.setEllipsize(TextUtils.TruncateAt.END);card.addView(last,gap(-1,-2,9));
        int n=conversation.optInt("message_count");String detail=n+" "+(n==1?"mensaje":"mensajes");
        if(ConversationUiStore.pending(getApplicationContext(),id).length()>0)detail+=" · envío pendiente";
        card.addView(text(detail,11,UiKit.MUTED),gap(-1,-2,8));
        if(isArchived){
            Button restore=UiKit.button(this,"Recuperar chat",false);restore.setTag("conversation_restore:"+id);restore.setEnabled(!changing);restore.setOnClickListener(v->restore(id));card.addView(restore,gap(-1,-2,10));
        }else{
            card.setFocusable(true);card.setClickable(true);card.setContentDescription("Abrir "+title+". "+date+". "+detail+". "+preview);
            card.setOnClickListener(v->{if(!ConversationUiStore.changingChats(getApplicationContext()))open(id);});
        }
        list.addView(card,gap(-1,-2,8));
    }
    private static String fold(String value){return Normalizer.normalize(value,Normalizer.Form.NFD).replaceAll("\\p{M}","").toLowerCase(Locale.ROOT);}
    private void updateControls(android.view.ViewGroup group,boolean enabled){
        for(int i=0;i<group.getChildCount();i++){View view=group.getChildAt(i);Object tag=view.getTag();
            if(tag!=null&&(tag.toString().startsWith("conversation_options:")||tag.toString().startsWith("conversation_restore:")))view.setEnabled(enabled);
            if(view instanceof android.view.ViewGroup)updateControls((android.view.ViewGroup)view,enabled);
        }
    }
    private void backToChat(){
        Intent intent=new Intent(this,IntegratedActivity.class).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
        if(!ConversationUiStore.activeId().isEmpty())intent.putExtra("conversation_id",ConversationUiStore.activeId());startActivity(intent);finish();
    }
    @Override public void onBackPressed(){backToChat();}
    private void open(String id){
        Intent intent=new Intent(this,IntegratedActivity.class).putExtra("conversation_id",id).addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);startActivity(intent);finish();
    }
    private void newChat(){
        if(!create.isEnabled())return;WeakReference<ChatsActivity> ref=new WeakReference<>(this);
        ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","create","request_id","create-chat-"+UUID.randomUUID()),(result,error)->{
            ChatsActivity a=ref.get();if(a==null||a.isFinishing()||a.isDestroyed())return;
            if(error!=null){Toast.makeText(a,"No se pudo crear el chat. Puedes reintentarlo.",Toast.LENGTH_LONG).show();return;}a.open(result.optString("active_conversation_id"));
        });render();
    }
    private void options(View anchor,JSONObject conversation){
        PopupMenu menu=new PopupMenu(this,anchor);menu.getMenu().add("Renombrar");menu.getMenu().add(conversation.optBoolean("archived")?"Recuperar chat":"Archivar chat");
        menu.setOnMenuItemClickListener(item->{if(item.getTitle().toString().equals("Renombrar"))rename(conversation);
            else if(conversation.optBoolean("archived"))restore(conversation.optString("conversation_id",conversation.optString("id")));else archive(conversation);return true;});menu.show();
    }
    private void rename(JSONObject conversation){
        String id=conversation.optString("conversation_id",conversation.optString("id"));EditText edit=new EditText(this);edit.setId(0x5807009);
        edit.setSingleLine(true);edit.setFilters(new InputFilter[]{new InputFilter.LengthFilter(120)});edit.setText(conversation.optString("title"));edit.setSelectAllOnFocus(true);edit.setContentDescription("Título del chat");
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Renombrar chat").setView(edit).setNegativeButton("Cancelar",null).setPositiveButton("Guardar",null).create();
        dialog.setOnShowListener(d->dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            String title=edit.getText().toString().trim();if(title.isEmpty()){edit.setError("Escribe un título");return;}
            if(ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","rename","request_id","rename-chat-"+UUID.randomUUID(),"conversation_id",id,"title",title),null))dialog.dismiss();
        }));show(dialog);
    }
    private void archive(JSONObject conversation){
        String id=conversation.optString("conversation_id",conversation.optString("id"));
        if(ConversationUiStore.hasPending(getApplicationContext(),id)){Toast.makeText(this,"Completa o reintenta el mensaje pendiente antes de archivar.",Toast.LENGTH_LONG).show();return;}
        AlertDialog dialog=new AlertDialog.Builder(this).setTitle("Archivar este chat")
            .setMessage("Lo encontrarás en Archivados. Sus mensajes y tu borrador seguirán guardados.")
            .setNegativeButton("Cancelar",null).setPositiveButton("Archivar",(d,w)->ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","archive","request_id","archive-chat-"+UUID.randomUUID(),"conversation_id",id),null)).create();show(dialog);
    }
    private void restore(String id){
        WeakReference<ChatsActivity> ref=new WeakReference<>(this);
        ConversationUiStore.mutate(getApplicationContext(),ConversationUiStore.args("action","restore","request_id","restore-chat-"+UUID.randomUUID(),"conversation_id",id),(result,error)->{
            ChatsActivity a=ref.get();if(a==null||a.isFinishing()||a.isDestroyed())return;
            Toast.makeText(a,error==null?"Chat recuperado. Lo encontrarás en Chats.":"No se pudo recuperar el chat.",Toast.LENGTH_LONG).show();
        });
    }
    private void show(Dialog dialog){dialogs.add(dialog);dialog.setOnDismissListener(d->dialogs.remove(dialog));dialog.show();}
}

