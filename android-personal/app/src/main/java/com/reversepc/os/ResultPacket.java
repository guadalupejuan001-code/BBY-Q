package com.reversepc.os;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
/** RXOS1 native result packet. Rejects truncated or oversized transports. */
public final class ResultPacket {
    public final String output;
    public final byte[] state;
    private ResultPacket(String output,byte[] state){this.output=output;this.state=state;}
    public static ResultPacket parse(byte[] payload) {
        if(payload==null||payload.length<13)throw new IllegalArgumentException("Paquete XI incompleto");
        byte[] magic="RXOS1".getBytes(StandardCharsets.US_ASCII);
        for(int i=0;i<5;i++)if(payload[i]!=magic[i])throw new IllegalArgumentException("Firma RXOS1 inválida");
        ByteBuffer b=ByteBuffer.wrap(payload).order(ByteOrder.LITTLE_ENDIAN);
        int n=b.getInt(5),s=b.getInt(9);
        if(n<0||s<0||n>16*1024*1024||s>32*1024*1024+29||13L+n+s!=payload.length)
            throw new IllegalArgumentException("Dimensiones de salida XI inválidas");
        return new ResultPacket(new String(payload,13,n,StandardCharsets.UTF_8),
                Arrays.copyOfRange(payload,13+n,payload.length));
    }
}
