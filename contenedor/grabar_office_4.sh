#!/usr/bin/env bash
# Dentro del contenedor; requiere pantalla :1 y ninguna simulación previa.
set -eo pipefail
source /ws/contenedor/entorno.sh
mkdir -p /home/ws3/run
bash /ws/contenedor/generar_robot_mapeo.sh 10 > /ws/evidencias/logs/office_4_r1_generacion.log 2>&1
ros2 launch omni_workshop simulation.launch.py world:=office_4 generate:=false gui_config:=/ws/contenedor/gui_office_4.config > /ws/evidencias/logs/office_4_r1_simulacion.log 2>&1 &
echo $! > /home/ws3/run/launch.pid
sleep 25
ros2 run controller_manager spawner joint_state_broadcaster platform_velocity_controller -c /do100_0000/controller_manager --controller-manager-timeout 60 --switch-timeout 60 >> /ws/evidencias/logs/office_4_r1_simulacion.log 2>&1
python3 /ws/contenedor/filtrar_huella.py --ros-args -r /tf:=/do100_0000/tf -r /tf_static:=/do100_0000/tf_static > /ws/evidencias/logs/office_4_r1_filtro.log 2>&1 &
echo $! > /home/ws3/run/filtro.pid
ros2 launch /ws/contenedor/mapping_grande.launch.py > /ws/evidencias/logs/office_4_r1_slam.log 2>&1 &
echo $! > /home/ws3/run/mapping.pid
ros2 launch clearpath_nav2_demos nav2.launch.py setup_path:=/home/ws3/.ros/omni_workshop/clearpath/ use_sim_time:=true scan_topic:=/do100_0000/sensors/lidar2d_0/scan_filtrado > /ws/evidencias/logs/office_4_r1_nav2.log 2>&1 &
echo $! > /home/ws3/run/nav2.pid
for i in {1..180}; do
  grep -q 'Managed nodes are active' /ws/evidencias/logs/office_4_r1_nav2.log && break
  sleep 1
done
grep -q 'Managed nodes are active' /ws/evidencias/logs/office_4_r1_nav2.log
bash /ws/contenedor/ajustar_nav2.sh
ros2 param set /do100_0000/controller_server FollowPath.vx_max 0.35
ros2 param set /do100_0000/controller_server FollowPath.vy_max 0.25
ros2 param set /do100_0000/controller_server FollowPath.wz_max 0.4
wmctrl -r 'Gazebo Sim' -b remove,maximized_vert,maximized_horz
wmctrl -r 'Gazebo Sim' -e 0,0,0,638,690
wmctrl -r 'RViz' -b remove,maximized_vert,maximized_horz
wmctrl -r 'RViz' -e 0,640,0,638,690
ffmpeg -nostdin -loglevel warning -f x11grab -draw_mouse 0 -framerate 15 -video_size 1280x720 -i :1.0 -c:v libx264 -preset ultrafast -crf 24 -threads 1 -pix_fmt yuv420p -y /ws/evidencias/videos/04_office_4.mp4 > /ws/evidencias/logs/office_4_r1_video.log 2>&1 &
echo $! > /home/ws3/run/record.pid
python3 /ws/contenedor/explorar_fronteras.py --max-goals 20 --max-sim-seconds 300 --bounds -3.22 -11.73 28.78 6.42 --ros-args -r /tf:=/do100_0000/tf -r /tf_static:=/do100_0000/tf_static > /ws/evidencias/logs/office_4_r1_exploracion.jsonl 2>&1 &
echo $! > /home/ws3/run/explorador.pid
python3 /ws/contenedor/cierre_autonomo.py office_4_r1 grande /ws/evidencias/videos/04_office_4.mp4 > /ws/evidencias/logs/office_4_r1_cierre_autonomo.log 2>&1 &
echo $! > /home/ws3/run/cierre.pid
wait
