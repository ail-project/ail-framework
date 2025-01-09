Docker Quick Start (Ubuntu 18.04 LTS)
------------

:warning:
This Docker is not maintained at the moment.
If you are interested to contribute, please submit a Pull Request


# Have docker Installed

## Linux Installation

Here is the [link](https://docs.docker.com/engine/install/) with the installation 
steps for all the diferent linux Platforms.

If your distro is not mentioned you probably need to install it through the 
package manager of the distro that you are using (Ex.: ArchLinux, NixOS).

## Windows Installation

To be able to run docker on a Windows device you will have to check the documentation 
on how to install it on windows.

If I'm not mistaken you have 2 ways of installing docker on windows:
 - Only using the WSL with an Ubuntu image, in this case you follow the 
 same [installation steps](https://docs.docker.com/engine/install/ubuntu/) as 
 you would in an Ubuntu distro.
 - Using the [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)

## Mac Installation

For mac users follow the [documentation](https://docs.docker.com/desktop/setup/install/mac-install/)

# Build the docker image

Type these commands to build the Docker image:

```bash
git clone https://github.com/ail-project/ail-framework.git
cd ail-framework
cp -r ./other_installers/docker/Dockerfile ./other_installers/docker/docker_start.sh ./other_installers/docker/pystemon ./
cp ./configs/update.cfg.sample ./configs/update.cfg
vim/nano ./configs/update.cfg (set auto_update to False)
docker build --build-arg tz_buildtime=YOUR_GEO_AREA/YOUR_CITY -t ail-framework .
```
# Start AIL

To start AIL on port 7000, type the following command below:
```
docker run -p 7000:7000 ail-framework
```

# Debug Container

To debug the running container, type the following command and note the container name or identifier:

```bash
docker ps
```

After getting the name or identifier type the following commands:
```bash
docker exec -it CONTAINER_NAME_OR_IDENTIFIER bash
cd /opt/ail
```

Install using Ansible
---------------------

Please check the [Ansible readme](ansible/README.md).

