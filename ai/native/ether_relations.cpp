// BBY Q E003: native spatial relation operator over REVERSE-PC QuantumRuntime.
// InverseMemory logical coordinates are the ONLY authority for learned rules.
// Uses the pinned Mundo X / REVERSE-PC implementation, not another AI.
#include "mundo_x/quantum_runtime.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>

namespace fs = std::filesystem;
using Runtime = mundo_x::QuantumRuntime;
namespace {
constexpr std::uint64_t SPACE = UINT64_C(7000000000000000000);
constexpr std::uint64_t MAX_BYTES = 32ULL*1024ULL*1024ULL;
constexpr std::uint64_t FNV_BASE = UINT64_C(14695981039346656037);
constexpr std::uint64_t FNV_MULT = UINT64_C(1099511628211);
constexpr unsigned FEATURE_COUNT = 5;
constexpr std::array<const char*,FEATURE_COUNT> RELATIONS = {
  "bias","signal","pressure","action","signal_action"};

void require(bool ok,const std::string& why) {
  if(!ok) throw std::runtime_error(why);
}
std::string address(std::uint64_t index) { return std::to_string(SPACE+index); }

// RVPC2 framing interoperable with original REVERSE-PC, not a second engine.
// FNV detects accidental corruption only; not a cryptographic authenticator.
std::uint64_t fnv(const std::string& core,const std::string& memory) {
  std::uint64_t h=FNV_BASE;
  for(const auto& data:{core,memory})
    for(unsigned char c:data) {h^=c;h*=FNV_MULT;}
  return h;
}
void write64(std::ostream& s,std::uint64_t v) {
  for(int i=0;i<8;++i)s.put(static_cast<char>((v>>(i*8))&255));
}
std::uint64_t read64(std::istream& s) {
  std::uint64_t v=0;
  for(int i=0;i<8;++i) {
    int c=s.get();require(c!=EOF,"truncated RVPC2 header");
    v|=std::uint64_t(static_cast<unsigned>(c))<<(i*8);
  }
  return v;
}
Runtime load(const fs::path& p) {
  require(fs::is_regular_file(p)&&fs::file_size(p)<=MAX_BYTES+29,
          "missing/oversized spatial state");
  std::ifstream in(p,std::ios::binary);require(bool(in),"cannot open RVPC2");
  char magic[5]{};
  in.read(magic,5);
  require(std::string(magic,5)=="RVPC2","native spatial path requires RVPC2");
  const auto nc=read64(in),nm=read64(in),digest=read64(in);
  require(nc<=MAX_BYTES&&nm<=MAX_BYTES&&nc<=MAX_BYTES-nm,"RVPC2 size budget");
  std::string core(static_cast<std::size_t>(nc),'\0');
  std::string memory(static_cast<std::size_t>(nm),'\0');
  in.read(core.data(),static_cast<std::streamsize>(nc));
  require(static_cast<std::uint64_t>(in.gcount())==nc,"short RVPC2 core");
  in.read(memory.data(),static_cast<std::streamsize>(nm));
  require(static_cast<std::uint64_t>(in.gcount())==nm,"short RVPC2 memory");
  require(in.peek()==EOF&&fnv(core,memory)==digest,"RVPC2 payload/checksum mismatch");
  Runtime r;r.restore(core,memory);
  require(r.core_snapshot()==core&&r.memory_persistent_snapshot()==memory,
          "RVPC2 restored state mismatch");
  return r;
}
void save(const fs::path& p,const Runtime& r) {
  const auto core=r.core_snapshot(),memory=r.memory_persistent_snapshot();
  require(core.size()<=MAX_BYTES&&memory.size()<=MAX_BYTES-core.size(),
          "RVPC2 exceeds 32 MiB");
  fs::create_directories(p.parent_path().empty()?fs::path("."):p.parent_path());
  const fs::path pending=p.string()+".pending";
  try {
    std::ofstream out(pending,std::ios::binary|std::ios::trunc);
    require(bool(out),"cannot write pending RVPC2");
    out.write("RVPC2",5);
    write64(out,core.size());write64(out,memory.size());
    write64(out,fnv(core,memory));
    out.write(core.data(),static_cast<std::streamsize>(core.size()));
    out.write(memory.data(),static_cast<std::streamsize>(memory.size()));
    out.close();require(bool(out),"failed writing RVPC2");
    fs::rename(pending,p);
  } catch(...) {std::error_code ec;fs::remove(pending,ec);throw;}
}
struct Lock {
  int fd=-1;
  explicit Lock(const fs::path& p) {
    fs::create_directories(p.parent_path().empty()?fs::path("."):p.parent_path());
    fd=::open((p.string()+".lock").c_str(),O_CREAT|O_RDWR,0600);
    require(fd>=0,"cannot open state lock");
    if(::flock(fd,LOCK_EX)!=0){::close(fd);throw std::runtime_error("cannot lock");}
  }
  ~Lock(){if(fd>=0){::flock(fd,LOCK_UN);::close(fd);}}
  Lock(const Lock&)=delete;Lock& operator=(const Lock&)=delete;
};
unsigned read_byte(const Runtime& r,std::uint64_t offset) {
  const auto item=r.memory().read(address(offset),r.core());
  require(item.deterministic,"implicit quantum measurement forbidden");
  return item.value;
}
void assert_birth(const Runtime& r) {
  require(read_byte(r,0)==66&&read_byte(r,1)==81&&read_byte(r,2)==3,
          "not BBY Q spatial entity: refusing legacy JSON reinterpretation");
  require(r.core().stats().active_qubits==0&&r.memory().stats().quantum_bindings==0,
          "spatial learner refuses quantum bindings");
}
std::uint32_t step_count(const Runtime& r) {
  std::uint32_t n=0;
  for(unsigned i=0;i<4;++i)n|=(read_byte(r,8+i)<<(8*i));
  return n;
}
int weight(const Runtime& r,unsigned i) {
  require(i<FEATURE_COUNT,"invalid relation index");
  const int v=static_cast<int>(read_byte(r,64+i));
  return v<128?v:v-256;
}
std::array<double,FEATURE_COUNT> activation(double s,double p,int a) {
  require(std::isfinite(s)&&std::isfinite(p)&&std::abs(s)<=1.0&&std::abs(p)<=1.0,
          "signals must be finite in [-1,1]");
  require(a==-1||a==1,"action must be -1 or 1");
  return {1.0,s,p,double(a),s*double(a)};
}
struct Prediction {int output;double score;};
Prediction predict(const Runtime& r,double s,double p,int a) {
  const auto act=activation(s,p,a);double score=0;
  for(unsigned i=0;i<FEATURE_COUNT;++i)score+=weight(r,i)*act[i];
  return {int(score>=0.0),score};
}
std::string prediction_json(const Prediction& v,std::uint32_t steps) {
  std::ostringstream o;o<<std::setprecision(12)
    <<"{\"prediction\":"<<v.output<<",\"score\":"<<v.score
    <<",\"steps\":"<<steps<<"}";
  return o.str();
}
std::string observe(Runtime& r,double s,double p,int a,int y) {
  require(y==0||y==1,"outcome must be 0 or 1");
  const auto before=predict(r,s,p,a);
  const auto act=activation(s,p,a);
  const auto steps=step_count(r);
  require(steps<std::numeric_limits<std::uint32_t>::max(),"step counter saturated");
  std::ostringstream xi;unsigned changes=0;
  // An error reinforces local relations with signed evidence; absent cells
  // have the implicit zero rule. Environment coefficients are never supplied.
  if(before.output!=y) {
    const int direction=y?1:-1;
    for(unsigned i=0;i<FEATURE_COUNT;++i) {
      const double evidence=direction*act[i];
      const int delta=evidence>.25?1:(evidence<-.25?-1:0);
      if(!delta)continue;
      const int old=weight(r,i),next=std::clamp(old+delta,-48,48);
      if(next!=old) {
        xi<<"mem_store "<<address(64+i)<<' '<<(next<0?next+256:next)<<'\n';
        ++changes;
      }
    }
  }
  const auto n=steps+1;
  for(unsigned i=0;i<4;++i) {
    unsigned octet=(n>>(8*i))&255u;
    if(octet!=read_byte(r,8+i))xi<<"mem_store "<<address(8+i)<<' '<<octet<<'\n';
  }
  // ONE XI transaction contains changed relations and step counter.
  r.execute(xi.str());
  std::ostringstream o;o<<std::setprecision(12)
    <<"{\"prediction_before_feedback\":"<<before.output
    <<",\"score_before_feedback\":"<<before.score
    <<",\"outcome\":"<<y<<",\"updates\":"<<changes
    <<",\"steps\":"<<n<<"}";
  return o.str();
}
std::string inspect(const Runtime& r,const fs::path& path) {
  const auto m=r.memory().stats();
  const auto q=r.core().stats();
  std::ostringstream o;
  o<<"{\"schema\":\"BBYQ-SPACE-3\",\"steps\":"<<step_count(r)
   <<",\"rvpc2_bytes\":"<<fs::file_size(path)
   <<",\"logical_overrides\":"<<m.overrides
   <<",\"quantum_bindings\":"<<m.quantum_bindings
   <<",\"active_qubits\":"<<q.active_qubits<<",\"relations\":{";
  for(unsigned i=0;i<FEATURE_COUNT;++i){
    if(i)o<<',';
    o<<'\"'<<RELATIONS[i]<<"\":";
    o<<weight(r,i);
  }
  o<<"}}";return o.str();
}
int parse_int(const char* s) {
  std::size_t used=0;int v=std::stoi(s,&used);
  require(used==std::string(s).size(),"invalid integer argument");
  return v;
}
double parse_double(const char* s) {
  std::size_t used=0;double v=std::stod(s,&used);
  require(used==std::string(s).size()&&std::isfinite(v),"invalid decimal argument");
  return v;
}
void session(Runtime& r,const fs::path& path) {
  std::string line,all;bool changed=false;std::size_t count=0;
  while(std::getline(std::cin,line)) {
    if(line.empty())continue;
    std::istringstream s(line);char mode;double sig,pressure;int action,y;
    require(bool(s>>mode>>sig>>pressure>>action),"invalid session input");
    require(++count<=100000,"session budget exceeded");
    activation(sig,pressure,action);
    if(mode=='L') {
      require(bool(s>>y),"missing feedback");
      std::string extra;require(!(s>>extra),"unexpected session tokens");
      all+=observe(r,sig,pressure,action,y)+'\n';changed=true;
    } else if(mode=='P') {
      std::string extra;require(!(s>>extra),"unexpected session tokens");
      all+=prediction_json(predict(r,sig,pressure,action),step_count(r))+'\n';
    } else throw std::runtime_error("unknown session operation");
    require(all.size()<=16*1024*1024,"session output budget exceeded");
  }
  // Nothing is published or persisted for a partially failed session.
  if(changed)save(path,r);
  std::cout<<all;
}
} // namespace

