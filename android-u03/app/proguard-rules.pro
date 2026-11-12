# Chaquopy's Java/Python bridge exposes members through native code and
# reflection. Avoid renaming or removing these entry points.
-keep class com.chaquo.python.** { *; }
-keep class com.bbyq.u03.U03Runtime { *; }

# Preserve names and signatures for native/JNI methods, including the
# Chaquopy-owned compiled libraries. Never strip JNI entry points.
-keepclasseswithmembers class * {
    native <methods>;
}
-keepattributes *Annotation*,Signature,InnerClasses,EnclosingMethod

# Conversation JSON uses Android's org.json directly (JSONObject/JSONArray),
# not reflection-based custom POJO deserialization. No broad keep of app views
# is required: manifest-declared Activities are R8 entry points.
