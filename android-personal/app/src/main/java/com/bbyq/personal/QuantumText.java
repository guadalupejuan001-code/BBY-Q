package com.bbyq.personal;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.Normalizer;
import java.util.*;
import java.util.regex.*;
import org.json.*;

/** Same byte codec as qchat100/engine.py. Features and generation execute in XI. */
final class QuantumText {
    static final long A=8160000000000000000L;
    private static final Pattern WORDS=Pattern.compile("[\\p{L}\\p{N}_]+|[.!?,]");
    static List<String> words(String s) {
        s=Normalizer.normalize(s.toLowerCase(Locale.ROOT),Normalizer.Form.NFD).replaceAll("\\p{M}","");
        List<String> out=new ArrayList<>();Matcher m=WORDS.matcher(s);while(m.find())out.add(m.group());return out;
    }
    static long fnv(String s) {long n=2166136261L;for(byte b:s.getBytes(StandardCharsets.UTF_8))n=((n^(b&255))*16777619L)&0xffffffffL;return n;}
    static Set<String> set(JSONArray a)throws Exception {Set<String> s=new HashSet<>();for(int i=0;i<a.length();i++)s.add(a.getString(i));return s;}
    static int[] bits(String prompt,List<String> prefix,String previous,Set<String> input,Set<String> history) {
        int[] b=new int[100];
        for(String token:words(prompt))if(input.contains(token))for(String salt:new String[]{"a","b","c"})b[(int)(fnv(salt+token)%48)]=1;
        for(String token:words(previous))if(input.contains(token)&&history.contains(token))for(String salt:new String[]{"p","q","r"})b[48+(int)(fnv(salt+token)%16)]=1;
        long h=fnv(prefix.isEmpty()?"<bos>":prefix.get(prefix.size()-1));for(int i=0;i<16;i++)b[64+i]=(int)((h>>>i)&1);
        h=fnv(prefix.size()<2?"<bos>":prefix.get(prefix.size()-2));for(int i=0;i<8;i++)b[80+i]=(int)((h>>>i)&1);
        b[88+Math.min(prefix.size(),11)]=1;return b;
    }
    static String detokenize(List<String> tokens) {
        Map<String,String> proper=new HashMap<>();for(String[] p:new String[][]{{"x","X"},{"bby","BBY"},{"q","Q"},{"xi","XI"},{"ether","Ether"}})proper.put(p[0],p[1]);
        List<String> out=new ArrayList<>();for(String t:tokens)out.add(proper.containsKey(t)?proper.get(t):t);
        String s=String.join(" ",out).replaceAll("\\s+([.!?,])","$1");return s.isEmpty()?s:s.substring(0,1).toUpperCase(Locale.ROOT)+s.substring(1);
    }
    static JSONObject generate(PersonalEngine engine,byte[] state,String prompt,String previous)throws Exception {
        if(XiPages.utf8(prompt).length>512)throw new IOException("QChat100 admite hasta 512 bytes por entrada");
        JSONArray vocabulary=new JSONArray(new String(engine.asset("qchat-vocabulary.json"),StandardCharsets.UTF_8));
        Set<String> inputs=set(new JSONArray(new String(engine.asset("qchat-input-vocabulary.json"),StandardCharsets.UTF_8)));
        Set<String> history=set(new JSONArray(new String(engine.asset("qchat-history-vocabulary.json"),StandardCharsets.UTF_8)));
        String library=new String(engine.asset("qchat-model.xi"),StandardCharsets.UTF_8);
        List<String> prefix=new ArrayList<>();double logp=0;boolean terminated=false;
        try(XiSession xi=new XiSession(state)) {
            for(int i=0;i<16;i++) {
                int[] values=bits(prompt,prefix,previous,inputs,history);StringBuilder body=new StringBuilder("#!reverse-pc-machine-v1\nbudget 50000000\n");
                for(int j=0;j<100;j++)XiPages.put(body,A+1000+j,values[j],1);
                body.append("store64 ").append(A+80).append(" 0\ncall qchat_encode\ncall qchat_next\nhalt\n").append(library);
                String events=xi.run(body.toString());int token=-1;
                for(String line:events.split("\n"))if(line.startsWith("{")){JSONObject e=new JSONObject(line);if(e.optString("type").equals("register")&&e.optString("register").equals("r12"))token=e.getInt("value");}
                logp+=XiPages.metrics(events).getDouble("log_probability");
                if(token==0){terminated=true;break;}
                if(token<0||token>=vocabulary.length())throw new IOException("Token nativo inválido");
                prefix.add(vocabulary.getString(token));
            }
        }
        return new JSONObject().put("response",detokenize(prefix)).put("terminated",terminated).put("tokens",prefix.size()).put("log_probability",logp).put("qubits",100);
    }
}
