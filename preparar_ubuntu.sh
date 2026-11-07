#!/usr/bin/env bash
# Ejecutar con bash preparar_ubuntu.sh desde Ubuntu 24.04.
set -eo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
source /etc/os-release
if [[ "${ID:-}" != ubuntu || "${VERSION_ID:-}" != 24.04 ]]; then
  echo "Entorno no validado para este taller: ${PRETTY_NAME:-desconocido}."
  echo 'Se requiere Ubuntu 24.04, ROS 2 Jazzy y Gazebo Harmonic. No se instalaron paquetes.'
  exit 1
fi
if [[ -n "${ROS_DISTRO:-}" && "$ROS_DISTRO" != jazzy ]]; then
  echo "La terminal tiene ROS_DISTRO=$ROS_DISTRO. Abre una terminal sin cargar otra distribución de ROS."
  echo 'No mezcles entornos ROS antes de compilar. No se instalaron paquetes.'
  exit 1
fi
if [[ ! -f /opt/ros/jazzy/setup.bash ]]; then
  echo 'Falta ROS 2 Jazzy. Instálalo según https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html y vuelve a ejecutar.'
  exit 1
fi
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install -y python3-vcstool python3-colcon-common-extensions python3-rosdep \
  python3-matplotlib ros-jazzy-ros-gz ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard
if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  sudo rosdep init
fi
rosdep update
(cd src && vcs import < dependencies.repos)
rosdep install --from-paths src --ignore-src -r -y --skip-keys clearpath_generator_robot
python3 -m unittest discover -s tests -v
MAKEFLAGS=-j2 colcon build --symlink-install --parallel-workers 2
echo 'Preparado. Sigue LEEME_EJECUCION.md; carga install/setup.bash en cada terminal.'
