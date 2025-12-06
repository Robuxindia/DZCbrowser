cmake_minimum_required(VERSION 3.20)
project(DZCbrowser)

set(CMAKE_CXX_STANDARD 17)

# CEF include
include_directories("include")
link_directories("lib")

# Proje dosyaları
add_executable(DZCbrowser main.cpp)

# CEF kütüphanelerini bağla
target_link_libraries(DZCbrowser libcef.lib libcef_dll_wrapper.lib)
