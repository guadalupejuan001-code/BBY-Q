package com.bbyq.personal;

import java.nio.charset.StandardCharsets;

/** A bounded native session; programs and model decisions remain in XI. */
final class XiSession implements AutoCloseable {
    static { System.loadLibrary("reverse_os"); }
    private long handle;
    XiSession(byte[] state) { handle = open(state); }
    private void live() { if (handle == 0) throw new IllegalStateException("Sesión XI cerrada"); }
    synchronized String run(String program) { live(); return new String(execute(handle, program), StandardCharsets.UTF_8); }
    synchronized String role(byte[] program) { live(); return new String(executeRxe(handle, program), StandardCharsets.UTF_8); }
    synchronized byte[] bytes(long address, int length) { live(); return read(handle, address, length); }
    synchronized long number(long address, int length) {
        if (length < 1 || length > 8) throw new IllegalArgumentException("Ancho de entero inválido");
        byte[] b = bytes(address, length); long n = 0;
        for (int i = 0; i < b.length; i++) n |= (b[i] & 255L) << (8 * i);
        return n;
    }
    synchronized byte[] save() { live(); return checkpoint(handle); }
    @Override public synchronized void close() { if (handle != 0) { release(handle); handle = 0; } }
    private static native long open(byte[] seed);
    private static native byte[] execute(long handle, String program);
    private static native byte[] executeRxe(long handle, byte[] program);
    private static native byte[] read(long handle, long address, int length);
    private static native byte[] checkpoint(long handle);
    private static native void release(long handle);
}
