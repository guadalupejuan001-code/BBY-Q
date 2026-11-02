// Measurement-only wrapper around the unmodified, pinned XI translation unit.
// The getrusage CPU counters are unchanged; RSS is read from this executable's
// Linux memory image rather than retaining a pre-exec parent's high-water mark.
#include <fstream>
#include <string>
#include <sys/resource.h>

template <class Selector>
int bbyq_reference_getrusage(Selector who, struct rusage* usage) {
  const int result = ::getrusage(who, usage);
  if (result == 0 && who == RUSAGE_SELF) {
    std::ifstream status("/proc/self/status");
    std::string line;
    while (std::getline(status, line))
      if (line.compare(0, 6, "VmHWM:") == 0)
        usage->ru_maxrss = std::stol(line.substr(6));
  }
  return result;
}

#define getrusage bbyq_reference_getrusage
#include BBYQ_XI_SOURCE
#undef getrusage
