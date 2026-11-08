package com.bbyq.u03;
import android.content.Context;
import android.os.Build;
import android.os.Process;
import android.system.Os;
import android.system.OsConstants;
import com.bbyq.personal.XiSession;
import org.json.JSONObject;
import org.json.JSONArray;
import java.io.File;
/** Reports the actual loader cause; never replaces native XI with a fake response. */
public final class NativeBootstrap {
 private NativeBootstrap(){}
 public static JSONObject diagnose(Context c){
  JSONObject d=new JSONObject();
  try{
   d.put("android_api",Build.VERSION.SDK_INT);d.put("manufacturer",Build.MANUFACTURER);d.put("model",Build.MODEL);
   d.put("abis",new JSONArray(Build.SUPPORTED_ABIS));d.put("process_64_bit",Process.is64Bit());
   d.put("page_size",Os.sysconf(OsConstants._SC_PAGESIZE));
   File dir=new File(c.getApplicationInfo().nativeLibraryDir);d.put("native_directory",dir.toString());
   d.put("reverse_os_file_present",new File(dir,"libreverse_os.so").isFile());
   d.put("runtime",new JSONObject(XiSession.capabilities()));d.put("loaded",true);
  }catch(Throwable error){
   try{d.put("loaded",false);d.put("error_class",error.getClass().getName());d.put("error",String.valueOf(error));Throwable cause=error.getCause();if(cause!=null)d.put("cause",cause.toString());}catch(Exception ignored){}
  }
  return d;
 }
 public static void require(Context c)throws Exception{
  JSONObject d=diagnose(c);if(!d.optBoolean("loaded"))throw new IllegalStateException("Biblioteca XI no disponible. Diagnóstico: "+d.toString());
 }
}
