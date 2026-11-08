package com.bbyq.personal;

/** Original REVERSE-PC RVPC2 operations, plus additive C01 source transport. */
public final class XiSession {
    static { System.loadLibrary("reverse_os"); }
    private XiSession() {}
    public static native long open(byte[] state);
    public static native byte[] execute(long handle, String program);
    public static native byte[] executeRxe(long handle, byte[] program);
    public static native byte[] read(long handle, long address, int length);
    public static native byte[] checkpoint(long handle);
    public static native void release(long handle);
    public static native int internLibrary(long handle, String source);
    public static native byte[] executeReference(long handle, int library, String prefix);
    public static native String transportMetrics(long handle);
    public static native void releaseIntegrated(long handle);
}
