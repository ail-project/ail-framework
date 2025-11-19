# AIL Framework Docker Installation

This document provides instructions on how to build and run the AIL framework using Docker or Podman with `docker-compose` or `podman-compose`.

The provided setup is designed to run AIL in a multi-container environment, with separate containers for the AIL application, Valkey instances for caching and queues, and a Kvrocks instance for persistent storage.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) or [Podman](https://podman.io/getting-started/installation)
- `docker-compose` or `podman-compose`

## Build the AIL Container Image

First, clone the AIL framework repository and initialize the submodules:

```bash
git clone https://github.com/ail-project/ail-framework.git
cd ail-framework
git submodule update --init --recursive
```

Next, build the AIL container image using the provided `Dockerfile`. The following command builds an image named `localhost/ail`, which is the default image used in the `docker-compose.yml` file.

```bash
podman build -t localhost/ail \
    --build-arg "BASE_IMAGE=ubuntu:24.04" \
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

**Note on Build Arguments:** The `SKIP_*` build arguments are used to disable the installation of dependencies that are provided by other containers in the compose setup (like Redis/Valkey and Kvrocks). This keeps the AIL container image smaller and more focused on the application itself.

## Running the AIL Framework

The recommended way to run the AIL framework is by using `podman-compose` (or `docker-compose`) with the provided `docker-compose.yml` file.

### 1. Launch the Services

Navigate to the `other_installers/docker` directory and start all the services in the background:

```bash
cd other_installers/docker
podman-compose up -d
```

This will start the following services:
- `ail`: The main AIL application container.
- `kvrocks`: The Kvrocks database for persistent storage.
- `cache`, `log`, `log-submit`, `queues`, `process`, `mixer-cache`: Six separate Valkey instances for various caching and queuing purposes.

### 2. Create a Default User

After the containers have started, you need to create an initial user to log in to the web interface.

```bash
podman exec -it ail /bin/bash -c ". ./AILENV/bin/activate && cd var/www && python3 ./create_default_user.py"
```

Follow the prompts to create the user.

### 3. Accessing AIL

The AIL web interface will be available at `https://localhost:7000/`.

### Managing the Services

- **View Logs**: To view the logs of all running services, use:
  ```bash
  podman-compose logs -f
  ```
  To view the logs of a specific service (e.g., `ail`):
  ```bash
  podman-compose logs -f ail
  ```

- **Stop Services**: To stop and remove the containers, networks, and volumes, use:
  ```bash
  podman-compose down
  ```

### Using Custom Images

You can override the default Valkey and Kvrocks images by setting environment variables before running `podman-compose up`:

```bash
KVROCKS_IMAGE=apache/kvrocks:2.14.0 VALKEY_IMAGE=valkey/valkey:8 podman-compose up -d
```

## Configuration

The AIL framework can be configured by editing the `core.cfg` file located in the `other_installers/docker` directory. This file is mounted into the `ail` container and will be applied on startup.

## Running the AIL Container Standalone (for Debugging)

It is also possible to run the AIL container by itself, but this is mainly intended for debugging and development. When running standalone, you will need to ensure that the AIL container can connect to externally running Redis/Valkey and Kvrocks instances.

Here is a basic example of how to run the AIL container standalone:

```bash
podman run --rm -p 7000:7000 --name ail \
  -e SKIP_LAUNCH_REDIS=true \
  -e SKIP_LAUNCH_KVROCKS=true \
  -e SKIP_CHECK_REDIS=true \
  -e SKIP_CHECK_KVROCKS=true \
  localhost/ail
```

In this mode, you would need to modify `core.cfg` to point to your database instances.
