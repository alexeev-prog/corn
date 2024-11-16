TEMPLATES = {
	"CMakeLists.txt": """cmake_minimum_required(VERSION {{cmake_version}})
include(cmake/modules/prelude.cmake)

project({{project_name}} LANGUAGES CXX)

include(cmake/modules/project-is-top-level.cmake)
include(cmake/modules/variables.cmake)

include_directories(include)

set(CMAKE_CXX_STANDARD {{cpp_standard}})
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic -O2")

file(GLOB_RECURSE SOURCES src/*.cpp)
add_executable(${PROJECT_NAME} ${SOURCES})

# ---- Developer mode ----

if(NOT {{project_name}}_DEVELOPER_MODE)
  return()
elseif(NOT PROJECT_IS_TOP_LEVEL)
  message(
      AUTHOR_WARNING
      "Developer mode is intended for developers of {{project_name}}"
  )
endif()

install(TARGETS ${PROJECT_NAME} DESTINATION bin)
install(DIRECTORY include/ DESTINATION include)
""",
	"README.md": """# {{project_name}}

## Build Instructions

To build this project, run:
```bash
mkdir build && cd build
cmake ..
make

""",
	"BUILDING.md": """# Building the Project

1. Ensure CMake is installed.
2. Navigate to the project directory.
3. Create a build directory and navigate into it:

   mkdir build && cd build

4. Run CMake to configure the project:

   cmake ..

5. Build the project:

   make

""",
	"main.cpp": """#include <iostream>

int main() {
	std::cout << "Hello, {{project_name}}!" << std::endl;
	return 0;
}
""",
	"my_library.hpp": """#pragma once

namespace {{project_name}} {{
	void do_something();
}}

""",
"CMakePresets.json": """{
    "version": 3,
    "cmakeMinimumRequired": {
        "major": 3,
        "minor": 10,
        "patch": 0
    },
    "configurePresets": [
        {
            "name": "default",
            "hidden": false,
            "generator": "Ninja"
        }
    ]
}
""",
    "CMakeUserPresets.json": """{
    "version": 3,
    "configurePresets": []
}
""",
    ".clang-format": """BasedOnStyle: Google
IndentWidth: 4
ColumnLimit: 120
""",
    ".clang-tidy": """Checks: '-*,clang-analyzer-*"
WarningsAsErrors: '*'
DiagnosticsFormat: 'clang'
""",
'build.sh': '''
#!/bin/bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project information
PROJECT_NAME="{{project_name}}"
BUILD_DIR="build"

# Functions
function print_header() {
	echo -e "${YELLOW}#######################################################################${NC}"
	echo -e "${YELLOW}### ${1}${NC}"
	echo -e "${YELLOW}#######################################################################${NC}"
}

function print_step() {
	currdate=$(date +"%Y-%m-%d %H:%M:%S")
	echo -e "${currdate} ${BLUE}[ * ] ${1}${NC}"
}

function print_debug() {
	currdate=$(date +"%Y-%m-%d %H:%M:%S")
	echo -e "${currdate} ${PURPLE}[ * ] ${1}${NC}"
}

function print_success() {
	currdate=$(date +"%Y-%m-%d %H:%M:%S")
	echo -e "${currdate} ${GREEN}[ ✓ ] ${1}${NC}"
}

function print_error() {
	currdate=$(date +"%Y-%m-%d %H:%M:%S")
	echo -e "${currdate} ${RED}[ ✗ ] ${1}${NC}"
}

currdate=$(date +"%Y-%m-%d %H:%M:%S")
clear
echo -e "{{project_name}} build @ ${currdate}\n"

if [ "$1" == "help" ]; then
	echo "Usage: build.sh <doxygen/format>"
	exit
elif [ "$1" == "doxygen" ]; then
	print_header "Generate docs with doxygem"
	print_step "Generating..."
	doxygen
	print_success "Docs generation complete."
elif [ "$1" == "format" ]; then
	print_header "Format code"
	print_step "Formatting..."
	python3 format-code.py
	print_success "Code formatting complete."
fi

print_header "Cleaning up previous build"
if [ -d "$BUILD_DIR" ]; then
	print_step "Removing $BUILD_DIR directory..."
	rm -rf "$BUILD_DIR"
	print_success "Removed $BUILD_DIR directory."
else
	print_success "No previous build found."
fi

if [ "$1" == "format" ]; then
	# Formatting code
	print_header "Formatting code"
	print_step "Format and cleaning code..."
	./format-code.py
	print_success "Code formatted."
fi

# Create build directory
print_header "Creating build directory"
print_step "Creating $BUILD_DIR directory..."
mkdir -p "$BUILD_DIR"
print_success "Created $BUILD_DIR directory."

# Configure the project
print_header "Configuring the project"
print_step "Running CMake in $BUILD_DIR..."
cd "$BUILD_DIR"

if [ "$1" == "BUILD_SHARED_LIBS" ]; then
	cmake .. -DBUILD_SHARED_LIBS=ON -D{{project_name}}_DEVELOPER_MODE=ON
else
	cmake .. -D{{project_name}}_DEVELOPER_MODE=ON
fi

if [ $? -eq 0 ]; then
	print_success "CMake configuration completed successfully."
else
	print_error "CMake configuration failed."
	exit 1
fi

# Build the project
print_header "Building the project"
print_step "Building the project in $BUILD_DIR..."
make
if [ $? -eq 0 ]; then
	print_success "Project build completed successfully."
else
	print_error "Project build failed."
	exit 1
fi

# Install the project
print_header "Installing the project"
print_step "Installing the project..."
sudo make install
if [ $? -eq 0 ]; then
	print_success "Project installation completed successfully."
else
	print_error "Project installation failed."
	exit 1
fi

print_header "Build completed successfully"
echo -e "${CYAN}The ${PROJECT_NAME} library has been built and installed.${NC}"
echo "Build dir: build/"
''',
'format-code.py': '''
#!/usr/bin/env python3
# Python program to format C/C++ files using clang-format 
import os
import sys
import subprocess

# Define color codes for output
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
NC = '\033[0m'  # No Color
BOLD = '\033[1m'  # No Color

# File Extension filter. You can add new extension 
cpp_extensions = (".cxx",".cpp",".c", ".hxx", ".hh", ".cc", ".hpp") 
IGNORED_DIRS = ['build', '.git', 'cmake', 'docs']

CLANG_FORMAT = 'clang-format'
SPACETABS = './space-tabs.sh'

print(f'libnumerixpp code-formatter: {CLANG_FORMAT}; Extensions: {" ".join(cpp_extensions)}')


def print_usage():
	"""Print the usage instructions."""
	print(f"{YELLOW}Usage: convert_tabs(file_path, tab_size, conversion_type){NC}")
	print(f"<conversion_type>: 'spaces' or 'tabs'")


def print_error(message):
	"""Print error messages."""
	print(f"{RED}Error: {message}{NC}")


def validate_positive_integer(value):
	"""Validate if the value is a positive integer."""
	try:
		int_value = int(value)
		if int_value < 1:
			raise ValueError
		return int_value
	except ValueError:
		print_error("Tab size must be a positive integer.")
		return None


def file_exists(file_path):
	"""Check if the file exists."""
	if not os.path.isfile(file_path):
		print_error(f"File not found: {file_path}")
		return False
	return True


def convert_tabs(file_path, tab_size, conversion_type):
	"""Convert tabs to spaces or spaces to tabs based on conversion type."""
	try:
		if conversion_type == "spaces":
			print(f"{BOLD}Converting tabs to spaces...{NC}")
			subprocess.run(["expand", "-t", str(tab_size), file_path], stdout=open(f"{file_path}.tmp", "w"))
		elif conversion_type == "tabs":
			print(f"{BOLD}Converting spaces to tabs...{NC}")
			subprocess.run(["unexpand", "-t", str(tab_size), file_path], stdout=open(f"{file_path}.tmp", "w"))
		else:
			print_error(f"Invalid conversion type: {conversion_type}. Use 'spaces' or 'tabs'.")
			return

		os.replace(f"{file_path}.tmp", file_path)
		print(f"{GREEN}Conversion completed successfully: {file_path}{NC}")
	except Exception as e:
		print_error(f"Conversion failed: {str(e)}")


def convert_file(file_path, tab_size, conversion_type):
	"""Main function to manage conversion."""
	tab_size = validate_positive_integer(tab_size)
	if tab_size is None:
		return
	
	if not file_exists(file_path):
		return

	convert_tabs(file_path, tab_size, conversion_type)
	

def main():
	# Set the current working directory for scanning c/c++ sources (including 
	# header files) and apply the clang formatting 
	# Please note "-style" is for standard style options 
	# and "-i" is in-place editing 

	if len(sys.argv) > 1:
		print(f"{BOLD}Format {sys.argv[1]}{NC}")
		os.system(f'codespell -w {sys.argv[1]}')
		os.system(f'clang-tidy --fix {sys.argv[1]}')
		os.system(f"{CLANG_FORMAT} -i -style=file {sys.argv[1]}")
		print(f"{GREEN}Formatting completed successfully: {sys.argv[1]}{NC}")
		convert_file(f'{sys.argv[1]}', "4", "tabs")
		return
	
	for root, dirs, files in os.walk(os.getcwd()):
		if len(set(root.split('/')).intersection(IGNORED_DIRS)) > 0:
			continue
		for file in files: 
			if file.endswith(cpp_extensions):
				print(f"{BOLD}Format {file}: {root}/{file}{NC}")
				os.system(f'codespell -w {root}/{file}')
				os.system(f'clang-tidy --fix {root}/{file}')
				os.system(f"{CLANG_FORMAT} -i -style=file {root}/{file}")
				print(f"{GREEN}Formatting completed successfully: {root}/{file}{NC}")
				convert_file(f'{root}/{file}', "4", "tabs")


if __name__ == '__main__':
	main()
''',
}