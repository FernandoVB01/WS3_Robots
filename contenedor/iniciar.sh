#!/usr/bin/env bash
# Construye primero: docker build -t ws3-jazzy:harmonic contenedor
set -euo pipefail
project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if docker container inspect ws3-jazzy >/dev/null 2>&1; then
  existing_dir=$(docker inspect --format '{{range .Mounts}}{{if eq .Destination "/ws"}}{{.Source}}{{end}}{{end}}' ws3-jazzy)
  [[ "$existing_dir" == "$project_dir" ]] || {
    echo "Ya existe ws3-jazzy con otro proyecto: $existing_dir"; exit 1;
  }
  docker start ws3-jazzy
  exit 0
fi
: "${DISPLAY:?Falta DISPLAY de la sesión gráfica}"
: "${XAUTHORITY:?Falta XAUTHORITY de la sesión gráfica}"
[[ -f "$XAUTHORITY" ]] || { echo 'No existe el archivo XAUTHORITY'; exit 1; }
host_display_number=${DISPLAY##*:}
host_display_number=${host_display_number%%.*}
device_args=()
if [[ -e /dev/dri/renderD128 ]]; then
  device_args+=(--device /dev/dri --group-add "$(stat -c %g /dev/dri/renderD128)")
fi
docker run -d --name ws3-jazzy --init --shm-size=1g \
  --hostname "$(hostname)" "${device_args[@]}" \
  --mount "type=bind,src=$project_dir,dst=/ws" \
  --mount "type=bind,src=/tmp/.X11-unix/X$host_display_number,dst=/tmp/.X11-unix/X$host_display_number,readonly" \
  --mount "type=bind,src=$XAUTHORITY,dst=/tmp/host.xauth,readonly" \
  -e DISPLAY="$DISPLAY" -e XAUTHORITY=/tmp/host.xauth -e HOME=/home/ws3 \
  -e QT_X11_NO_MITSHM=1 -e QT_QPA_PLATFORM=xcb -e LIBGL_ALWAYS_SOFTWARE=1 \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp -e CYCLONEDDS_URI=file:///ws/contenedor/cyclonedds.xml -e LP_NUM_THREADS=1 -e ROS_DOMAIN_ID=33 -e TZ=America/Guayaquil \
  "${WS3_IMAGE:-ws3-jazzy:harmonic}"
