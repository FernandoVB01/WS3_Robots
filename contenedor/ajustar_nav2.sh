#!/usr/bin/env bash
# Dentro del contenedor, con Nav2 activo. Ajustes usados solo al explorar mapas.
set -eo pipefail
source /ws/contenedor/entorno.sh
# Basta alcanzar la posición: la orientación final no es un requisito de SLAM.
ros2 param set /do100_0000/controller_server general_goal_checker.yaw_goal_tolerance 3.14159
# Reducir carga de MPPI en la VM, manteniendo comprobación de obstáculos.
ros2 param set /do100_0000/controller_server FollowPath.batch_size 500
