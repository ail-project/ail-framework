#!/bin/bash

# halt on errors
set -e

## bash debug mode toggle below
#set -x

sudo apt-get update

packages="python3-pip virtualenv python3-dev python3-tk libfreetype6-dev screen g++ unzip libsnappy-dev cmake automake libtool make gcc pkg-config"

#Needed for downloading jemalloc
packages="${packages} wget"

#Needed for bloom filters
packages="${packages} libssl-dev libfreetype6-dev python3-numpy"

# pycld3
packages="${packages} protobuf-compiler libprotobuf-dev"

# qrcode
packages="${packages} python3-opencv libzbar0"

# DNS deps
packages="${packages} libadns1 libadns1-dev"

#Needed for redis-lvlDB
packages="${packages} libev-dev libgmp-dev" # TODO NEED REVIEW

#Need for generate-data-flow graph
packages="${packages} graphviz"

# ssdeep
packages="${packages} libfuzzy-dev build-essential libffi-dev autoconf"

# sflock, gz requirement
packages="${packages} p7zip-full" # TODO REMOVE ME

# resolve needed packages & install all at once while keeping history of why some packages are needed.
sudo apt-get install --assume-yes ${packages}

# SUBMODULES #
git submodule update --init --recursive

# REDIS #
test ! -d redis/ && git clone https://github.com/redis/redis.git
pushd redis/
git checkout 5.0
make -j
popd

# tlsh
test ! -d tlsh && git clone https://github.com/trendmicro/tlsh.git
pushd tlsh/
./make.sh
pushd build/release/
sudo make install
sudo ldconfig
popd
popd

# pgpdump
test ! -d pgpdump && git clone https://github.com/kazu-yamamoto/pgpdump.git
pushd pgpdump/
autoreconf -fiW all
./configure
make -j
sudo make install
popd

# Yara
YARA_VERSION="4.3.0"
mkdir yara_temp
wget https://github.com/VirusTotal/yara/archive/v${YARA_VERSION}.zip -O yara_temp/yara.zip
unzip yara_temp/yara.zip -d yara_temp/
pushd yara_temp/yara-${YARA_VERSION}
./bootstrap.sh
./configure
make -j
sudo make install
make check
popd
rm -rf yara_temp


# ARDB #
#test ! -d ardb/ && git clone https://github.com/ail-project/ardb.git
#pushd ardb/
#make
#popd

DEFAULT_HOME=$(pwd)

#### KVROCKS ####
# If we are on debian, we can get the kvrocks deb package:
#   download the right version from https://github.com/RocksLabs/kvrocks-fpm/releases
#   then sudo dpkg -i kvrocks_2.11.1-1_amd64.deb   (change the version number to yours)

test ! -d kvrocks/ && git clone https://github.com/apache/incubator-kvrocks.git kvrocks
pushd kvrocks
# Build Kvrocks in portable mode
#export PORTABLE=1
./x.py build -j 4
popd

DEFAULT_KVROCKS_DATA=$DEFAULT_HOME/DATA_KVROCKS
mkdir -p $DEFAULT_KVROCKS_DATA

sed -i "s|dir /tmp/kvrocks|dir ${DEFAULT_KVROCKS_DATA}|1" $DEFAULT_HOME/configs/6383.conf
##-- KVROCKS --##



# Config File
if [ ! -f configs/core.cfg ]; then
    cp configs/core.cfg.sample configs/core.cfg
fi

# create AILENV + install python packages
./install_virtualenv.sh

# force virtualenv activation
if [ -z "$VIRTUAL_ENV" ]; then
    . ./AILENV/bin/activate
fi

pushd ${AIL_HOME}/tools/gen_cert
./gen_root.sh
wait
./gen_cert.sh
wait
popd

cp ${AIL_HOME}/tools/gen_cert/server.crt ${AIL_FLASK}/server.crt
cp ${AIL_HOME}/tools/gen_cert/server.key ${AIL_FLASK}/server.key

mkdir -p $AIL_HOME/PASTES

#### DB SETUP ####

# init update version
pushd ${AIL_HOME}
# shallow clone
git fetch --depth=500 --tags --prune
if [ ! -z "$TRAVIS" ]; then
    echo "Travis detected"
    git fetch --unshallow
fi
git describe --abbrev=0 --tags | tr -d '\n' > ${AIL_HOME}/update/current_version
echo "AIL current version:"
git describe --abbrev=0 --tags
popd

# LAUNCH Kvrocks
bash ${AIL_BIN}/LAUNCH.sh -lkv &
wait
echo ""

# create default user
pushd ${AIL_FLASK}
python3 create_default_user.py
popd

bash ${AIL_BIN}/LAUNCH.sh -k &
wait
echo ""
