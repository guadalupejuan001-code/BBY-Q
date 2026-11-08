package com.bbyq.personal;

/** JNI adapter to the ORIGINAL REVERSE-PC RVPC2 XI runtime. Not a mock. */
public final class XiSession {
    static { System.loadLibrary("reverse_os"); }
    private XiSession() {}
    public static native long open(byte[] state);
    public static native byte[] execute(long handle, String program);
    public static native byte[] executeRxe(long handle, byte[] program);
    public static native byte[] read(long handle, long address, int length);
    public static native byte[] checkpoint(long handle);
    public static native void release(long handle);
}
