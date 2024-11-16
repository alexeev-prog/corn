
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
set(package EXAMPLE)

install(
    DIRECTORY
    include/
    "${PROJECT_BINARY_DIR}/export/"
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
    COMPONENT EXAMPLE_Development
)

install(
    TARGETS EXAMPLE_EXAMPLE
    EXPORT EXAMPLETargets
    RUNTIME #
    COMPONENT EXAMPLE_Runtime
    LIBRARY #
    COMPONENT EXAMPLE_Runtime
    NAMELINK_COMPONENT EXAMPLE_Development
    ARCHIVE #
    COMPONENT EXAMPLE_Development
    INCLUDES #
    DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)

write_basic_package_version_file(
    "${package}ConfigVersion.cmake"
    COMPATIBILITY SameMajorVersion
)

# Allow package maintainers to freely override the path for the configs
set(
    EXAMPLE_INSTALL_CMAKEDIR "${CMAKE_INSTALL_LIBDIR}/cmake/modules/${package}"
    CACHE STRING "CMake package config location relative to the install prefix"
)
set_property(CACHE EXAMPLE_INSTALL_CMAKEDIR PROPERTY TYPE PATH)
mark_as_advanced(EXAMPLE_INSTALL_CMAKEDIR)

install(
    FILES cmake/modules/install-config.cmake
    DESTINATION "${EXAMPLE_INSTALL_CMAKEDIR}"
    RENAME "${package}Config.cmake"
    COMPONENT EXAMPLE_Development
)

install(
    FILES "${PROJECT_BINARY_DIR}/${package}ConfigVersion.cmake"
    DESTINATION "${EXAMPLE_INSTALL_CMAKEDIR}"
    COMPONENT EXAMPLE_Development
)

install(
    EXPORT EXAMPLETargets
    NAMESPACE EXAMPLE::
    DESTINATION "${EXAMPLE_INSTALL_CMAKEDIR}"
    COMPONENT EXAMPLE_Development
)

if(PROJECT_IS_TOP_LEVEL)
  include(CPack)
endif()
	