package com.bbyq.u03;

import android.content.Context;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.recyclerview.widget.DiffUtil;
import androidx.recyclerview.widget.ListAdapter;
import androidx.recyclerview.widget.RecyclerView;

/** Virtualized chat rows; the native history remains the source of truth. */
public final class ChatTranscriptAdapter extends ListAdapter<ChatTranscriptAdapter.Row, ChatTranscriptAdapter.Holder> {
    public static final class Row {
        public final String key, conversationId, id, requestId, role, text;
        public final boolean confirmed, notice;
        private Row(String key, String conversationId, String id, String requestId,
                    String role, String text, boolean confirmed, boolean notice) {
            this.key=key;this.conversationId=conversationId;this.id=id;
            this.requestId=requestId;this.role=role;this.text=text;
            this.confirmed=confirmed;this.notice=notice;
        }
        static Row message(String chat, String id, String requestId, String role, String text, boolean confirmed) {
            // One stable identity for the native saved row and the local pending row.
            // Historical records can have different message IDs for the same receipt.
            final String identity=requestId.isEmpty()?id:requestId+":"+role;
            return new Row("msg:"+chat+":"+identity,chat,id,requestId,role,text,confirmed,false);
        }
        static Row notice(String chat, String text) {
            return new Row("notice:"+chat,chat,"","","notice",text,true,true);
        }
    }

    static final class Holder extends RecyclerView.ViewHolder {
        final TextView message;
        Holder(View root, TextView message) {super(root);this.message=message;}
    }

    private static final DiffUtil.ItemCallback<Row> ROW_DIFF=new DiffUtil.ItemCallback<Row>() {
        @Override public boolean areItemsTheSame(Row left, Row right) {
            return left.key.equals(right.key);
        }
        @Override public boolean areContentsTheSame(Row left, Row right) {
            return left.confirmed==right.confirmed && left.notice==right.notice
                && left.id.equals(right.id) && left.role.equals(right.role)
                && left.text.equals(right.text);
        }
    };

    ChatTranscriptAdapter() {super(ROW_DIFF);}

    @Override public int getItemViewType(int position) {
        Row row=getItem(position);
        return row.notice?2:("user".equals(row.role)?0:1);
    }

    @Override public Holder onCreateViewHolder(ViewGroup parent, int type) {
        Context ctx=parent.getContext();
        FrameLayout root=new FrameLayout(ctx);
        root.setLayoutParams(new RecyclerView.LayoutParams(-1,-2));

        if(type==2) {
            TextView hint=UiKit.text(ctx,"",12,UiKit.MUTED);
            FrameLayout.LayoutParams hp=new FrameLayout.LayoutParams(-1,-2);
            hp.topMargin=UiKit.dp(ctx,10);hp.bottomMargin=UiKit.dp(ctx,10);
            root.addView(hint,hp);
            return new Holder(root,hint);
        }

        final boolean user=type==0;
        LinearLayout bubble=UiKit.column(ctx);
        if(user) {
            bubble.setBackground(UiKit.shape(ctx,0xff1e3933,17));
            bubble.setPadding(UiKit.dp(ctx,14),UiKit.dp(ctx,11),
                              UiKit.dp(ctx,14),UiKit.dp(ctx,11));
        } else {
            bubble.setPadding(UiKit.dp(ctx,3),UiKit.dp(ctx,8),
                              UiKit.dp(ctx,8),UiKit.dp(ctx,10));
            TextView who=UiKit.text(ctx,"BBY Q",11,UiKit.ACCENT);
            who.setLetterSpacing(.1f);bubble.addView(who);
        }
        TextView message=UiKit.text(ctx,"",16,UiKit.TEXT);
        message.setTextIsSelectable(true);
        LinearLayout.LayoutParams mp=new LinearLayout.LayoutParams(-1,-2);
        mp.topMargin=UiKit.dp(ctx,user?0:5);
        bubble.addView(message,mp);
        FrameLayout.LayoutParams bp=new FrameLayout.LayoutParams(-1,-2,
                user?Gravity.END:Gravity.START);
        bp.topMargin=UiKit.dp(ctx,user?12:8);
        bp.bottomMargin=UiKit.dp(ctx,6);
        bp.leftMargin=UiKit.dp(ctx,user?32:0);
        bp.rightMargin=UiKit.dp(ctx,user?0:8);
        root.addView(bubble,bp);
        return new Holder(root,message);
    }

    @Override public void onBindViewHolder(Holder holder, int position) {
        Row row=getItem(position);
        holder.message.setText(row.text);
        holder.itemView.setTag(row.notice?"pending:"+row.conversationId:"message:"+row.id);
        holder.itemView.setContentDescription(!row.notice && "user".equals(row.role)
                && !row.confirmed?"Mensaje pendiente: "+row.text:null);
    }
}
