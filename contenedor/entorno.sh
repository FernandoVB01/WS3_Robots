# Cargar dentro del contenedor antes de cada comando ROS.
source /opt/ros/jazzy/setup.bash
source /ws/install/setup.bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export ROS_DOMAIN_ID=33
export LP_NUM_THREADS=1
export DISPLAY=:1
export CYCLONEDDS_URI=file:///ws/contenedor/cyclonedds.xml
