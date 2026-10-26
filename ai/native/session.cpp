// I/O adapter only. Reuse the owner's exact pinned bootstrap, serialization,
// QuantumRuntime and XI interpreter. No tokenizer, knowledge or AI in C++.
#define main bbyq_original_reverse_pc_main
#include "reverse_pc.cpp"
#undef main
#include <sys/resource.h>

namespace {
struct WriterLock {
  fs::path path;
  explicit WriterLock(const fs::path& state) : path(state.string()+".lock") {
    if (!fs::create_directory(path)) throw std::runtime_error("state has an active writer");
  }
  ~WriterLock() { std::error_code ignored; fs::remove(path,ignored); }
};
void response(bool ok,const std::string& output) {
  std::cout<<(ok?"OK ":"ERROR ")<<output.size()<<'\n';
  std::cout.write(output.data(),static_cast<std::streamsize>(output.size()));
  std::cout.flush();
}
std::string metrics(const Runtime& runtime) {
  struct rusage usage{};
  if(getrusage(RUSAGE_SELF,&usage)!=0)throw std::runtime_error("resource metrics unavailable");
  long resident=-1;
  std::ifstream status("/proc/self/status");std::string line;
  while(std::getline(status,line)) {
    if(line.compare(0,6,"VmRSS:")==0) { std::istringstream value(line.substr(6));value>>resident;break; }
  }
  std::ostringstream output;
  output<<"{\"method\":\"getrusage_self\",\"peak_rss_kib\":"<<usage.ru_maxrss
        <<",\"resident_rss_kib\":"<<(resident>=0?std::to_string(resident):"null")
        <<",\"cpu_ms\":"<<(usage.ru_utime.tv_sec+usage.ru_stime.tv_sec)*1000.0+
            (usage.ru_utime.tv_usec+usage.ru_stime.tv_usec)/1000.0
        <<",\"active_qubits\":"<<runtime.core().stats().active_qubits<<"}";
  return output.str();
}
}

int main(int argc,char** argv) {
  try {
    if(argc!=3)throw std::invalid_argument("usage: bbyq_session STATE.rvp LINKED.xi");
    const fs::path state=fs::canonical(argv[1]);
    WriterLock lock(state);
    auto current=load_state(state);
    std::string body=read_file(argv[2]);
    const auto newline=body.find('\n');
    if(newline==std::string::npos || body.substr(0,newline)!="#!reverse-pc-machine-v1")
      throw std::invalid_argument("invalid linked XI header");
    body.erase(0,newline+1);
    std::string header;
    // Header: output-language (1/2) and UTF-8 byte count (0..255), then raw bytes.
    // Syntax validation of the QUESTION and all intelligence remain inside XI.
    while(std::getline(std::cin,header)) {
      // Control plane only: no question interpretation or model mutation.
      if(header=="METRICS") { response(true,metrics(current)); continue; }
      if(header.size()>32)throw std::invalid_argument("oversized frame header");
      std::istringstream fields(header);
      unsigned language=0,length=0;std::string extra;
      if(!(fields>>language>>length) || fields>>extra || language<1 || language>2 || length>255)
        throw std::invalid_argument("invalid frame header");
      std::string text(length,'\0');
      std::cin.read(text.data(),static_cast<std::streamsize>(length));
      if(static_cast<unsigned>(std::cin.gcount())!=length)throw std::runtime_error("truncated input frame");
      try {
        std::ostringstream program;
        program<<"#!reverse-pc-machine-v1\n"
               <<"store8 7400000000000000016 1\n"
               <<"store8 7400000000000000017 "<<length<<'\n'
               <<"store8 7400000000000000003 "<<language<<'\n';
        for(unsigned i=0;i<length;++i)
          program<<"store8 "<<(UINT64_C(7400000000000000128)+i)<<' '
                 <<unsigned(static_cast<unsigned char>(text[i]))<<'\n';
        program<<body;
        auto candidate=current;
        const auto output=candidate.execute(program.str());
        // Same RVPC2 atomic publication as reverse_pc run. Announce a
        // response only after save_state succeeds; failed turns keep current.
        save_state(state,candidate);
        current=std::move(candidate);
        response(true,output);
      } catch(const std::exception& error) { response(false,error.what()); }
    }
    return 0;
  } catch(const std::exception& error) {
    std::cerr<<"BBYQ_SESSION_FAIL "<<error.what()<<'\n';return 1;
  }
}
