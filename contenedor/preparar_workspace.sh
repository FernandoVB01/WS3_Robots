#!/usr/bin/env bash
# Dentro de ws3-jazzy, como root, para resolver dependencias del código fijado.
set -eo pipefail
cd /ws
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || exit 1
source /opt/ros/jazzy/setup.bash
if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  rosdep init
fi
apt-get update
rosdep update --rosdistro jazzy
rosdep install --from-paths src --ignore-src --rosdistro jazzy -y \
  --skip-keys clearpath_generator_robot
