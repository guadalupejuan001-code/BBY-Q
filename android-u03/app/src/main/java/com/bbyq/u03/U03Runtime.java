package com.bbyq.u03;
import android.content.Context;
import com.chaquo.python.Python;
import com.chaquo.python.PyObject;
import com.chaquo.python.android.AndroidPlatform;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
/** Single synchronized gateway. The C13 experiment cannot race a live user turn. */
public final class U03Runtime {
 private static PyObject core;
 private static JSONObject initialized;
 private U03Runtime(){}
 public static synchronized JSONObject start(Context context)throws Exception{
  if(core!=null && initialized!=null)return initialized;
  Context app=context.getApplicationContext();NativeBootstrap.require(app);
  if(!Python.isStarted())Python.start(new AndroidPlatform(app));
  File archive=new File(app.getFilesDir(),"u03-original-runtime.zip");
  try(InputStream in=app.getAssets().open("u03/bbyq-u03-runtime.zip");OutputStream out=new FileOutputStream(archive)){
   byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);
  }
  ByteArrayOutputStream json=new ByteArrayOutputStream();
  try(InputStream in=app.getAssets().open("u03/mobile-manifest.json")){
   byte[] buf=new byte[65536];int n;while((n=in.read(buf))!=-1)json.write(buf,0,n);
  }
  PyObject engine=Python.getInstance().getModule("u03_mobile");
  JSONObject result=new JSONObject(engine.callAttr("initialize",app.getFilesDir().getAbsolutePath(),archive.getAbsolutePath(),json.toString(StandardCharsets.UTF_8.name())).toString());
  if(!result.optBoolean("ready") || result.optInt("banks")!=7 || result.optInt("historical_assets")!=159 || !result.optBoolean("checkpoint_identity_verified"))throw new IllegalStateException("Original U03 startup audit failed");
  core=engine;initialized=result;return result;
 }
 public static synchronized JSONObject turn(Context c,String id,String prompt,String payload)throws Exception{
  start(c);return new JSONObject(core.callAttr("turn",id,prompt,payload==null?"":payload).toString());
 }
 public static synchronized JSONObject action(Context c,String name,String payload)throws Exception{
  start(c);return new JSONObject(core.callAttr("action",name,payload==null?"{}":payload).toString());
 }
 public static synchronized JSONObject status(Context c)throws Exception{start(c);return new JSONObject(core.callAttr("status").toString());}
 public static synchronized String panel(Context c)throws Exception{start(c);return core.callAttr("panel").toString();}
 public static synchronized String history(Context c)throws Exception{start(c);return core.callAttr("history").toString();}
 public static synchronized String lastReport(Context c)throws Exception{start(c);return core.callAttr("last_report").toString();}
 public static JSONObject diagnostics(Context c){return NativeBootstrap.diagnose(c);}
}
