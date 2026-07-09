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
RUN  ( grep -qF 'static const std::regex gp_msg_regex("^\\$G.*$");' host/lib/usrp/gps_ctrl.cpp ||   sed -i '/static const std::regex gp_msg_regex/{s|^|// |;a\
static const std::regex gp_msg_regex("^\\\\$G.*$");
}' host/lib/usrp/gps_ctrl.cpp ) && ( grep -qF 'if(msg.substr(1,2) == "GN"){ msg.replace(1, 2, "GP");}' host/lib/usrp/gps_ctrl.cpp ||   sed -i '/msgs\[msg\.substr(1, 5)\] = msg;/i\
        if(msg.substr(1,2) == "GN"){ msg.replace(1, 2, "GP");}
' host/lib/usrp/gps_ctrl.cpp )


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
