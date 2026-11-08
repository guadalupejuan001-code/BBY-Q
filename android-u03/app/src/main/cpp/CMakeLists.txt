cmake_minimum_required(VERSION 3.22.1)
project(BBYQU03 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../../../../../" ABSOLUTE)
set(REVERSE "${ROOT}/deps/reverse-pc")
set(MUNDO "${ROOT}/deps/mundo-x")
set(PATCH "${ROOT}/build/ether-compat")
add_library(reverse_os SHARED
  "${REVERSE}/reverse-os-android/app/src/main/cpp/reverse_os_jni.cpp"
  "${ROOT}/android-personal/app/src/main/cpp/personal_session.cpp")
target_include_directories(reverse_os PRIVATE "${PATCH}" "${MUNDO}/native/include"
  "${REVERSE}/src" "${REVERSE}/reverse-os-android/app/src/main/cpp")
target_compile_options(reverse_os PRIVATE -O2 -fexceptions -frtti)
target_compile_definitions(reverse_os PRIVATE REVERSE_PC_HAVE_BOUNDED_PRODUCT_IMPORT=1)
find_library(LOG_LIB log)
target_link_libraries(reverse_os PRIVATE "${LOG_LIB}")
