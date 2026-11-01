cmake_minimum_required(VERSION 3.25)

project(
    HyprPeek
    VERSION 0.1.0
    DESCRIPTION "A fast visual window switcher for Hyprland"
    LANGUAGES CXX
)

option(HYPRPEEK_WARNINGS_AS_ERRORS "Treat warnings as errors" OFF)

include(CTest)
include(GNUInstallDirs)

# ------------------------------------------------------------------------------
# Project settings
# ------------------------------------------------------------------------------

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ------------------------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------------------------

find_package(Qt6 6.8 REQUIRED COMPONENTS
    Core
    Gui
    Qml
    Quick
)

qt_standard_project_setup(REQUIRES 6.8)

# ------------------------------------------------------------------------------
# Warnings
# ------------------------------------------------------------------------------

add_library(hyprpeek_warnings INTERFACE)

target_compile_options(hyprpeek_warnings
    INTERFACE
        $<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:
            -Wall
            -Wextra
            -Wpedantic
            -Wconversion
            -Wsign-conversion
            -Wshadow
        >
)

if(HYPRPEEK_WARNINGS_AS_ERRORS)
    target_compile_options(hyprpeek_warnings
        INTERFACE
            $<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:-Werror>
    )
endif()

# ------------------------------------------------------------------------------
# HyprPeek executable
# ------------------------------------------------------------------------------

qt_add_executable(hyprpeek
    src/main.cpp
)

target_compile_features(hyprpeek
    PRIVATE
        cxx_std_23
)

target_compile_definitions(hyprpeek
    PRIVATE
        HYPRPEEK_VERSION="${PROJECT_VERSION}"
)

set_target_properties(hyprpeek PROPERTIES
    CXX_EXTENSIONS OFF
)

target_link_libraries(hyprpeek
    PRIVATE
        hyprpeek_warnings
        Qt6::Core
        Qt6::Gui
        Qt6::Qml
        Qt6::Quick
)

qt_add_qml_module(hyprpeek
    URI HyprPeek
    VERSION 1.0
    QML_FILES
        qml/Main.qml
)

# ------------------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------------------

if(BUILD_TESTING)
    add_test(
        NAME smoke.qml_startup
        COMMAND hyprpeek --smoke-test
    )

    set_tests_properties(smoke.qml_startup PROPERTIES
        LABELS smoke
        TIMEOUT 10
        ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_QPA_PLATFORMTHEME="
    )
endif()

# ------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------

install(
    TARGETS hyprpeek
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
