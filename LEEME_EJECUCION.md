# Ejecutar en Ubuntu 24.04 / VirtualBox

## 1. Copiar y preparar

Copia `WS3_JRL_preparado.tar.gz` desde Windows a tu carpeta personal de Ubuntu usando una carpeta compartida de VirtualBox o el método de transferencia que tengas habilitado. Los siguientes comandos suponen que está en `~/WS3_JRL_preparado.tar.gz`.

```bash
cd ~
tar -xzf WS3_JRL_preparado.tar.gz
cd ~/WS3_proyecto
bash preparar_ubuntu.sh
```

El script requiere ROS 2 Jazzy instalado en `/opt/ros/jazzy`; si falta se detiene y muestra la documentación oficial de instalación. Descarga las dependencias Clearpath fijadas por el profesor (aproximadamente 1 GB), instala dependencias y compila con dos procesos. Necesita Internet y contraseña de sudo. Si falla, no continúes a los lanzadores: conserva el primer error de la terminal. Si ya tienes otra carpeta `WS3_proyecto`, extrae este archivo en una carpeta distinta para no mezclar trabajos.

## 2. Prueba del controlador

Terminal 1:

```bash
cd ~/WS3_proyecto
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch omni_workshop workshop.launch.py rviz:=true
```

Espera el mensaje **Wheel controller active** y confirma que la simulación avanza.

Terminal 2:

```bash
cd ~/WS3_proyecto
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run omni_workshop self_controller --ros-args -p figure:=prueba_omni
```

Al terminar espera al menos tres segundos: el nodo plotter guarda PNG, CSV y JSON en `~/workshop_results/`. Cierra el lanzamiento de la terminal 1 con Ctrl+C y espera a que termine. Vuelve a ejecutar ese lanzamiento para reiniciar la posición. Cuando aparezca **Wheel controller active**, en la terminal 2 ejecuta:

```bash
ros2 run omni_workshop self_controller --ros-args -p figure:=JRL
```

Graba la prueba y las letras con Gazebo y RViz visibles al mismo tiempo. La vista superior de Gazebo ayuda a reconocer las letras; en el gráfico usa x horizontal e y vertical. Las conexiones y los trazos repasados son intencionales. La imagen `JRL_referencia.png` es solo una previsualización matemática, no evidencia de simulación.

## 3. Mapa pequeño

Cierra la simulación de trayectorias antes de comenzar. En CADA terminal nueva carga el entorno:

```bash
cd ~/WS3_proyecto
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

Terminal 1:

```bash
ros2 launch omni_workshop simulation.launch.py world:=office_0
```

Terminal 2:

```bash
ros2 launch omni_workshop mapping.launch.py
```

Con el panel **Omnidirectional teleop** de Gazebo enfocado, usa W/S para avanzar/retroceder, A/D para desplazarte lateralmente y Q/E para girar. Suelta las teclas para parar. Explora despacio las zonas accesibles y vuelve al inicio. Vigila obstáculos; no hay navegación autónoma en estos pasos. RViz debe ir mostrando el mapa. No abras RViz por separado porque necesita las remisiones TF del lanzador.

Terminal 3, cuando el mapa esté completo y el robot detenido:

```bash
mkdir -p ~/WS3_proyecto/evidencias/mapas
ros2 run nav2_map_server map_saver_cli -f ~/WS3_proyecto/evidencias/mapas/pequeno \
  --ros-args -r map:=/do100_0000/map -p use_sim_time:=true
ls -lh ~/WS3_proyecto/evidencias/mapas/pequeno.*
```

Comprueba que existen `pequeno.pgm` y `pequeno.yaml`. El PGM se puede abrir con el visor de imágenes; verifica que contiene el entorno recorrido, no solo un área vacía. Graba Gazebo y RViz durante la exploración.

## 4. Mapa grande

Cierra con Ctrl+C los lanzamientos de las terminales 1 y 2. Espera a que terminen. En la terminal 1:

```bash
ros2 launch omni_workshop simulation.launch.py world:=office_4
```

En la terminal 2:

```bash
ros2 launch omni_workshop mapping.launch.py
```

Recorre las zonas accesibles por secciones, revisita intersecciones y regresa al inicio. No intentes entrar en espacios donde el robot no cabe. Graba la exploración y, al finalizar, en la terminal 3:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/WS3_proyecto/evidencias/mapas/grande \
  --ros-args -r map:=/do100_0000/map -p use_sim_time:=true
ls -lh ~/WS3_proyecto/evidencias/mapas/grande.*
```

## 5. Videos y entrega final

Puedes grabar desde Windows la ventana de VirtualBox usando tu grabador habitual, siempre que Gazebo y RViz estén visibles en pantalla dividida durante la ejecución. También puedes usar el grabador de Ubuntu. Guarda los videos en `~/WS3_proyecto/evidencias/videos/` (créala con `mkdir -p` si hace falta).

Archivos sugeridos: `01_prueba_omni.mp4`, `02_JRL.mp4`, `03_mapa_pequeno.mp4` y `04_mapa_grande.mp4`. Conserva el formato real que genere el grabador; no cambies solo la extensión. No sustituyas las grabaciones por la previsualización de referencia.

```bash
mkdir -p ~/WS3_proyecto/evidencias/trayectorias
cp -v ~/workshop_results/trajectory_* ~/WS3_proyecto/evidencias/trayectorias/
```

Identifica los resultados por su hora de ejecución. Completa la tabla de `INFORME.md` con los JSON de esta sesión y añade tus observaciones. No incluyas resultados de talleres anteriores si ya había archivos en `~/workshop_results`.

Para empaquetar fuentes y evidencias sin los directorios generados de compilación:

```bash
cd ~
tar --exclude='WS3_proyecto/build' --exclude='WS3_proyecto/install' \
    --exclude='WS3_proyecto/log' --exclude='.git' --exclude='__pycache__' \
    -czf WS3_JRL_entrega_final.tar.gz WS3_proyecto
tar -tzf WS3_JRL_entrega_final.tar.gz | tail -20
```

Antes de entregar comprueba: código, informe con resultados reales, dos pares PGM/YAML, gráficos/datos y videos. El archivo preparado inicialmente en Windows contiene código y documentación; los mapas y videos se agregan después de tu ejecución.

## Si algo falla

- `Package not found`: carga `install/setup.bash` en esa terminal y confirma que la compilación terminó correctamente.
- `Waiting for the simulation`: confirma que Gazebo no está en pausa y que apareció `Wheel controller active`.
- Compilación interrumpida por falta de memoria: repite con `MAKEFLAGS=-j1 colcon build --symlink-install --parallel-workers 1`.
- No aparecen mapas: revisa la terminal de `mapping.launch.py`; confirma que publican con `ros2 topic hz /do100_0000/map` (Ctrl+C para salir).
- No continúes sobre una simulación anterior abierta. Cierra los lanzadores de esta práctica antes de cambiar de entorno.
