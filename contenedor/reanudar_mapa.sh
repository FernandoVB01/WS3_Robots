#!/usr/bin/env bash
# Dentro del contenedor; requiere pantalla :1 y ninguna simulación previa.
set -euo pipefail
source /ws/contenedor/entorno.sh
mkdir -p /home/ws3/run
bash /ws/contenedor/generar_robot_mapeo.sh 10 > /ws/evidencias/logs/office_0_r2_generacion.log 2>&1
ros2 launch omni_workshop simulation.launch.py world:=office_0 generate:=false gui_config:=/ws/contenedor/gui_office_0.config > /ws/evidencias/logs/office_0_r2_simulacion.log 2>&1 &
echo $! > /home/ws3/run/launch.pid
for i in {1..180}; do
  grep -q 'Successfully loaded controller\|Successfully activated controllers\|Configured and activated' /ws/evidencias/logs/office_0_r2_simulacion.log && break
  sleep 1
done
python3 /ws/contenedor/filtrar_huella.py --ros-args -r /tf:=/do100_0000/tf -r /tf_static:=/do100_0000/tf_static > /ws/evidencias/logs/office_0_r2_filtro.log 2>&1 &
echo $! > /home/ws3/run/filtro.pid
ros2 launch omni_workshop mapping.launch.py rviz_config:=/ws/contenedor/mapping_office_0.rviz scan_topic:=/do100_0000/sensors/lidar2d_0/scan_filtrado > /ws/evidencias/logs/office_0_r2_slam.log 2>&1 &
echo $! > /home/ws3/run/mapping.pid
ros2 launch clearpath_nav2_demos nav2.launch.py setup_path:=/home/ws3/.ros/omni_workshop/clearpath/ use_sim_time:=true scan_topic:=/do100_0000/sensors/lidar2d_0/scan_filtrado > /ws/evidencias/logs/office_0_r2_nav2.log 2>&1 &
echo $! > /home/ws3/run/nav2.pid
for i in {1..180}; do
  grep -q 'Managed nodes are active' /ws/evidencias/logs/office_0_r2_nav2.log && break
  sleep 1
done
grep -q 'Managed nodes are active' /ws/evidencias/logs/office_0_r2_nav2.log
bash /ws/contenedor/ajustar_nav2.sh
wmctrl -r 'Gazebo Sim' -b remove,maximized_vert,maximized_horz
wmctrl -r 'Gazebo Sim' -e 0,0,0,638,690
wmctrl -r 'RViz' -b remove,maximized_vert,maximized_horz
wmctrl -r 'RViz' -e 0,640,0,638,690
ffmpeg -nostdin -loglevel warning -f x11grab -draw_mouse 0 -framerate 15 -video_size 1280x720 -i :1.0 -c:v libx264 -preset ultrafast -crf 24 -threads 1 -pix_fmt yuv420p -y /ws/evidencias/videos/03_office_0_repeticion.mp4 > /ws/evidencias/logs/office_0_r2_video.log 2>&1 &
echo $! > /home/ws3/run/record.pid
python3 /ws/contenedor/explorar_fronteras.py --max-goals 30 --max-sim-seconds 500 --bounds -2.07 -3.12 8.93 6.63 --ros-args -r /tf:=/do100_0000/tf -r /tf_static:=/do100_0000/tf_static > /ws/evidencias/logs/office_0_r2_exploracion.jsonl 2>&1 &
echo $! > /home/ws3/run/explorador.pid
python3 /ws/contenedor/cierre_autonomo.py office_0_r2 pequeno_repeticion /ws/evidencias/videos/03_office_0_repeticion.mp4 > /ws/evidencias/logs/office_0_r2_cierre_autonomo.log 2>&1 &
echo $! > /home/ws3/run/cierre.pid
wait
