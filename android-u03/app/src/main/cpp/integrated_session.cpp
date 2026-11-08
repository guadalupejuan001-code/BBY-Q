// Additive Android transport: original RVPC2 implementation is included unchanged.
#include "personal_session.cpp"
#include <algorithm>
#include <sstream>
#include <unistd.h>

namespace {
struct MobileLibraries {
    std::vector<std::string> code;
    std::size_t bytes = 0;
    std::uint64_t execs = 0, sent = 0, reconstructed = 0;
};
std::map<jlong, MobileLibraries> mobile_libraries;
std::string mobile_text(JNIEnv* env, jstring value) {
    if (!value || env->GetStringUTFLength(value) > 16 * 1024 * 1024)
        throw std::length_error("Invalid XI program size");
    const char* text = env->GetStringUTFChars(value, nullptr);
    if (!text) throw std::runtime_error("JNI UTF-8 transfer failed");
    std::string result(text);
    env->ReleaseStringUTFChars(value, text);
    return result;
}
}
extern "C" JNIEXPORT jint JNICALL
Java_com_bbyq_personal_XiSession_internLibrary(JNIEnv* env, jclass, jlong id, jstring text) {
    try {
        const std::string source = mobile_text(env, text);
        std::lock_guard<std::mutex> guard(lock);
        get(id); // Validate against the original live RVPC2 handle registry.
        auto& item = mobile_libraries[id];
        const auto found = std::find(item.code.begin(), item.code.end(), source);
        if (found != item.code.end()) return jint(found - item.code.begin());
        if (item.code.size() >= 128 || item.bytes + source.size() > 16 * 1024 * 1024)
            throw std::length_error("XI source-library budget exceeded");
        item.bytes += source.size();
        item.sent += source.size();
        item.code.push_back(source);
        return jint(item.code.size() - 1);
    } catch (const std::exception& err) { fail(env, err); return -1; }
}
extern "C" JNIEXPORT jbyteArray JNICALL
Java_com_bbyq_personal_XiSession_executeReference(JNIEnv* env, jclass, jlong id, jint library, jstring prefix) {
    try {
        const std::string code = mobile_text(env, prefix);
        std::lock_guard<std::mutex> guard(lock);
        auto& runtime = get(id);
        const auto found = mobile_libraries.find(id);
        if (found == mobile_libraries.end() || library < 0 || std::size_t(library) >= found->second.code.size())
            throw std::invalid_argument("Unknown XI library reference; no execution");
        auto& item = found->second;
        const std::string source = code + item.code[std::size_t(library)];
        if (source.size() > 16 * 1024 * 1024) throw std::length_error("XI reconstructed program exceeds original budget");
        // No cached answers, gradients, instructions or state are substituted.
        const auto events = runtime.execute(source);
        ++item.execs;
        item.sent += code.size();
        item.reconstructed += source.size();
        return output(env, {events.begin(), events.end()});
    } catch (const std::exception& err) { fail(env, err); return nullptr; }
}
extern "C" JNIEXPORT jstring JNICALL
Java_com_bbyq_personal_XiSession_transportMetrics(JNIEnv* env, jclass, jlong id) {
    try {
        std::lock_guard<std::mutex> guard(lock);
        get(id);
        const auto found = mobile_libraries.find(id);
        MobileLibraries empty;
        const auto& item = found == mobile_libraries.end() ? empty : found->second;
        std::ostringstream json;
        json << "{\"libraries\":" << item.code.size() << ",\"resident_source_bytes\":" << item.bytes
             << ",\"native_reference_executions\":" << item.execs << ",\"transferred_bytes\":" << item.sent
             << ",\"reconstructed_source_bytes\":" << item.reconstructed << ",\"page_size\":" << sysconf(_SC_PAGESIZE)
             << ",\"cached_inference_results\":false}";
        return env->NewStringUTF(json.str().c_str());
    } catch (const std::exception& err) { fail(env, err); return nullptr; }
}
extern "C" JNIEXPORT void JNICALL
Java_com_bbyq_personal_XiSession_releaseIntegrated(JNIEnv*, jclass, jlong id) {
    std::lock_guard<std::mutex> guard(lock);
    mobile_libraries.erase(id);
    sessions.erase(id);
}
