#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools

class CapicxxCoreRuntimeConan(ConanFile):
    name = "capicxx-core-runtime"
    version = "3.2.0"
    license = "https://github.com/maingig/capicxx-core-runtime/blob/master/LICENSE"
    author = "https://github.com/maingig/capicxx-core-runtime/blob/master/AUTHORS"
    url = "https://github.com/maingig/capicxx-core-runtime.git"
    description = "CommonAPI C++ is a C++ framework for interprocess and network communication"
    topics = ("tcp", "C++", "networking")
    settings = "os", "compiler", "build_type", "arch"
    exports = "*"
    options = {
        "shared": [ True, False ],
        "fPIC": [ True, False ],
    }
    default_options = {
        'shared': True,
        'fPIC': True,
    }
    generators = "cmake_find_package"

    # Custom variables
    source_url = url
    source_branch = "master"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

    def source(self):
        self.run("git clone %s %s" % (self.source_url, self.name))
        self.run("cd %s && git checkout tags/%s" % (self.name, self.version))
        """Wrap the original CMake file to call conan_basic_setup
        """
        shutil.move("%s/CMakeLists.txt" % (self.name), "%s/CMakeListsOriginal.txt" % (self.name))
        f = open("%s/CMakeLists.txt" % (self.name), "w")
        f.write('cmake_minimum_required(VERSION 2.8)\n')
        f.write('set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CONAN_CXX_FLAGS}")\n')
        f.write('set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${CONAN_C_FLAGS}")\n')
        f.write('set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} ${CONAN_SHARED_LINKER_FLAGS}")\n')
        f.write('include(${CMAKE_SOURCE_DIR}/CMakeListsOriginal.txt)\n')
        f.close()

    def configure_cmake(self):
        cmake = CMake(self)
        if 'fPIC' in self.options and self.options.fPIC:
            cmake.definitions["CMAKE_C_FLAGS"] = "-fPIC"
            cmake.definitions["CMAKE_CXX_FLAGS"] = "-fPIC"
        if 'shared' in self.options:
            cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        if 'USE_FILE' in self.env and len(self.env['USE_FILE']) > 0:
            cmake.definitions["USE_FILE"] = self.env['USE_FILE']
        if 'USE_CONSOLE' in self.env and len(self.env['USE_CONSOLE']) > 0:
            cmake.definitions["USE_CONSOLE"] = self.env['USE_CONSOLE']
        cmake.configure(source_folder=self.name, build_folder=self.name)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.name)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.libs.extend(['winmm', 'ws2_32'])
        elif self.settings.os == "Linux":
            self.cpp_info.libs.extend(['pthread'])
        elif self.settings.os == "QNX":
            self.cpp_info.libs.extend(['socket'])
            self.cpp_info.defines.extend(["__EXT_BSD", "__QNXNTO__", "_QNX_SOURCE"])
