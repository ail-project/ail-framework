# Container Installation

Still unde development - mostly notes rather than comprehensive manual


## Build

Get the source

```
git clone -b dev https://github.com/rht-jbittner/ail-framework.git
cd ail-framework
git submodule update --init --recursive
```

Build primary container. In this example we disable most dependency builds as we do not need it in pure AIL container.
```
podman build -t ail\
    --build-arg "BASE_IMAGE=ubuntu:24.04" \
    --build-arg "http_proxy=$http_proxy" \
    --build-arg "https_proxy=$https_proxy" \
    --build-arg "no_proxy=$no_proxy" \
    --build-arg "SKIP_REDIS=1" \
    --build-arg "SKIP_PGPDUMP=1" \
    --build-arg "SKIP_YARA=1" \
    --build-arg "SKIP_KVROCKS=1" \
    --build-arg "SKIP_GEN_CERT=1" \
    --build-arg "SKIP_DB_SETUP=1" \
    --build-arg "SKIP_LNX_PKG_INSTALL=1" \
    --build-arg "SKIP_GIT_SUBMODULE=1" \
    -f other_installers/docker/Dockerfile .
```

Comment: skipping tlsh build (`--build-arg "SKIP_TLSH=1"`) is possible, but additional chages would need to be added to install_virtualenv.sh file. In this case it probably does not matter, but package python3-tlsh exists in Ubuntu.

## Start Container

Simple way to start AIL container. We disable redis and kvrock related stuff as we have it deployed separately (not covered in this document).
```
podman run --rm -p 7000:7000 --name ail \
  -e SKIP_LAUNCH_REDIS=true \
  -e SKIP_LAUNCH_KVROCKS=false \
  -e SKIP_CHECK_REDIS=true \
  -e SKIP_CHECK_KVROCKS=true \
  localhost/ail
```

## Create default user

podman exec -it ail /bin/bash -c ". ./AILENV/bin/activate && cd var/www && python3 ./create_default_user.py"
