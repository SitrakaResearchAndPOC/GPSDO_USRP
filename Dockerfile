FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c"]

# Installation dépendances
RUN apt-get update -o Acquire::Retries=5 && \
    apt-get install -y \
    -o Acquire::Retries=5 \
    --no-install-recommends \
    git \
    cmake \
    build-essential \
    libboost-all-dev \
    libusb-1.0-0-dev \
    python3-dev \
    python3-mako \
    python3-numpy \
    python3-requests \
    python3-setuptools \
    libfftw3-dev \
    libcomedi-dev \
    libgps-dev \
    libgmp-dev \
    swig \
    pkg-config \
    gedit \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /opt

# Clone UHD
RUN git clone https://github.com/EttusResearch/uhd.git


WORKDIR /opt/uhd


# Correction GPS GN -> GP
RUN wget https://raw.githubusercontent.com/SitrakaResearchAndPOC/GPSDO_USRP/refs/heads/main/patch_gpsdo.sh && \
bash patch_gpsdo.sh


# Compilation UHD
WORKDIR /opt/uhd/host

RUN mkdir -p build

WORKDIR /opt/uhd/host/build

RUN cmake ..

RUN make -j$(nproc --ignore=2)

RUN make install

RUN ldconfig


# Lien outil GPSDO
RUN ln -sf /usr/local/lib/uhd/utils/query_gpsdo_sensors \
    /usr/local/bin/query_gpsdo_sensors


# Téléchargement images UHD
RUN uhd_images_downloader


# Test GPSDO
# RUN query_gpsdo_sensors || true


CMD ["/bin/bash"]
