cmake_minimum_required(VERSION 3.14)
include(cmake/modules/prelude.cmake)

project(EXAMPLE LANGUAGES CXX)

include(cmake/modules/project-is-top-level.cmake)
include(cmake/modules/variables.cmake)

include_directories(include)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic -O2")

file(GLOB_RECURSE SOURCES src/*.cpp)
add_executable(${PROJECT_NAME} ${SOURCES})

# ---- Developer mode ----

if(NOT EXAMPLE_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of EXAMPLE"
  )
endif()

install(TARGETS ${PROJECT_NAME} DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)
