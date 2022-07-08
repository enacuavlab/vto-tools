This will build the docker image with nvidia sdkmanager inside
--------------------------------------------------------------
1) Create  Dockerfile (below)
2) Get sdkmanager_1.8.0-10363_amd64.deb from
   https://developer.nvidia.com/nvidia-sdk-manager
3) ...

docker system prune

docker build --build-arg GID=$(id -g) --build-arg UID=$(id -u) -t jetpackimage .

docker image ls
jetpackimage   latest    6b3f68fb6f84   10 seconds ago   944MB
ubuntu         18.04     ad080923604a   4 weeks ago      63.1MB

1a)
docker run --name jetpackcontainer --privileged -v /dev/bus/usb:/dev/bus/usb/ -v /dev:/dev jetpackimage
(keep running for executions below)

1b)
docker exec -it jetpackcontainer /bin/bash

sudo apt purge binfmt-support qemu-user-static
sudo apt-get update
sudo apt-get install qemu-user-static

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Dockerfile
-------------------------------------------------------------------------------
FROM ubuntu:18.04

ARG SDK_MANAGER_DEB=sdkmanager_1.8.0-10363_amd64.deb
ARG GID=1000
ARG UID=1000

ENV USERNAME jetpack
ENV HOME /home/$USERNAME
RUN useradd -m $USERNAME && \
        echo "$USERNAME:$USERNAME" | chpasswd && \
        usermod --shell /bin/bash $USERNAME && \
        usermod -aG sudo $USERNAME && \
        mkdir /etc/sudoers.d && \
        echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME && \
        chmod 0440 /etc/sudoers.d/$USERNAME && \
        # Replace 1000 with your user/group id
        usermod  --uid ${UID} $USERNAME && \
        groupmod --gid ${GID} $USERNAME


RUN apt-get update -y --fix-missing \
    && apt-get install -y vim sudo libgconf-2-4 libcanberra-gtk-module locales usbutils python3 qemu-user-static libxml2-utils net-tools iputils-ping screen  ssh cpio binutils libmoosex-getopt-perl netcat uuid-runtime gdisk \
    && apt-get autoremove -y \
    && apt-get autoclean -y \
    && rm -rf /var/lib/apt/lists/*



USER jetpack
COPY --chown=jetpack:jetpack ${SDK_MANAGER_DEB}  /home/${USERNAME}/
WORKDIR /home/${USERNAME}
RUN sudo apt-get install -f /home/${USERNAME}/${SDK_MANAGER_DEB}
RUN rm /home/${USERNAME}/${SDK_MANAGER_DEB}

ENV SHELL=/bin/bash
ENV TERM=xterm
ENV LANG C.UTF-8
CMD exec /bin/bash -c "trap : TERM INT; sleep infinity & wait"
