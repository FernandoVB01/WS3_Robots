#!/usr/bin/env bash
# Usar sin simulación activa. Reduce únicamente la frecuencia de ambos lidars.
set -euo pipefail
source /ws/contenedor/entorno.sh
sensor_rate=${1:-10}
setup_dir=/home/ws3/.ros/omni_workshop/clearpath
mkdir -p "$setup_dir"
cp /ws/src/omni_workshop/config/dingo_o.yaml "$setup_dir/robot.yaml"
ros2 run clearpath_generator_common generate_description -s "$setup_dir"
ros2 run clearpath_generator_common generate_semantic_description -s "$setup_dir"
ros2 run clearpath_generator_gz generate_launch -s "$setup_dir"
ros2 run clearpath_generator_gz generate_param -s "$setup_dir"
python3 - "$setup_dir/robot.urdf.xacro" "$sensor_rate" <<'PY'
import sys
import xml.etree.ElementTree as ET
rate=float(sys.argv[2])
assert 1 <= rate <= 40, 'La frecuencia debe estar entre 1 y 40 Hz'
ET.register_namespace('xacro','http://ros.org/wiki/xacro')
tree=ET.parse(sys.argv[1]); nodes=tree.findall('.//{http://ros.org/wiki/xacro}hokuyo_ust')
assert len(nodes)==2, 'Se esperaban dos lidars Hokuyo'
for node in nodes: node.set('update_rate',str(rate))
tree.write(sys.argv[1],encoding='unicode',xml_declaration=True)
print(f'Lidars configurados a {rate} Hz. Lanzar simulation.launch.py generate:=false.')
PY
