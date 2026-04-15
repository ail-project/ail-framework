FROM ubuntu:24.04

# pre-seed the timezone info
RUN ln -sf /usr/share/zoneinfo/UTC /etc/localtime \
    # install sudo as it's not in the base image & installing_deps.sh expects it
    && apt-get update && apt-get install --assume-yes git sudo \
    # Make sudo works right away
    && echo 'ubuntu ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/ubuntu \
    && chmod 0440 /etc/sudoers.d/ubuntu

USER ubuntu