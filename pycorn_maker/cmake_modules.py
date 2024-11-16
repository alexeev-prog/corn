CMAKE_MODULES = {
	'coverage.cmake': '''
# ---- Variables ----

# We use variables separate from what CTest uses, because those have
# customization issues
set(
    COVERAGE_TRACE_COMMAND
    lcov -c -q
    -o "${PROJECT_BINARY_DIR}/coverage.info"
    -d "${PROJECT_BINARY_DIR}"
    --include "${PROJECT_SOURCE_DIR}/*"
    CACHE STRING
    "; separated command to generate a trace for the 'coverage' target"
)

set(
    COVERAGE_HTML_COMMAND
    genhtml --legend -f -q
    "${PROJECT_BINARY_DIR}/coverage.info"
    -p "${PROJECT_SOURCE_DIR}"
    -o "${PROJECT_BINARY_DIR}/coverage_html"
    CACHE STRING
    "; separated command to generate an HTML report for the 'coverage' target"
)

# ---- Coverage target ----

add_custom_target(
    coverage
    COMMAND ${COVERAGE_TRACE_COMMAND}
    COMMAND ${COVERAGE_HTML_COMMAND}
    COMMENT "Generating coverage report"
    VERBATIM
)
	''',
	'dev-mode.cmake': '''
include(cmake/modules/folders.cmake)

include(CTest)
if(BUILD_TESTING)
  add_subdirectory(test)
endif()

option(BUILD_MCSS_DOCS "Build documentation using Doxygen and m.css" OFF)
if(BUILD_MCSS_DOCS)
  include(cmake/modules/docs.cmake)
endif()

option(ENABLE_COVERAGE "Enable coverage support separate from CTest's" OFF)
if(ENABLE_COVERAGE)
  include(cmake/modules/coverage.cmake)
endif()

include(cmake/modules/lint-targets.cmake)
include(cmake/modules/spell-targets.cmake)

add_folders(Project)	                  
	''',
	'docs.cmake': '''
# ---- Dependencies ----

set(extract_timestamps "")
if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.24")
  set(extract_timestamps DOWNLOAD_EXTRACT_TIMESTAMP YES)
endif()

include(FetchContent)
FetchContent_Declare(
    mcss URL
    https://github.com/friendlyanon/m.css/releases/download/release-1/mcss.zip
    URL_MD5 00cd2757ebafb9bcba7f5d399b3bec7f
    SOURCE_DIR "${PROJECT_BINARY_DIR}/mcss"
    UPDATE_DISCONNECTED YES
    ${extract_timestamps}
)
FetchContent_MakeAvailable(mcss)

find_package(Python3 3.6 REQUIRED)

# ---- Declare documentation target ----

set(
    DOXYGEN_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/docs"
    CACHE PATH "Path for the generated Doxygen documentation"
)

set(working_dir "${PROJECT_BINARY_DIR}/docs")

foreach(file IN ITEMS Doxyfile conf.py)
  configure_file("docs/${file}.in" "${working_dir}/${file}" @ONLY)
endforeach()

set(mcss_script "${mcss_SOURCE_DIR}/documentation/doxygen.py")
set(config "${working_dir}/conf.py")

add_custom_target(
    docs
    COMMAND "${CMAKE_COMMAND}" -E remove_directory
    "${DOXYGEN_OUTPUT_DIRECTORY}/html"
    "${DOXYGEN_OUTPUT_DIRECTORY}/xml"
    COMMAND "${Python3_EXECUTABLE}" "${mcss_script}" "${config}"
    COMMENT "Building documentation using Doxygen and m.css"
    WORKING_DIRECTORY "${working_dir}"
    VERBATIM
)
	''',
	'docs-ci.cmake': '''
cmake_minimum_required(VERSION 3.14)

foreach(var IN ITEMS PROJECT_BINARY_DIR PROJECT_SOURCE_DIR)
  if(NOT DEFINED "${var}")
    message(FATAL_ERROR "${var} must be defined")
  endif()
endforeach()
set(bin "${PROJECT_BINARY_DIR}")
set(src "${PROJECT_SOURCE_DIR}")

# ---- Dependencies ----

set(mcss_SOURCE_DIR "${bin}/docs/.ci")
if(NOT IS_DIRECTORY "${mcss_SOURCE_DIR}")
  file(MAKE_DIRECTORY "${mcss_SOURCE_DIR}")
  file(
      DOWNLOAD
      https://github.com/friendlyanon/m.css/releases/download/release-1/mcss.zip
      "${mcss_SOURCE_DIR}/mcss.zip"
      STATUS status
      EXPECTED_MD5 00cd2757ebafb9bcba7f5d399b3bec7f
  )
  if(NOT status MATCHES "^0;")
    message(FATAL_ERROR "Download failed with ${status}")
  endif()
  execute_process(
      COMMAND "${CMAKE_COMMAND}" -E tar xf mcss.zip
      WORKING_DIRECTORY "${mcss_SOURCE_DIR}"
      RESULT_VARIABLE result
  )
  if(NOT result EQUAL "0")
    message(FATAL_ERROR "Extraction failed with ${result}")
  endif()
  file(REMOVE "${mcss_SOURCE_DIR}/mcss.zip")
endif()

find_program(Python3_EXECUTABLE NAMES python3 python)
if(NOT Python3_EXECUTABLE)
  message(FATAL_ERROR "Python executable was not found")
endif()

# ---- Process project() call in CMakeLists.txt ----

file(READ "${src}/CMakeLists.txt" content)

string(FIND "${content}" "project(" index)
if(index EQUAL "-1")
  message(FATAL_ERROR "Could not find \"project(\"")
endif()
string(SUBSTRING "${content}" "${index}" -1 content)

string(FIND "${content}" "\n)\n" index)
if(index EQUAL "-1")
  message(FATAL_ERROR "Could not find \"\\n)\\n\"")
endif()
string(SUBSTRING "${content}" 0 "${index}" content)

file(WRITE "${bin}/docs-ci.project.cmake" "docs_${content}\n)\n")

macro(list_pop_front list out)
  list(GET "${list}" 0 "${out}")
  list(REMOVE_AT "${list}" 0)
endmacro()

function(docs_project name)
  cmake_parse_arguments(PARSE_ARGV 1 "" "" "VERSION;DESCRIPTION;HOMEPAGE_URL" LANGUAGES)
  set(PROJECT_NAME "${name}" PARENT_SCOPE)
  if(DEFINED _VERSION)
    set(PROJECT_VERSION "${_VERSION}" PARENT_SCOPE)
    string(REGEX MATCH "^[0-9]+(\\.[0-9]+)*" versions "${_VERSION}")
    string(REPLACE . ";" versions "${versions}")
    set(suffixes MAJOR MINOR PATCH TWEAK)
    while(NOT versions STREQUAL "" AND NOT suffixes STREQUAL "")
      list_pop_front(versions version)
      list_pop_front(suffixes suffix)
      set("PROJECT_VERSION_${suffix}" "${version}" PARENT_SCOPE)
    endwhile()
  endif()
  if(DEFINED _DESCRIPTION)
    set(PROJECT_DESCRIPTION "${_DESCRIPTION}" PARENT_SCOPE)
  endif()
  if(DEFINED _HOMEPAGE_URL)
    set(PROJECT_HOMEPAGE_URL "${_HOMEPAGE_URL}" PARENT_SCOPE)
  endif()
endfunction()

include("${bin}/docs-ci.project.cmake")

# ---- Generate docs ----

if(NOT DEFINED DOXYGEN_OUTPUT_DIRECTORY)
  set(DOXYGEN_OUTPUT_DIRECTORY "${bin}/docs")
endif()
set(out "${DOXYGEN_OUTPUT_DIRECTORY}")

foreach(file IN ITEMS Doxyfile conf.py)
  configure_file("${src}/docs/${file}.in" "${bin}/docs/${file}" @ONLY)
endforeach()

set(mcss_script "${mcss_SOURCE_DIR}/documentation/doxygen.py")
set(config "${bin}/docs/conf.py")

file(REMOVE_RECURSE "${out}/html" "${out}/xml")

execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${mcss_script}" "${config}"
    WORKING_DIRECTORY "${bin}/docs"
    RESULT_VARIABLE result
)
if(NOT result EQUAL "0")
  message(FATAL_ERROR "m.css returned with ${result}")
endif()
	''',
	'folders.cmake': '''
set_property(GLOBAL PROPERTY USE_FOLDERS YES)

# Call this function at the end of a directory scope to assign a folder to
# targets created in that directory. Utility targets will be assigned to the
# UtilityTargets folder, otherwise to the ${name}Targets folder. If a target
# already has a folder assigned, then that target will be skipped.
function(add_folders name)
  get_property(targets DIRECTORY PROPERTY BUILDSYSTEM_TARGETS)
  foreach(target IN LISTS targets)
    get_property(folder TARGET "${target}" PROPERTY FOLDER)
    if(DEFINED folder)
      continue()
    endif()
    set(folder Utility)
    get_property(type TARGET "${target}" PROPERTY TYPE)
    if(NOT type STREQUAL "UTILITY")
      set(folder "${name}")
    endif()
    set_property(TARGET "${target}" PROPERTY FOLDER "${folder}Targets")
  endforeach()
endfunction()                 
	''',
	'install-config.cmake': '''
include(CMakeFindDependencyMacro)
find_dependency(fmt)
	''',
	'install-rules.cmake': '''
if(PROJECT_IS_TOP_LEVEL)
  set(
      CMAKE_INSTALL_INCLUDEDIR "include"
      CACHE STRING ""
  )
  set_property(CACHE CMAKE_INSTALL_INCLUDEDIR PROPERTY TYPE PATH)
endif()

include(CMakePackageConfigHelpers)
include(GNUInstallDirs)

# find_package(<package>) call for consumers to find this project
set(package {{project_name}})

install(
    DIRECTORY
    include/
    "${PROJECT_BINARY_DIR}/export/"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    COMPONENT {{project_name}}_Development
)

install(
    TARGETS {{project_name}}_{{project_name}}
    EXPORT {{project_name}}Targets
    RUNTIME #
    COMPONENT {{project_name}}_Runtime
    LIBRARY #
    COMPONENT {{project_name}}_Runtime
    NAMELINK_COMPONENT {{project_name}}_Development
    ARCHIVE #
    COMPONENT {{project_name}}_Development
    INCLUDES #
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)

write_basic_package_version_file(
    "${package}ConfigVersion.cmake"
    COMPATIBILITY SameMajorVersion
)

# Allow package maintainers to freely override the path for the configs
set(
    {{project_name}}_INSTALL_CMAKEDIR "${CMAKE_INSTALL_LIBDIR}/cmake/modules/${package}"
    CACHE STRING "CMake package config location relative to the install prefix"
)
set_property(CACHE {{project_name}}_INSTALL_CMAKEDIR PROPERTY TYPE PATH)
mark_as_advanced({{project_name}}_INSTALL_CMAKEDIR)

install(
    FILES cmake/modules/install-config.cmake
    DESTINATION "${{{project_name}}_INSTALL_CMAKEDIR}"
    RENAME "${package}Config.cmake"
    COMPONENT {{project_name}}_Development
)

install(
    FILES "${PROJECT_BINARY_DIR}/${package}ConfigVersion.cmake"
    DESTINATION "${{{project_name}}_INSTALL_CMAKEDIR}"
    COMPONENT {{project_name}}_Development
)

install(
    EXPORT {{project_name}}Targets
    NAMESPACE {{project_name}}::
    DESTINATION "${{{project_name}}_INSTALL_CMAKEDIR}"
    COMPONENT {{project_name}}_Development
)

if(PROJECT_IS_TOP_LEVEL)
  include(CPack)
endif()
	''',
	'link.cmake': '''
cmake_minimum_required(VERSION 3.14)

macro(default name)
  if(NOT DEFINED "${name}")
    set("${name}" "${ARGN}")
  endif()
endmacro()

default(FORMAT_COMMAND clang-format)
default(
    PATTERNS
    source/*.cpp source/*.hpp
    include/*.hpp
    test/*.cpp test/*.hpp
)
default(FIX NO)

set(flag --output-replacements-xml)
set(args OUTPUT_VARIABLE output)
if(FIX)
  set(flag -i)
  set(args "")
endif()

file(GLOB_RECURSE files ${PATTERNS})
set(badly_formatted "")
set(output "")
string(LENGTH "${CMAKE_SOURCE_DIR}/" path_prefix_length)

foreach(file IN LISTS files)
  execute_process(
      COMMAND "${FORMAT_COMMAND}" --style=file "${flag}" "${file}"
      WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
      RESULT_VARIABLE result
      ${args}
  )
  if(NOT result EQUAL "0")
    message(FATAL_ERROR "'${file}': formatter returned with ${result}")
  endif()
  if(NOT FIX AND output MATCHES "\n<replacement offset")
    string(SUBSTRING "${file}" "${path_prefix_length}" -1 relative_file)
    list(APPEND badly_formatted "${relative_file}")
  endif()
  set(output "")
endforeach()

if(NOT badly_formatted STREQUAL "")
  list(JOIN badly_formatted "\n" bad_list)
  message("The following files are badly formatted:\n\n${bad_list}\n")
  message(FATAL_ERROR "Run again with FIX=YES to fix these files.")
endif()
	''',
	'lint-targets.cmake': '''
set(
    FORMAT_PATTERNS
    source/*.cpp source/*.hpp
    include/*.hpp
    test/*.cpp test/*.hpp
    CACHE STRING
    "; separated patterns relative to the project source dir to format"
)

set(FORMAT_COMMAND clang-format CACHE STRING "Formatter to use")

add_custom_target(
    format-check
    COMMAND "${CMAKE_COMMAND}"
    -D "FORMAT_COMMAND=${FORMAT_COMMAND}"
    -D "PATTERNS=${FORMAT_PATTERNS}"
    -P "${PROJECT_SOURCE_DIR}/cmake/modules/lint.cmake"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    COMMENT "Linting the code"
    VERBATIM
)

add_custom_target(
    format-fix
    COMMAND "${CMAKE_COMMAND}"
    -D "FORMAT_COMMAND=${FORMAT_COMMAND}"
    -D "PATTERNS=${FORMAT_PATTERNS}"
    -D FIX=YES
    -P "${PROJECT_SOURCE_DIR}/cmake/modules/lint.cmake"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    COMMENT "Fixing the code"
    VERBATIM
)
	''',
	'prelude.cmake': '''
# ---- In-source guard ----

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(
      FATAL_ERROR
      "In-source builds are not supported. "
      "Please read the BUILDING document before trying to build this project. "
      "You may need to delete 'CMakeCache.txt' and 'CMakeFiles/' first."
  )
endif()
	''',
	'project-is-top-level.cmake': '''
# This variable is set by project() in CMake 3.21+
string(
    COMPARE EQUAL
    "${CMAKE_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}"
    PROJECT_IS_TOP_LEVEL
)                            
	''',
	'spell.cmake': '''
cmake_minimum_required(VERSION 3.14)

macro(default name)
  if(NOT DEFINED "${name}")
    set("${name}" "${ARGN}")
  endif()
endmacro()

default(SPELL_COMMAND codespell)
default(FIX NO)

set(flag "")
if(FIX)
  set(flag -w)
endif()

execute_process(
    COMMAND "${SPELL_COMMAND}" ${flag}
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    RESULT_VARIABLE result
)

if(result EQUAL "65")
  message(FATAL_ERROR "Run again with FIX=YES to fix these errors.")
elseif(result EQUAL "64")
  message(FATAL_ERROR "Spell checker printed the usage info. Bad arguments?")
elseif(NOT result EQUAL "0")
  message(FATAL_ERROR "Spell checker returned with ${result}")
endif()
	''',
	'spell-targets.cmake': '''
set(SPELL_COMMAND codespell CACHE STRING "Spell checker to use")

add_custom_target(
    spell-check
    COMMAND "${CMAKE_COMMAND}"
    -D "SPELL_COMMAND=${SPELL_COMMAND}"
    -P "${PROJECT_SOURCE_DIR}/cmake/modules/spell.cmake"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    COMMENT "Checking spelling"
    VERBATIM
)

add_custom_target(
    spell-fix
    COMMAND "${CMAKE_COMMAND}"
    -D "SPELL_COMMAND=${SPELL_COMMAND}"
    -D FIX=YES
    -P "${PROJECT_SOURCE_DIR}/cmake/modules/spell.cmake"
    WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    COMMENT "Fixing spelling errors"
    VERBATIM
)
	''',
	'variables.cmake': '''
# ---- Developer mode ----

# Developer mode enables targets and code paths in the CMake scripts that are
# only relevant for the developer(s) of {{project_name}}
# Targets necessary to build the project must be provided unconditionally, so
# consumers can trivially build and package the project
if(PROJECT_IS_TOP_LEVEL)
  option({{project_name}}_DEVELOPER_MODE "Enable developer mode" OFF)
  option(BUILD_SHARED_LIBS "Build shared libs." OFF)
endif()

# ---- Suppress C4251 on Windows ----

# Please see include/{{project_name}}/{{project_name}}.hpp for more details
set(pragma_suppress_c4251 "
/* This needs to suppress only for MSVC */
#if defined(_MSC_VER) && !defined(__ICL)
#  define LIBNUMERIXPP_SUPPRESS_C4251 _Pragma(\"warning(suppress:4251)\")
#else
#  define LIBNUMERIXPP_SUPPRESS_C4251
#endif
")

# ---- Warning guard ----

# target_include_directories with the SYSTEM modifier will request the compiler
# to omit warnings from the provided paths, if the compiler supports that
# This is to provide a user experience similar to find_package when
# add_subdirectory or FetchContent is used to consume this project
set(warning_guard "")
if(NOT PROJECT_IS_TOP_LEVEL)
  option(
      {{project_name}}_INCLUDES_WITH_SYSTEM
      "Use SYSTEM modifier for {{project_name}}'s includes, disabling warnings"
      ON
  )
  mark_as_advanced({{project_name}}_INCLUDES_WITH_SYSTEM)
  if({{project_name}}_INCLUDES_WITH_SYSTEM)
    set(warning_guard SYSTEM)
  endif()
endif()	                   
'''
}
