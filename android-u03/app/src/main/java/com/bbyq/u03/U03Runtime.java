package com.bbyq.u03;

import android.content.Context;
import android.os.Build;
import android.system.Os;
import android.system.OsConstants;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import com.chaquo.python.PyObject;
import org.json.JSONObject;
import org.json.JSONArray;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.zip.ZipFile;

/** One serialized gateway to the original U02 authority and isolated labs. */
public final class U03Runtime {
    private static PyObject core;
    private static JSONObject initialized;
    private static String lastError="";
    private U03Runtime() {}

    public static JSONObject diagnostics(Context c) {
        JSONObject result=new JSONObject();
        try {
            result.put("sdk",Build.VERSION.SDK_INT);
            result.put("abis",new JSONArray(Build.SUPPORTED_ABIS));
            result.put("page_size",Os.sysconf(OsConstants._SC_PAGESIZE));
            result.put("native_library_directory",c.getApplicationInfo().nativeLibraryDir);
            result.put("package",c.getPackageName());
            result.put("ready",initialized!=null);
            result.put("last_error",lastError);
            JSONArray libs=new JSONArray();
            try(ZipFile zip=new ZipFile(c.getApplicationInfo().sourceDir)) {
                java.util.Enumeration<? extends java.util.zip.ZipEntry> entries=zip.entries();
                while(entries.hasMoreElements()){
                    String path=entries.nextElement().getName();
                    if(path.startsWith("lib/") && path.endsWith(".so"))libs.put(path);
                }
            }
            result.put("packaged_libraries",libs);
        } catch(Exception e){try{result.put("diagnostic_error",e.toString());}catch(Exception ignored){}}
        return result;
    }
    private static void saveFailure(Context c,Throwable error) {
        StringWriter text=new StringWriter();error.printStackTrace(new PrintWriter(text));
        lastError=text.toString();
        try(FileOutputStream out=new FileOutputStream(new File(c.getFilesDir(),"startup-diagnostic.json"))){
            out.write(diagnostics(c).toString(2).getBytes(StandardCharsets.UTF_8));
        } catch(Exception ignored){}
    }
    public static synchronized JSONObject start(Context context) throws Exception {
        if(core!=null && initialized!=null)return initialized;
        Context app=context.getApplicationContext();
        try {
            if(!Python.isStarted())Python.start(new AndroidPlatform(app));
            File archive=new File(app.getFilesDir(),"u03-original-runtime.zip");
            try(InputStream in=app.getAssets().open("u03/bbyq-u03-runtime.zip");
                OutputStream out=new FileOutputStream(archive)){
                byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1)out.write(b,0,n);
            }
            ByteArrayOutputStream doc=new ByteArrayOutputStream();
            try(InputStream in=app.getAssets().open("u03/mobile-manifest.json")){
                byte[] b=new byte[65536];int n;while((n=in.read(b))!=-1)doc.write(b,0,n);
            }
            PyObject engine=Python.getInstance().getModule("u03_integrated");
            JSONObject answer=new JSONObject(engine.callAttr("initialize",
                app.getFilesDir().getAbsolutePath(),archive.getAbsolutePath(),
                doc.toString(StandardCharsets.UTF_8.name())).toString());
            if(!answer.optBoolean("ready") || !answer.optBoolean("checkpoint_identity_verified") ||
               answer.optInt("banks")!=7 || answer.optInt("historical_assets")!=159)
                throw new IllegalStateException("Original seven-bank identity verification failed");
            core=engine;initialized=answer;lastError="";return answer;
        } catch(LinkageError error){
            saveFailure(app,error);
            throw new IllegalStateException("No se pudo cargar la biblioteca nativa. Abre Diagnóstico para ver ABI, tamaño de página y causa exacta.",error);
        } catch(Exception error){saveFailure(app,error);throw error;}
    }
    public static synchronized JSONObject turn(Context c,String id,String prompt,String payload)throws Exception{
        start(c);
        if(id==null || id.isEmpty() || prompt==null || prompt.isEmpty())throw new IllegalArgumentException("ID y texto requeridos");
        return new JSONObject(core.callAttr("turn",id,prompt,payload==null?"":payload).toString());
    }
    public static synchronized JSONObject operation(Context c,String name,String args)throws Exception{
        start(c);return new JSONObject(core.callAttr("operation",name,args==null?"{}":args).toString());
    }
    public static synchronized JSONObject status(Context c)throws Exception{
        start(c);return new JSONObject(core.callAttr("status").toString());
    }
    public static synchronized String panel(Context c)throws Exception{
        start(c);return core.callAttr("panel").toString();
    }
    public static synchronized String history(Context c)throws Exception{
        start(c);return core.callAttr("history").toString();
    }
}
