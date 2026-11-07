#!/usr/bin/env bash
# Dentro del contenedor, como el UID/GID del usuario anfitrión.
set -eo pipefail
cd /ws
source /opt/ros/jazzy/setup.bash
python3 -m unittest discover -s tests -v
MAKEFLAGS=-j2 colcon build --symlink-install --parallel-workers 2
