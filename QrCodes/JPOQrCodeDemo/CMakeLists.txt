cmake_minimum_required(VERSION 3.0)
project(JPOQrCodeDemo)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)
if(${OpenCV_FOUND})
    include_directories(${OpenCV_INCLUDE_DIRS})
    link_directories(${OpenCV_LIBRARY_DIRS})
else()
    message("Could not find OpenCV")
endif()

set (SOURCE_FILES
        src/main.cpp)

link_directories(../QUIRC)
include_directories(../QUIRC/lib)

add_executable(JPOQrCodeDemo ${SOURCE_FILES})
target_link_libraries(JPOQrCodeDemo ${OpenCV_LIBRARIES} quirc)
