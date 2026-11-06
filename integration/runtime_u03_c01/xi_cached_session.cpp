// C01 opt-in host transport. Uses the *original* REVERSE-PC Runtime.
// CODELIB + EXECREF replace redundant IPC of unchanged XI library text.
// The exact original XI source is reconstructed before Runtime::execute.
// Does not cache quantum state, alter execution, bypass validation or write APKs.
#define main reverse_pc_embedded_cli_main
#include "reverse_pc.cpp"
#undef main
#include <sys/resource.h>
#include <vector>

namespace {
constexpr std::size_t kPacketLimit = 16ULL * 1024 * 1024;
constexpr std::size_t kLibraryBudget = 16ULL * 1024 * 1024;
constexpr std::size_t kMaxLibraries = 128;

void respond(bool ok, const std::string& body) {
  std::cout << (ok ? "OK " : "ERROR ") << body.size() << '\n';
  std::cout.write(body.data(), static_cast<std::streamsize>(body.size()));
  std::cout.flush();
}

std::string recv(std::size_t n) {
  if (n > kPacketLimit) throw std::length_error("C01 packet larger than 16 MiB");
  std::string data(n, '\0');
  std::cin.read(data.data(), static_cast<std::streamsize>(n));
  if (static_cast<std::size_t>(std::cin.gcount()) != n)
    throw std::runtime_error("C01 transport was truncated");
  return data;
}

std::string metrics_json(const Runtime& current) {
  struct rusage usage {};
  if (getrusage(RUSAGE_SELF, &usage)) throw std::runtime_error("getrusage failed");
  long peak = usage.ru_maxrss;
  bool linux_hwm = false;
  std::ifstream status("/proc/self/status");
  std::string line;
  while (std::getline(status, line))
    if (line.compare(0, 6, "VmHWM:") == 0) {
      peak = std::stol(line.substr(6));
      linux_hwm = true;
      break;
    }
  const auto stats = current.core().stats();
  std::ostringstream out;
  out << std::setprecision(17)
      << "{\"peak_rss_kib\":" << peak
      << ",\"rusage_peak_rss_kib\":" << usage.ru_maxrss
      << ",\"rss_measurement\":\"" << (linux_hwm ? "Linux VmHWM after exec" : "getrusage") << "\""
      << ",\"cpu_ms\":"
      << (usage.ru_utime.tv_sec + usage.ru_stime.tv_sec) * 1000. +
             (usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) / 1000.
      << ",\"active_qubits\":" << stats.active_qubits
      << ",\"quantum_payload_bytes\":" << current.core().quantum_stats().payload_bytes
      << "}";
  return out.str();
}

std::size_t parse_library_id(const std::string& value, std::size_t count) {
  if (value.empty() || value.size() > 12 ||
      value.find_first_not_of("0123456789") != std::string::npos)
    throw std::invalid_argument("Invalid cached library identifier");
  const unsigned long long id = std::stoull(value);
  if (!id || id > count)
    throw std::invalid_argument("Unknown cached library identifier");
  return static_cast<std::size_t>(id - 1);
}
} // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 2) throw std::invalid_argument("usage: xi_session_c01 INPUT.rvp");
    auto current = load_state(argv[1]);
    std::vector<std::string> libraries;
    std::size_t library_bytes = 0;
    std::string header;
    while (std::getline(std::cin, header)) {
      if (header.size() > 64) throw std::length_error("C01 header too long");
      std::istringstream in(header);
      std::string command, extra;
      std::size_t length = 0;
      in >> command;
      if (command == "METRICS" && !(in >> extra)) {
        respond(true, metrics_json(current));
        continue;
      }
      if (command == "C01CAP" && !(in >> extra)) {
        respond(true, "{\"cached_library_transport\":1,\"source_execution\":\"original XI Runtime\"}");
        continue;
      }
      if (!(in >> length) || (in >> extra) ||
          (command != "EXEC" && command != "SAVE" && command != "CODELIB" &&
           command != "EXECREF" && command != "RESTORE"))
        throw std::invalid_argument("Expected EXEC/SAVE/CODELIB/EXECREF/RESTORE n or METRICS");
      const auto payload = recv(length);
      try {
        if (command == "SAVE") {
          if (payload.empty() || payload.find('\0') != std::string::npos)
            throw std::invalid_argument("invalid checkpoint path");
          if (fs::exists(payload))
            throw std::invalid_argument("checkpoint exists; choose a new path");
          save_state(payload, current);
          respond(true, "{}");
        } else if (command == "RESTORE") {
          // Fully authenticate the replacement RVPC2 before touching the live
          // runtime. All state, memory revisions and RNG come from the file.
          if (payload.empty() || payload.find('\0') != std::string::npos)
            throw std::invalid_argument("Invalid C01 RESTORE path");
          // load_state checks checksum, exact size and both authorities.
          // After validation, move the complete owner directly rather than
          // snapshotting/restoring the already validated state a second time.
          auto replacement = load_state(payload);
          current = std::move(replacement);
          respond(true, "{}");
        } else if (command == "EXEC") {
          respond(true, current.execute(payload));
        } else if (command == "CODELIB") {
          if (payload.empty() || libraries.size() >= kMaxLibraries ||
              payload.size() > kLibraryBudget - library_bytes)
            throw std::length_error("C01 library capacity exceeded");
          // No user code executes when a library is registered.
          libraries.push_back(payload);
          library_bytes += payload.size();
          respond(true, std::to_string(libraries.size()));
        } else {
          const auto newline = payload.find('\n');
          if (newline == std::string::npos)
            throw std::invalid_argument("Missing cached library ID separator");
          const auto index = parse_library_id(payload.substr(0, newline), libraries.size());
          const std::string body = payload.substr(newline + 1);
          const std::string ending = "\nhalt\n";
          if (body.size() < ending.size() ||
              body.compare(body.size() - ending.size(), ending.size(), ending) != 0)
            throw std::invalid_argument("C01 prelude must end with newline-halt-newline");
          if (libraries[index].size() > kPacketLimit - body.size())
            throw std::length_error("Combined XI source exceeds 16 MiB");
          // Byte-for-byte reconstruction; the original XI interpreter still
          // handles execution, rollback, validation and RNG.
          respond(true, current.execute(body + libraries[index]));
        }
      } catch (const std::exception& e) {
        respond(false, e.what());
      }
    }
    return 0;
  } catch (const std::exception& e) {
    std::cerr << "XI_C01_FAIL " << e.what() << '\n';
    return 1;
  }
}
