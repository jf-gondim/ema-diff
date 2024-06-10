# Get system number of threads
NUM_THREADS := $(shell nproc)

# Check if threads value cannot be determined
ifeq ($(NUM_THREADS),)
	NUM_THREADS := 1
endif

# Define the number of threads that Make can use
MAKEFLAGS := -j$(NUM_THREADS)

# Default command
.DEFAULT_GOAL := all

# Variables
BUILD_DIR := build
RUNDIR=	sscDif sscDif/ src/

all: clean install

clean:
	rm -fr build/ _skbuild/ *.egg-info/ dist/ *~
	@for j in ${RUNDIR}; do rm -rf $$j/*.pyc; rm -rf $$j/*~; done

install:
	python3 setup.py install --user
