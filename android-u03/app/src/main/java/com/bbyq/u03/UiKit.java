package com.bbyq.u03;

import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Insets;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.RippleDrawable;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

/** Shared personal visual language and one owner for all system/keyboard insets. */
public final class UiKit {
    public static final int BG=0xff0c1417, SURFACE=0xff152226, RAISED=0xff1c2d31,
        BORDER=0xff2b4042, TEXT=0xffedf4ee, MUTED=0xffa0b5b0,
        ACCENT=0xff79d6b2, AMBER=0xffdfbd86, ERROR=0xfff0a59b;
    public static final String PREFS="bbyq-personal";
    public static final int INSETS_TAG=0x58060f0;
    private UiKit(){}
    public static int dp(Context c,float n){return Math.round(n*c.getResources().getDisplayMetrics().density);}
    public static float font(Context c,float n){
        float scale=c.getSharedPreferences(PREFS,Context.MODE_PRIVATE).getFloat("font_scale",1f);
        return n*Math.max(.9f,Math.min(1.3f,scale));
    }
    public static TextView text(Context c,String value,int size,int color){
        TextView t=new TextView(c);t.setText(value);t.setTextSize(font(c,size));t.setTextColor(color);
        t.setFontFeatureSettings("kern");t.setLineSpacing(dp(c,2),1.08f);return t;
    }
    public static LinearLayout column(Context c){
        LinearLayout l=new LinearLayout(c);l.setOrientation(LinearLayout.VERTICAL);return l;
    }
    public static GradientDrawable shape(Context c,int color,float radius){
        GradientDrawable d=new GradientDrawable();d.setColor(color);d.setCornerRadius(dp(c,radius));return d;
    }
    public static LinearLayout card(Context c){
        LinearLayout l=column(c);GradientDrawable d=shape(c,SURFACE,18);d.setStroke(dp(c,1),BORDER);
        l.setBackground(d);l.setPadding(dp(c,16),dp(c,16),dp(c,16),dp(c,16));return l;
    }
    public static Button button(Context c,String title,boolean primary){
        Button b=new Button(c);b.setText(title);b.setAllCaps(false);b.setTextSize(font(c,14));
        b.setTypeface(Typeface.create("sans-serif-medium",Typeface.NORMAL));
        b.setTextColor(primary?BG:TEXT);b.setMinHeight(dp(c,48));b.setMinimumHeight(dp(c,48));
        b.setMinWidth(dp(c,48));b.setPadding(dp(c,14),dp(c,8),dp(c,14),dp(c,8));
        GradientDrawable bg=shape(c,primary?ACCENT:RAISED,13);
        if(!primary)bg.setStroke(dp(c,1),BORDER);
        b.setBackground(new RippleDrawable(ColorStateList.valueOf(0x24ffffff),bg,null));
        b.setContentDescription(title);return b;
    }
    public static View brand(Context c,int size){
        View v=new View(c){
            final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override protected void onDraw(Canvas canvas){
                float u=Math.min(getWidth(),getHeight())/48f;canvas.save();
                canvas.translate((getWidth()-48*u)/2,(getHeight()-48*u)/2);canvas.scale(u,u);
                p.setStyle(Paint.Style.FILL);p.setColor(SURFACE);canvas.drawRoundRect(0,0,48,48,15,15,p);
                p.setStyle(Paint.Style.STROKE);p.setStrokeCap(Paint.Cap.ROUND);p.setStrokeWidth(2.2f);
                p.setColor(ACCENT);canvas.drawArc(new RectF(9,8,38,37),42,282,false,p);
                canvas.drawLine(29,30,38,39,p);p.setStrokeWidth(1.8f);
                canvas.drawLine(18,18,27,27,p);canvas.drawLine(27,18,18,27,p);
                p.setStyle(Paint.Style.FILL);p.setColor(TEXT);canvas.drawCircle(34,12,2.2f,p);
                canvas.restore();
            }
        };
        v.setContentDescription("Emblema BBY Q 0");
        v.setLayoutParams(new LinearLayout.LayoutParams(dp(c,size),dp(c,size)));return v;
    }
    public static Drawable icon(Context c,String name,int color){
        return new Drawable(){
            final Paint p=new Paint(Paint.ANTI_ALIAS_FLAG);
            @Override public void draw(Canvas canvas){
                canvas.save();canvas.translate(getBounds().left,getBounds().top);
                canvas.scale(getBounds().width()/24f,getBounds().height()/24f);
                p.setColor(color);p.setStrokeWidth(1.7f);p.setStrokeCap(Paint.Cap.ROUND);
                p.setStrokeJoin(Paint.Join.ROUND);p.setStyle(Paint.Style.STROKE);
                Path path=new Path();
                if(name.equals("send")){
                    path.moveTo(5,12);path.lineTo(19,12);path.moveTo(13,5);path.lineTo(20,12);path.lineTo(13,19);canvas.drawPath(path,p);
                }else if(name.equals("back")){
                    path.moveTo(15,5);path.lineTo(8,12);path.lineTo(15,19);canvas.drawPath(path,p);
                }else if(name.equals("model")){
                    canvas.drawLine(4,6,20,6,p);canvas.drawLine(4,12,20,12,p);canvas.drawLine(4,18,20,18,p);
                    p.setStyle(Paint.Style.FILL);p.setColor(BG);canvas.drawCircle(8,6,2.5f,p);canvas.drawCircle(16,12,2.5f,p);canvas.drawCircle(10,18,2.5f,p);
                    p.setStyle(Paint.Style.STROKE);p.setColor(color);canvas.drawCircle(8,6,2.5f,p);canvas.drawCircle(16,12,2.5f,p);canvas.drawCircle(10,18,2.5f,p);
                }else if(name.equals("chat")){
                    path.moveTo(7,4);path.lineTo(18,4);path.quadTo(21,4,21,7);path.lineTo(21,15);path.quadTo(21,18,18,18);
                    path.lineTo(10,18);path.lineTo(4,21);path.lineTo(4,7);path.quadTo(4,4,7,4);canvas.drawPath(path,p);
                    canvas.drawLine(8,9,17,9,p);canvas.drawLine(8,13,14,13,p);
                }else if(name.equals("book")){
                    path.moveTo(12,6);path.quadTo(8,3,3,5);path.lineTo(3,19);path.quadTo(8,17,12,20);
                    path.quadTo(16,17,21,19);path.lineTo(21,5);path.quadTo(16,3,12,6);path.lineTo(12,20);canvas.drawPath(path,p);
                }else{
                    p.setStyle(Paint.Style.FILL);for(int x=5;x<=19;x+=7)canvas.drawCircle(x,12,1.7f,p);
                }
                canvas.restore();
            }
            @Override public void setAlpha(int a){p.setAlpha(a);invalidateSelf();}
            @Override public void setColorFilter(android.graphics.ColorFilter f){p.setColorFilter(f);invalidateSelf();}
            @Override public int getOpacity(){return android.graphics.PixelFormat.TRANSLUCENT;}
            @Override public int getIntrinsicWidth(){return dp(c,22);}
            @Override public int getIntrinsicHeight(){return dp(c,22);}
        };
    }

