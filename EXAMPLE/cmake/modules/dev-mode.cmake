
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
	