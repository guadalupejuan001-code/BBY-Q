#include "rvpc2.hpp"
#include "rxe.hpp"
#include <jni.h>
#include <map>
#include <memory>
#include <mutex>
#include <limits>

namespace {
using Runtime = reverse_pc::rvpc2::Runtime;
std::mutex lock;
std::map<jlong, std::unique_ptr<Runtime>> sessions;
jlong serial = 0;
void fail(JNIEnv* env, const std::exception& err) {
    if (!env->ExceptionCheck()) env->ThrowNew(env->FindClass("java/lang/IllegalStateException"), err.what());
}
std::vector<std::uint8_t> input(JNIEnv* env, jbyteArray value) {
    if (!value) return {};
    const auto n = env->GetArrayLength(value);
    if (n < 0 || std::size_t(n) > reverse_pc::rvpc2::max_state + 29) throw std::length_error("XI input limit");
    std::vector<std::uint8_t> out(n);
    env->GetByteArrayRegion(value, 0, n, reinterpret_cast<jbyte*>(out.data()));
    if (env->ExceptionCheck()) throw std::runtime_error("XI byte transfer failed");
    return out;
}
jbyteArray output(JNIEnv* env, const std::vector<std::uint8_t>& value) {
    if (value.size() > 32 * 1024 * 1024 + 29) throw std::length_error("XI output limit");
    auto out = env->NewByteArray(jsize(value.size()));
    if (out && !value.empty()) env->SetByteArrayRegion(out, 0, jsize(value.size()), reinterpret_cast<const jbyte*>(value.data()));
    return out;
}
Runtime& get(jlong handle) {
    const auto it = sessions.find(handle);
    if (it == sessions.end()) throw std::invalid_argument("Closed XI session");
    return *it->second;
}
}
extern "C" JNIEXPORT jlong JNICALL Java_com_bbyq_personal_XiSession_open(JNIEnv* e,jclass,jbyteArray seed) {
    try {
        auto runtime = std::make_unique<Runtime>(seed ? reverse_pc::rvpc2::restore(input(e,seed)) : Runtime{});
        std::lock_guard<std::mutex> guard(lock);
        if (sessions.size() >= 8 || serial == std::numeric_limits<jlong>::max()) throw std::length_error("XI session limit");
        const auto id = ++serial; sessions.emplace(id,std::move(runtime)); return id;
    } catch (const std::exception& x) { fail(e,x); return 0; }
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_execute(JNIEnv* e,jclass,jlong id,jstring program) {
    try {
        if (!program || e->GetStringUTFLength(program) > 16*1024*1024) throw std::length_error("XI program limit");
        const char* text = e->GetStringUTFChars(program,nullptr);
        if (!text) return nullptr;
        std::string source(text); e->ReleaseStringUTFChars(program,text);
        std::lock_guard<std::mutex> guard(lock);
        const auto events = get(id).execute(source);
        return output(e,{events.begin(),events.end()});
    } catch (const std::exception& x) { fail(e,x); return nullptr; }
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_executeRxe(JNIEnv* e,jclass,jlong id,jbyteArray program) {
    try {
        const auto source = reverse_pc::rxe::disassemble(reverse_pc::rxe::decode(input(e,program)));
        std::lock_guard<std::mutex> guard(lock); const auto events = get(id).execute(source);
        return output(e,{events.begin(),events.end()});
    } catch (const std::exception& x) { fail(e,x); return nullptr; }
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_read(JNIEnv* e,jclass,jlong id,jlong address,jint length) {
    try {
        if (address < 0 || length < 0 || length > 65536 || address > std::numeric_limits<jlong>::max()-length) throw std::length_error("XI page limit");
        std::lock_guard<std::mutex> guard(lock); auto& rt = get(id);
        std::vector<std::uint8_t> out(length);
        for (int i=0;i<length;i++) {
            const auto value = rt.memory().read(std::to_string(address+i),rt.core());
            if (!value.deterministic) throw std::runtime_error("Quantum byte requires an explicit measurement");
            out[i]=value.value;
        }
        return output(e,out);
    } catch (const std::exception& x) { fail(e,x); return nullptr; }
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_checkpoint(JNIEnv* e,jclass,jlong id) {
    try { std::lock_guard<std::mutex> guard(lock); return output(e,reverse_pc::rvpc2::save(get(id))); }
    catch (const std::exception& x) { fail(e,x); return nullptr; }
}
extern "C" JNIEXPORT void JNICALL Java_com_bbyq_personal_XiSession_release(JNIEnv*,jclass,jlong id) {
    std::lock_guard<std::mutex> guard(lock); sessions.erase(id);
}