int main(int argc,char** argv) {
  try {
    require(argc>=3,"usage: bbyq-space new|inspect|predict|learn|session FILE [s p action [outcome]]");
    const std::string cmd=argv[1];const fs::path path=fs::absolute(argv[2]);
    Lock lock(path);
    if(cmd=="new"&&argc==3) {
      require(!fs::exists(path),"entity exists; refusing overwrite");
      Runtime r;
      r.execute("mem_store "+address(0)+" 66\nmem_store "+address(1)
                +" 81\nmem_store "+address(2)+" 3\n");
      save(path,r);assert_birth(r);
      std::cout<<inspect(r,path)<<'\n';return 0;
    }
    Runtime r=load(path);assert_birth(r);
    if(cmd=="inspect"&&argc==3)
      std::cout<<inspect(r,path)<<'\n';
    else if(cmd=="predict"&&argc==6)
      std::cout<<prediction_json(predict(r,parse_double(argv[3]),
                 parse_double(argv[4]),parse_int(argv[5])),step_count(r))<<'\n';
    else if(cmd=="learn"&&argc==7) {
      const auto record=observe(r,parse_double(argv[3]),parse_double(argv[4]),
                                parse_int(argv[5]),parse_int(argv[6]));
      save(path,r);std::cout<<record<<'\n';
    } else if(cmd=="session"&&argc==3)
      session(r,path);
    else throw std::runtime_error("invalid command/arguments");
    return 0;
  } catch(const std::exception& e) {
    std::cerr<<"BBYQ_SPACE_FAIL "<<e.what()<<'\n';return 1;
  }
}