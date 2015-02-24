include config.mk

# Object file names (targets)
OBJS = interface.o

# Dynamic library names (targets)
LIBS = interface.so

# Generated file names (targets)
GEN = interface.cpp

vpath %.o $(libdir)

# Absolute file paths for object files
OBJ_FILES = $(foreach obj, $(OBJS), $(libdir)/$(obj))

# Clear allowed target suffixes
.SUFFIXES:

# Set allowed target suffixes
.SUFFIXES: .cpp .hpp .o .so

# Declare all phony targets
.PHONY: all clean mklib

# All (final) targets
all: $(LIBS)

# Clean up all files
clean:
	@# Remove all make-generated files
	rm -f $(OBJ_FILES) $(LIBS) $(GEN)
	@# Remove Python bytecode
	rm -rf $(srcdir)/__pycache__
	@# If libdir is empty, remove it
	if [[ -d $(libdir) && -z "`ls -A $(libdir)`" ]]; then \
	    rm -rf $(libdir); \
	fi

# Create directory for containing object files and libraries
mklib:
	@# Make libdir if it doesn't already exist
	test -d $(libdir) || mkdir $(libdir)

# Generate a C++ file from a Cython file
%.cpp: %.pyx mklib
	$(CYTHON) $(CYTHON_FLAGS) --cplus $(srcdir)/$< -o $(srcdir)/$@

interface.o: private ALL_CFLAGS += $(CYTHON_CFLAGS)

# Implicit rule to generate object files
%.o: %.cpp mklib 
	$(CXX) $(ALL_CXXFLAGS) -c $< -o $(libdir)/$@

# Implicit rule matching the C/C++ dynamic library naming convention
lib%.so: %.o
	$(CXX) $(LD_FLAGS) -shared -Wl,-soname,$@ $(libdir)/$< -o $(libdir)/$@ \
	$(EXTRA_LDFLAGS)

interface.so: private EXTRA_LDFLAGS := $(CYTHON_LDFLAGS)

# Any shared object not matching the C/C++ library naming convention is
# assumed to be a Cython extension; shared objects must match the name of the
# Cython interfaces to avoid runtime errors
%.so: %.o
	$(CXX) $(LD_FLAGS) -shared -Wl,-soname,$@ \
	$(foreach dep, $^, $(libdir)/$(dep)) -o $@ $(EXTRA_LDFLAGS)