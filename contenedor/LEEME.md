# Ejecución comprobada dentro de la VM

El anfitrión es Ubuntu 26.04.1 con ROS Lyrical. El contenedor ejecuta Ubuntu
24.04.5, ROS 2 Jazzy y Gazebo Harmonic 8.15.0; comparte el kernel de la VM.
No se mezclaron paquetes ROS de ambas distribuciones. Se compilaron 29 paquetes
con éxito y pasaron las cuatro pruebas numéricas.

## Preparación

Desde una terminal de Ubuntu, en la raíz de `~/WS3_proyecto`:

```bash
bash contenedor/instalar_docker_host.sh
docker build -t ws3-jazzy:harmonic contenedor
bash contenedor/iniciar.sh
```

El primer script requiere contraseña sudo e instala Docker/ACL. El acceso al
socket permite administrar contenedores con los privilegios del daemon. Para
una nueva sesión gráfica, si cambió XAUTHORITY, revisar la montura antes de
reutilizar un contenedor antiguo.

Con las seis dependencias de `src/dependencies.repos` descargadas en `src/clearpath_ws/src`:

```bash
docker exec ws3-jazzy bash /ws/contenedor/preparar_workspace.sh
docker exec --user 1000:1000 ws3-jazzy bash /ws/contenedor/compilar.sh
bash contenedor/pantalla.sh
```

La sesión comprobada usa el usuario UID/GID 1000, una pantalla Xephyr de
1280×720 y renderizado Mesa llvmpipe. El tiempo de simulación avanza más lento
que el real. `entorno.sh` selecciona Cyclone DDS, dominio 33 y pantalla :1.
`cyclonedds.xml` permite hasta 120 índices de participantes para el conjunto
robot/SLAM/Nav2; no cambia la cinemática ni las mediciones.

## Trayectorias

Abrir una terminal dentro del contenedor para cada comando que deba permanecer
activo. En **cada terminal**:

```bash
docker exec -it --user 1000:1000 ws3-jazzy bash
source /ws/contenedor/entorno.sh
```

Terminal 1:

```bash
ros2 launch omni_workshop workshop.launch.py rviz:=true \
  gui_config:=/ws/contenedor/gui_arena.config \
  rviz_config:=/ws/contenedor/workshop_grabacion.rviz
```

Esperar `Wheel controller active`. Terminal 2:

```bash
ros2 run omni_workshop self_controller --ros-args -p figure:=JRL
```

Para la otra prueba usar `figure:=prueba_omni`. Reiniciar la simulación entre
pruebas. Esperar `Figure finished.` y el mensaje de exportación del plotter antes
de cerrar. PNG/CSV/JSON se guardan en `/home/ws3/workshop_results` dentro del
contenedor. Copiarlos a `/ws/evidencias/trayectorias/<nombre>` para conservarlos
fuera del contenedor. Las ejecuciones verificadas ya están en esas carpetas.

## Mapeo con lecturas filtradas

El filtro conserva los retornos exteriores y descarta solamente puntos dentro
de la huella rectangular del Dingo-O: x ±0.343 m, y ±0.2585 m, transformados al
marco `base_link`. Así se evita que el láser incluya partes del propio robot en
SLAM. No se genera ocupación a partir de la geometría de los mundos.

En terminales distintas, cargando `entorno.sh` en cada una:

```bash
ros2 launch omni_workshop simulation.launch.py world:=office_0 \
  gui_config:=/ws/contenedor/gui_office_0.config
```

```bash
python3 /ws/contenedor/filtrar_huella.py --ros-args \
  -r /tf:=/do100_0000/tf -r /tf_static:=/do100_0000/tf_static
```

```bash
ros2 launch omni_workshop mapping.launch.py \
  scan_topic:=/do100_0000/sensors/lidar2d_0/scan_filtrado \
  rviz_config:=/ws/contenedor/mapping_office_0.rviz
```

```bash
ros2 launch clearpath_nav2_demos nav2.launch.py \
  setup_path:=/home/ws3/.ros/omni_workshop/clearpath/ use_sim_time:=true \
  scan_topic:=/do100_0000/sensors/lidar2d_0/scan_filtrado
```

El explorador propone destinos sobre el mapa SLAM; Nav2 planifica el movimiento.
Su mensaje `no_more_frontiers` no garantiza cobertura completa: revisar el mapa
antes de guardar. No abrir varias simulaciones simultáneamente.

Los videos de evidencia son capturas X11 de Gazebo y RViz lado a lado; no están
acelerados. Los intentos descartados permanecen separados en diagnóstico.
