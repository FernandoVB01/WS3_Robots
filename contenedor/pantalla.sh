#!/usr/bin/env bash
# Ejecutar en el anfitrión después de iniciar.sh.
set -euo pipefail
if ! docker exec ws3-jazzy test -S /tmp/.X11-unix/X1; then
  docker exec ws3-jazzy chmod 1777 /tmp/.X11-unix
  docker exec -d --user 1000:1000 ws3-jazzy bash -c \
    'exec Xephyr :1 -screen 1280x720 -ac -noreset -nolisten tcp -title "Workshop 3 - Gazebo y RViz" > /home/ws3/xephyr.log 2>&1'
  for attempt in {1..30}; do
    docker exec ws3-jazzy test -S /tmp/.X11-unix/X1 && break
    sleep 1
  done
  docker exec ws3-jazzy test -S /tmp/.X11-unix/X1
  docker exec -d --user 1000:1000 -e DISPLAY=:1 ws3-jazzy bash -c \
    'exec openbox > /home/ws3/openbox.log 2>&1'
fi
