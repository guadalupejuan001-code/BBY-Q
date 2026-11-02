// Independent numerical reference and benchmark, not a replacement BBY Q agent.
// qsim is Apache-2.0: https://github.com/quantumlib/qsim/blob/main/LICENSE
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sys/resource.h>
#include <vector>

#include "lib/seqfor.h"
#include "lib/simulator_basic.h"

using Simulator = qsim::SimulatorBasic<qsim::SequentialFor, double>;
using Space = Simulator::StateSpace;
using Values = std::array<double, 1000>;

struct Input {
  unsigned role, block;
  double bias, label;
  Values x, theta, weights;
};
struct Output {
  Values z{};
  double score = 0, probability = 0;
};

class ProductReference {
 public:
  ProductReference() : simulator_(1), space_(1) {
    // Keep both 1000-wire registers allocated simultaneously. Every block of
    // the selected register is reset, evolved and measured on every forward.
    states_.reserve(500);
    for (unsigned i = 0; i < 500; ++i) {
      auto state = Space::Create(4);
      if (Space::IsNull(state)) throw std::runtime_error("qsim allocation");
      space_.SetStateZero(state);
      states_.push_back(std::move(state));
    }
  }

  Output forward(const Input& input) {
    Output output;
    for (unsigned b = 0; b < 250; ++b) {
      const auto z = block(input, b, -1, 0);
      for (unsigned j = 0; j < 4; ++j) {
        output.z[4*b+j] = z[j];
        output.score += input.weights[4*b+j] * z[j];
      }
    }
    output.score = std::clamp(output.score / std::sqrt(1000.) + input.bias, -25., 25.);
    output.probability = 1. / (1. + std::exp(-output.score));
    return output;
  }

  std::array<double, 4> gradients(const Input& input) {
    std::array<double, 4> result{};
    const double half_pi = std::acos(-1.) / 2.;
    for (unsigned j = 0; j < 4; ++j) {
      const auto positive = block(input, input.block, int(j), half_pi);
      const auto negative = block(input, input.block, int(j), -half_pi);
      double plus = 0, minus = 0;
      for (unsigned k = 0; k < 4; ++k) {
        plus += input.weights[4*input.block+k] * positive[k];
        minus += input.weights[4*input.block+k] * negative[k];
      }
      result[j] = (plus-minus) / (2.*std::sqrt(1000.));
    }
    return result;
  }

 private:
  std::array<double, 4> block(const Input& input, unsigned b, int shifted, double shift) {
    auto& state = states_[250*input.role+b];
    space_.SetStateZero(state);
    for (unsigned j = 0; j < 4; ++j) ry(j, input.x[4*b+j], state);
    const double x[8] = {0,0,1,0,1,0,0,0};
    for (unsigned j = 0; j < 3; ++j)
      simulator_.ApplyControlledGate({j+1}, {j}, 1, x, state);
    for (unsigned j = 0; j < 4; ++j)
      ry(j, input.theta[4*b+j] + (int(j)==shifted ? shift : 0), state);
    std::array<double, 4> result{};
    const double z[8] = {1,0,0,0,0,0,-1,0};
    for (unsigned j = 0; j < 4; ++j)
      result[j] = simulator_.ExpectationValue({j}, z, state).real();
    return result;
  }

  void ry(unsigned q, double angle, Space::State& state) {
    const double c = std::cos(angle/2.), s = std::sin(angle/2.);
    const double matrix[8] = {c,0,-s,0,s,0,c,0};
    simulator_.ApplyGate({q}, matrix, state);
  }
  Simulator simulator_;
  Space space_;
  std::vector<Space::State> states_;
};

template <class Container> void array_json(const Container& values) {
  std::cout << '[';
  bool first = true;
  for (const auto value : values) {
    if (!first) std::cout << ',';
    first = false;
    std::cout << value;
  }
  std::cout << ']';
}

int main(int argc, char** argv) {
  try {
    if (argc != 2) throw std::runtime_error("usage: qsim_reference fixture.txt");
    std::ifstream file(argv[1]);
    unsigned count, repetitions, warmups;
    if (!(file >> count >> repetitions >> warmups) || !count || !repetitions)
      throw std::runtime_error("invalid fixture header");
    ProductReference reference;
    std::cout << std::setprecision(17);
    for (unsigned case_id = 0; case_id < count; ++case_id) {
      Input input;
      file >> input.role >> input.block >> input.bias >> input.label;
      for (auto* values : {&input.x, &input.theta, &input.weights})
        for (auto& value : *values) file >> value;
      if (!file || input.role > 1 || input.block >= 250)
        throw std::runtime_error("invalid fixture record");
      Output output;
      std::vector<double> times;
      for (unsigned i = 0; i < repetitions+warmups; ++i) {
        const auto start = std::chrono::steady_clock::now();
        output = reference.forward(input);
        const auto end = std::chrono::steady_clock::now();
        if (i >= warmups)
          times.push_back(std::chrono::duration<double, std::milli>(end-start).count());
      }
      const auto gradient = reference.gradients(input);
      // Independent one-step SGD oracle for VQC only. This is a validation
      // calculation; the product agents and their learning remain in XI.
      const double error = output.probability-input.label;
      for (unsigned j = 0; j < 4; ++j) {
        const auto q = 4*input.block+j;
        input.theta[q] = std::clamp(input.theta[q]-.002*250.*error*gradient[j],
                                   -2.*std::acos(-1.), 2.*std::acos(-1.));
      }
      for (unsigned q = 0; q < 1000; ++q)
        input.weights[q] -= .3*error*output.z[q]/std::sqrt(1000.);
      input.bias -= .3*error;
      struct rusage usage {};
      getrusage(RUSAGE_SELF, &usage);
      // ru_maxrss can retain the pre-exec Python child's high-water mark.
      // Linux VmHWM measures this executable's current memory image instead.
      long vm_hwm_kib = 0;
      std::ifstream status("/proc/self/status");
      std::string status_line;
      while (std::getline(status, status_line))
        if (status_line.compare(0, 6, "VmHWM:") == 0)
          vm_hwm_kib = std::stol(status_line.substr(6));
      if (vm_hwm_kib <= 0) throw std::runtime_error("Linux VmHWM unavailable");
      std::cout << "{\"case\":" << case_id << ",\"native_ms\":";
      array_json(times);
      std::cout << ",\"observations\":"; array_json(output.z);
      std::cout << ",\"score\":" << output.score
                << ",\"probability\":" << output.probability
                << ",\"gradients\":"; array_json(gradient);
      std::cout << ",\"sgd_theta\":"; array_json(input.theta);
      std::cout << ",\"sgd_weights\":"; array_json(input.weights);
      std::cout << ",\"sgd_bias\":" << input.bias
                << ",\"peak_rss_kib\":" << vm_hwm_kib
                << ",\"rusage_peak_rss_kib\":" << usage.ru_maxrss << "}\n";
    }
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
}
