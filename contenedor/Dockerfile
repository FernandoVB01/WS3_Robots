FROM ros:jazzy-ros-base-noble@sha256:8eed0a4669bbf43ee331878a4c39bd8ebddea8e3312a58b4fae8edb14526b617
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git ca-certificates \
    python3-vcstool python3-colcon-common-extensions python3-rosdep \
    python3-matplotlib python3-scipy python3-pytest \
    ros-jazzy-ros-gz ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-rviz2 ros-jazzy-xacro ros-jazzy-rmw-cyclonedds-cpp \
    ffmpeg xauth x11-utils mesa-utils xserver-xephyr openbox wmctrl \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /home/ws3 /ws && chown 1000:1000 /home/ws3 /ws
WORKDIR /ws
CMD ["sleep", "infinity"]
