package com.bbyq.personal;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;
import org.json.*;

/** Versioned exact C1 transport. XI derives features from measured frames.
 * The caller must persist this dictionary with any checkpoint trained on it.
 * This experimental codec does not select the app's active language model. */
final class SequenceCodec {
    static final long C=8150000000000000000L;
    static final long T=C+10000,TL=C+15000,H=C+20000,HL=C+21000;
    static final long NF=C+25000,NV=C+26000,F=C+100000,G=C+110000;
    static final long RAW=C+60000,HRAW=C+80000,FRAME=C+2000,MEASURED=C+2200;
    static final long FEATURE_STRIDE=1L<<40;
    static final int[] WIDTHS={20,20,16,2,7,7,6,16,6};
    private static final String WORD="[\\p{L}\\p{N}_]";
    private static final Pattern TOKENS=Pattern.compile(
        "\\p{Nd}+(?:[.,]\\p{Nd}+)?|[\\p{L}\\p{Nl}\\p{No}]"+
        "[\\p{L}\\p{N}_\\u0300-\\u036f]*|_"+WORD+
        "*|[^\\x09-\\x0d\\x1c-\\x20\\x85\\u00a0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]");
    private static final Pattern NUMBER=Pattern.compile("[0-9]+(?:[.,][0-9]+)?");
    private final List<String> vocabulary=new ArrayList<>();
    private final Map<String,Integer> ids=new HashMap<>();

    SequenceCodec(JSONArray words)throws Exception {
        if(words.length()<1||!words.getString(0).equals("<pad>")||words.length()>=(1<<20))throw new IOException("Diccionario C1 inválido");
        for(int i=0;i<words.length();i++){
            String word=words.getString(i);
            if(ids.put(word,i)!=null)throw new IOException("Identidad duplicada en C1");
            vocabulary.add(word);
        }
    }
    JSONArray dictionary(){return new JSONArray(vocabulary);}
    static final class Token {
        final int id,start,length;final String key;final Double number;
        Token(int id,String key,int start,int length,Double number){this.id=id;this.key=key;this.start=start;this.length=length;this.number=number;}
        JSONObject json()throws Exception {return new JSONObject().put("id",id).put("key",key).put("start",start).put("length",length).put("numeric",number==null?JSONObject.NULL:number);}
    }
    static final class Text {
        final byte[] raw;final List<Token> tokens;
        Text(byte[] raw,List<Token> tokens){this.raw=raw;this.tokens=tokens;}
    }
    Text text(String text,int limit)throws Exception {
        for(int i=0;i<text.length();i++)if(Character.isSurrogate(text.charAt(i))){
            if(!Character.isHighSurrogate(text.charAt(i))||i+1>=text.length()||!Character.isLowSurrogate(text.charAt(++i)))throw new IOException("UTF-8 C1 inválido");
        }
        byte[] raw=text.getBytes(StandardCharsets.UTF_8);
        if(raw.length>16384)throw new IOException("C1 admite hasta 16384 bytes por texto");
        Matcher matcher=TOKENS.matcher(text);List<int[]> spans=new ArrayList<>();
        while(matcher.find()){spans.add(new int[]{matcher.start(),matcher.end()});if(spans.size()>limit)throw new IOException("Capacidad de tokens C1 superada");}
        List<Token> tokens=new ArrayList<>();
        for(int[] span:spans){
            String token=text.substring(span[0],span[1]);
            String key=Normalizer.normalize(token,Normalizer.Form.NFC).toLowerCase(Locale.ROOT);
            Double number=NUMBER.matcher(key).matches()?Double.valueOf(key.replace(',','.')):null;
            if(number!=null&&!Double.isFinite(number))throw new IOException("Valor numérico C1 fuera de rango");
            Integer id=ids.get(key);
            if(id==null){if(vocabulary.size()>=(1<<20))throw new IOException("Diccionario C1 lleno");id=vocabulary.size();vocabulary.add(key);ids.put(key,id);}
            tokens.add(new Token(id,key,text.substring(0,span[0]).getBytes(StandardCharsets.UTF_8).length,token.getBytes(StandardCharsets.UTF_8).length,number));
        }
        return new Text(raw,tokens);
    }
    static void put(StringBuilder source,long address,long value){source.append("store64 ").append(address).append(' ').append(value).append('\n');}
    static void bytes(StringBuilder source,long address,byte[] data){for(int i=0;i<data.length;i++)source.append("store8 ").append(address+i).append(' ').append(data[i]&255).append('\n');}
    private static void stage(StringBuilder source,Text text,boolean history){
        long words=history?H:T,lengths=history?HL:TL;
        for(int i=0;i<text.tokens.size();i++){
            Token token=text.tokens.get(i);put(source,words+i*8,token.id);put(source,lengths+i*8,token.length);
            if(!history){source.append("store8 ").append(NF+i).append(' ').append(token.number==null?0:1).append('\n');
                if(token.number!=null)source.append("fstore ").append(NV+i*8).append(' ').append(token.number).append('\n');}
        }
        bytes(source,history?HRAW:RAW,text.raw);put(source,C+(history?312:304),text.raw.length);
    }
    Text encode(XiSession nativeSession,String library,String prompt,String previous)throws Exception {
        Text input=text(prompt,256),history=text(previous,64);
        StringBuilder source=new StringBuilder("#!reverse-pc-machine-v1\nbudget 100000000\n");
        put(source,C+8,input.tokens.size());put(source,C+16,history.tokens.size());stage(source,input,false);stage(source,history,true);
        nativeSession.run(source.append("call c1_encode_input\nhalt\n").append(library).toString());
        if(nativeSession.number(C+184,8)!=1)throw new IOException("El circuito C1 rechazó el cuadro");
        return input;
    }
}
