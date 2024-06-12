# Base Image: Start with the official Ubuntu 20.04 image
FROM ubuntu:20.04

# Environment Variables
# Set locale for consistent text encoding (UTF-8)
ENV LC_ALL=C.UTF-8
# Disable interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package lists and install core dependencies
RUN apt update && \
    apt install -y software-properties-common curl libcurl4-openssl-dev build-essential \
    libhdf5-openmpi-dev libhdf5-dev libopenmpi-dev libomp-dev libblas-dev liblapack-dev pkg-config python3-numpy-dev doxygen git vim && \
    rm -rf /var/lib/apt/lists/*    # Clean up package cache to reduce image size

# Add Deadsnakes PPA for additional Python versions
RUN apt-add-repository ppa:deadsnakes/ppa

# Install multiple Python versions, pip, and venv
RUN apt update && \
    apt install -y python3.8-dev \
    python3-pip python3-venv &&\
    rm -rf /var/lib/apt/lists/*    # Clean up package cache

# Create symlink for HDF5 library (needed for some scientific libraries)
RUN ln -sf /usr/lib/x86_64-linux-gnu/hdf5/serial/libhdf5.so /usr/lib/libhdf5.so

# Download get-pip.py script (to install or upgrade pip)
RUN curl -Ss -O https://bootstrap.pypa.io/get-pip.py

# Install/upgrade pip using Python 3.8
RUN python3.8 get-pip.py

# Install Python build tools and common scientific packages
RUN python3.8 -m pip install build scikit-build cython pybind11 wheel numpy setuptools cmake pkgconfig

# Set Python 3.8 as default Python and Python3
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 3

# Install tools for packaging (twine) and documentation (Sphinx, Breathe)
RUN python3 -m pip install twine sphinx sphinx-rtd-theme breathe
