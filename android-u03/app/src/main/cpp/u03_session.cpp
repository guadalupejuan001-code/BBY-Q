// Android transport only. RVPC2/Ether execution and checkpoint format remain original.
#include "rvpc2.hpp"
#include "rxe.hpp"
#include <jni.h>
#include <map>
#include <memory>
#include <mutex>
#include <limits>
#include <string>
#include <vector>
#include <stdexcept>
namespace {
using Runtime=reverse_pc::rvpc2::Runtime;
struct Slot { std::unique_ptr<Runtime> runtime; std::map<jlong,std::string> libraries; jlong next_library=0; };
std::mutex guard;
std::map<jlong,Slot> slots;
jlong next_session=0;
void fail(JNIEnv* env,const std::exception& error) {
 if(!env->ExceptionCheck()) env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),error.what());
}
std::vector<std::uint8_t> bytes(JNIEnv* env,jbyteArray value) {
 if(!value) return {};
 const auto n=env->GetArrayLength(value);
 if(n<0 || std::size_t(n)>reverse_pc::rvpc2::max_state+29) throw std::length_error("XI state input size");
 std::vector<std::uint8_t> out(n);
 env->GetByteArrayRegion(value,0,n,reinterpret_cast<jbyte*>(out.data()));
 if(env->ExceptionCheck()) throw std::runtime_error("XI byte input failed");
 return out;
}
std::string text(JNIEnv* env,jstring value) {
 if(!value || env->GetStringUTFLength(value)>16*1024*1024) throw std::length_error("XI program input size");
 const char* p=env->GetStringUTFChars(value,nullptr);
 if(!p) throw std::runtime_error("XI UTF input failed");
 std::string out(p);env->ReleaseStringUTFChars(value,p);return out;
}
jbyteArray output(JNIEnv* env,const std::vector<std::uint8_t>& value) {
 if(value.size()>32*1024*1024+29) throw std::length_error("XI state output size");
 auto out=env->NewByteArray(jsize(value.size()));
 if(out && !value.empty()) env->SetByteArrayRegion(out,0,jsize(value.size()),reinterpret_cast<const jbyte*>(value.data()));
 return out;
}
Slot& get(jlong id) {
 auto it=slots.find(id);if(it==slots.end()) throw std::invalid_argument("Closed XI session");return it->second;
}
jbyteArray execute(JNIEnv* env,Slot& slot,const std::string& source) {
 const auto events=slot.runtime->execute(source);
 return output(env,std::vector<std::uint8_t>(events.begin(),events.end()));
}
}
extern "C" JNIEXPORT jlong JNICALL Java_com_bbyq_personal_XiSession_open(JNIEnv* e,jclass,jbyteArray seed) {
 try {
  auto runtime=std::make_unique<Runtime>(seed?reverse_pc::rvpc2::restore(bytes(e,seed)):Runtime{});
  std::lock_guard<std::mutex> lock(guard);
  if(slots.size()>=8 || next_session==std::numeric_limits<jlong>::max()) throw std::length_error("XI native session budget exhausted (8 handles)");
  const auto id=++next_session;Slot s;s.runtime=std::move(runtime);slots.emplace(id,std::move(s));return id;
 }catch(const std::exception& x){fail(e,x);return 0;}
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_execute(JNIEnv* e,jclass,jlong id,jstring source) {
 try {const auto code=text(e,source);std::lock_guard<std::mutex> lock(guard);return execute(e,get(id),code);}catch(const std::exception& x){fail(e,x);return nullptr;}
}
extern "C" JNIEXPORT jlong JNICALL Java_com_bbyq_personal_XiSession_registerLibrary(JNIEnv* e,jclass,jlong id,jstring library) {
 try {
  const auto code=text(e,library);std::lock_guard<std::mutex> lock(guard);auto& s=get(id);
  if(s.next_library==std::numeric_limits<jlong>::max()) throw std::overflow_error("XI library handle overflow");
  for(const auto& item:s.libraries) if(item.second==code) return item.first;
  const auto handle=++s.next_library;s.libraries.emplace(handle,code);return handle;
 }catch(const std::exception& x){fail(e,x);return 0;}
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_executeRef(JNIEnv* e,jclass,jlong id,jlong library,jstring prelude) {
 try {
  const auto head=text(e,prelude);std::lock_guard<std::mutex> lock(guard);auto& s=get(id);
  auto found=s.libraries.find(library);if(found==s.libraries.end()) throw std::invalid_argument("Unknown XI code library handle");
  if(head.size()+found->second.size()>16*1024*1024) throw std::length_error("XI reconstructed source too large");
  // Same original code, same order, same runtime; only duplicate JNI transfer is avoided.
  return execute(e,s,head+found->second);
 }catch(const std::exception& x){fail(e,x);return nullptr;}
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_executeRxe(JNIEnv* e,jclass,jlong id,jbyteArray code) {
 try {const auto source=reverse_pc::rxe::disassemble(reverse_pc::rxe::decode(bytes(e,code)));std::lock_guard<std::mutex> lock(guard);return execute(e,get(id),source);}catch(const std::exception& x){fail(e,x);return nullptr;}
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_checkpoint(JNIEnv* e,jclass,jlong id) {
 try {std::lock_guard<std::mutex> lock(guard);return output(e,reverse_pc::rvpc2::save(*get(id).runtime));}catch(const std::exception& x){fail(e,x);return nullptr;}
}
extern "C" JNIEXPORT jbyteArray JNICALL Java_com_bbyq_personal_XiSession_read(JNIEnv* e,jclass,jlong id,jlong address,jint size) {
 try {
  if(address<0 || size<0 || size>65536 || address>std::numeric_limits<jlong>::max()-size) throw std::length_error("XI byte read bounds");
  std::lock_guard<std::mutex> lock(guard);auto& rt=*get(id).runtime;std::vector<std::uint8_t> value(size);
  for(int i=0;i<size;++i){const auto b=rt.memory().read(std::to_string(address+i),rt.core());if(!b.deterministic)throw std::runtime_error("Quantum byte requires explicit measurement");value[i]=b.value;}
  return output(e,value);
 }catch(const std::exception& x){fail(e,x);return nullptr;}
}
extern "C" JNIEXPORT void JNICALL Java_com_bbyq_personal_XiSession_release(JNIEnv*,jclass,jlong id){std::lock_guard<std::mutex> lock(guard);slots.erase(id);}
extern "C" JNIEXPORT jstring JNICALL Java_com_bbyq_personal_XiSession_capabilities(JNIEnv* e,jclass){return e->NewStringUTF("{\"runtime\":\"original-RVPC2-XI\",\"library_transport\":true,\"cached_inference\":false,\"elf_target_alignment\":16384}");}
