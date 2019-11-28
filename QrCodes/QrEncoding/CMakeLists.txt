cmake_minimum_required(VERSION 3.15)
project(QrEncoding)

set(CMAKE_CXX_STANDARD 14)

find_package(OpenCV REQUIRED)
if(${OpenCV_FOUND})
    include_directories(${OpenCV_INCLUDE_DIRS})
    link_directories(${OpenCV_LIBRARY_DIRS})
else()
    message("Could not find OpenCV")
endif()

add_executable(Encode src/encode.cpp)
target_link_libraries(Encode ${OpenCV_LIBRARIES} qrencode)

link_directories(/home/garciafa/Documents/PROG/OPENSOURCE/QUIRC)
include_directories(/home/garciafa/Documents/PROG/OPENSOURCE/QUIRC/lib)
add_executable(Decode src/decode.cpp)
target_link_libraries(Decode ${OpenCV_LIBRARIES} qrencode quirc)