    /**
     * System bars and keyboard are measured per window, including dialog windows.
     * Android 10 keeps the platform's fitted/resize layout. On API30+ the root
     * owns insets once; children receive consumed insets and cannot double-pad.
     */
    public static void applyInsets(Window window,View root,int left,int top,int right,int bottom,
                                   boolean handleIme,View... hideWhenIme){
        window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        window.setStatusBarColor(BG);window.setNavigationBarColor(BG);
        if(Build.VERSION.SDK_INT>=29)window.setNavigationBarContrastEnforced(false);
        root.setPadding(dp(root.getContext(),left),dp(root.getContext(),top),
                dp(root.getContext(),right),dp(root.getContext(),bottom));
        if(Build.VERSION.SDK_INT>=30){
            window.setDecorFitsSystemWindows(false);
            WindowInsetsController controller=window.getInsetsController();
            if(controller!=null)controller.setSystemBarsAppearance(0,
                    WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS|WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS);
            root.setOnApplyWindowInsetsListener((view,insets)->{
                Insets bars=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
                Insets ime=insets.getInsets(WindowInsets.Type.ime());
                boolean visible=handleIme&&insets.isVisible(WindowInsets.Type.ime())&&ime.bottom>0;
                int safeBottom=handleIme?Math.max(bars.bottom,ime.bottom):bars.bottom;
                view.setPadding(dp(view.getContext(),left)+bars.left,dp(view.getContext(),top)+bars.top,
                        dp(view.getContext(),right)+bars.right,dp(view.getContext(),bottom)+safeBottom);
                view.setTag(INSETS_TAG,new int[]{bars.left,bars.top,bars.right,bars.bottom,ime.bottom,visible?1:0});
                for(View other:hideWhenIme)if(other!=null)other.setVisibility(visible?View.GONE:View.VISIBLE);
                return WindowInsets.CONSUMED;
            });
        }else{
            window.getDecorView().setSystemUiVisibility(0);
        }
        root.requestApplyInsets();
        root.post(root::requestApplyInsets);
    }
}
