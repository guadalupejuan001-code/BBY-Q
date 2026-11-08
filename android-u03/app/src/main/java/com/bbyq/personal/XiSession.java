package com.bbyq.personal;
/** Original XI stateful interpreter with C01 source-library transport; never result caching. */
public final class XiSession {
 static { System.loadLibrary("reverse_os"); }
 private XiSession() {}
 public static native long open(byte[] state);
 public static native byte[] execute(long handle,String source);
 public static native long registerLibrary(long handle,String library);
 public static native byte[] executeRef(long handle,long library,String prelude);
 public static native byte[] executeRxe(long handle,byte[] program);
 public static native byte[] read(long handle,long address,int length);
 public static native byte[] checkpoint(long handle);
 public static native void release(long handle);
 public static native String capabilities();
}
