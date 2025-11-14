ARG BASE_IMAGE=ubuntu
FROM $BASE_IMAGE

# Installing_deps.sh script arguments
ARG SKIP_REDIS
ARG SKIP_TLSH
ARG SKIP_PGPDUMP
ARG SKIP_YARA
ARG SKIP_KVROCKS
ARG SKIP_GEN_CERT
ARG SKIP_DB_SETUP
ARG SKIP_LNX_PKG_INSTALL

Installing_deps.sh script env (arg to env mapping)
ENV SKIP_REDIS=$SKIP_REDIS
ENV SKIP_TLSH=$SKIP_TLSH
ENV SKIP_PGPDUMP=$SKIP_PGPDUMP
ENV SKIP_YARA=$SKIP_YARA
ENV SKIP_KVROCKS=$SKIP_KVROCKS
ENV SKIP_GEN_CERT=$SKIP_GEN_CERT
ENV SKIP_DB_SETUP=$SKIP_DB_SETUP
ENV SKIP_LNX_PKG_INSTALL=$SKIP_LNX_PKG_INSTALL

# AIL runtime env variables
ENV LANG C.UTF-8
ENV AIL_HOME /home/ail/ail-framework
ENV AIL_BIN ${AIL_HOME}/bin
ENV AIL_FLASK ${AIL_HOME}/var/www
ENV AIL_REDIS ${AIL_HOME}/redis/src
ENV AIL_ARDB ${AIL_HOME}/ardb/src
ENV AIL_VENV ${AIL_HOME}/AILENV

#ENV PATH ${AIL_VENV}/bin:${AIL_HOME}:${AIL_REDIS}:${AIL_ARDB}:${AIL_BIN}:${AIL_FLASK}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Build Dependencies
RUN apt-get update && \
    apt-get install -y \
    sudo \
    wget \
    git \
    python3-dev \
    g++ \
    cmake \
    automake \
    libtool \
    make \
    gcc \
    pkg-config \
    build-essential \
    autoconf \
    virtualenv \
    unzip \
    libsnappy-dev \
    libssl-dev \
    libfreetype6-dev \
    protobuf-compiler \
    libprotobuf-dev \
    libadns1-dev \
    libev-dev \
    libgmp-dev \
    libfuzzy-dev \
    libffi-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Runtime Dependencies
RUN apt-get update && \
    apt-get install -y \
    python3-pip \
    python3-tk \
    screen \
    python3-numpy \
    python3-opencv \
    libzbar0 \
    libadns1 \
    graphviz \
    p7zip-full && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Replacements of Comiles/Builds
RUN wget https://github.com/RocksLabs/kvrocks-fpm/releases/download/202502091/kvrocks_2.11.1-1_amd64.deb && \
    apt-get update && \
    apt-get install -y \
    pgpdump \
    tlsh-tools \
    yara \
    ./kvrocks_2.11.1-1_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create ail user
RUN useradd -m -s /bin/bash ail

# Create ail framework work directory
RUN mkdir -p /home/ail/ail-framework

# Change to ail work directory
WORKDIR /home/ail/ail-framework

# Copy AIL files
COPY bin configs doc files logs samples tests tools update var install_virtualenv.sh installing_deps.sh requirements.txt reset_AIL.sh ./

# Start AIL installers
RUN apt-get update && \
    chmod +x ./installing_deps.sh && \
    sed -i 's/^sudo *//' ./installing_deps.sh && \
    ./installing_deps.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Docker modified files
COPY other_installers/docker/update.cfg configs/update.cfg

COPY other_installers/docker/core.cfg configs/core.cfg

COPY other_installers/docker/kvrocks_6383.conf configs/6383.conf

COPY other_installers/docker/docker_start.sh /usr/local/sbin/

RUN chmod +x /usr/local/sbin/docker_start.sh

RUN chown -R ail:ail /home/ail/

# Change user
USER ail

ENTRYPOINT ["/bin/bash", "/usr/local/sbin/docker_start.sh"]