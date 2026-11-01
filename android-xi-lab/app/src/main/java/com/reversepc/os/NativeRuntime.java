package com.reversepc.os;
/** Exact JNI ABI of the pinned REVERSE-PC runtime. Only XI runs native. */
public final class NativeRuntime {
    static { System.loadLibrary("reverse_os"); }
    private NativeRuntime() {}
    public static native byte[] initialize();
    public static native byte[] execute(byte[] state, String source);
    public static native String inspect(byte[] state);
}
