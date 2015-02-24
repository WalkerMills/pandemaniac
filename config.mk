# Default shell
SHELL = /bin/sh

# Default C compiler
CC = gcc

# Default C++ compiler
CXX = g++

# Default Cython compiler
CYTHON = cython

# SWIG interface generator
SWIG = swig

srcdir = .
libdir = lib

# Default compiler flags (for C and C++)
CFLAGS = -O3 -mtune=generic -pipe -fstack-protector --param=ssp-buffer-size=4 \
-Wno-sign-compare -Wno-unused-function

# Default compiler flags for C++
CXXFLAGS = -std=c++11 -Wno-write-strings 

# Default linker flags
LD_FLAGS = -L$(libdir) -Wl,-O1,--sort-common,--as-needed,-z,relro \
-Wl,-rpath,$(realpath $(libdir))

# Compiler flags for compiling with Cython
CYTHON_CFLAGS = -I/usr/include/python3.4m -Wno-strict-aliasing
# Linker flags for linking object files compiled from Cython-generated code
CYTHON_LDFLAGS = -lpython3.4m

# All C compiler flaga for normal compilation
ALL_CFLAGS = -Wall -fPIC $(CFLAGS)

# All C++ compiler flags required for normal compilation
ALL_CXXFLAGS = $(ALL_CFLAGS) $(CXXFLAGS)

# Default Cython flags
CYTHON_FLAGS = --cplus -3

