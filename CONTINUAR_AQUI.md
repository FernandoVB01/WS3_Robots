# Continuidad del Workshop 3

Última actualización: 6 de noviembre de 2026, durante la exploración de office_0.
**Este es un punto de continuidad, no la entrega final.** Consultar los logs vivos
antes de actuar: el mapa y el video pueden haber terminado después de este commit.

## Instrucciones del usuario

- Prioridad: ejecutar las trayectorias y conservar evidencias reales. Se permite
  modificar el xacro si hace falta; no fue necesario para las trayectorias.
- Terminar office_0 y office_4, guardar ambos PGM/YAML y videos Gazebo/RViz.
- Generar el informe en LaTeX, con redacción natural y concreta, **solo después
  de terminar todas las pruebas**. Aún no se ha creado el LaTeX.
- Preparar el archivo final y subirlo a GitHub. La publicación está autorizada.
- Dejar el estado y comandos para continuar con otra IA. Pedir intervención
  solamente cuando se necesite contraseña o interacción manual.
- No inventar resultados. Las imágenes de referencia de src/ no son evidencias.

## Entorno y proyecto

Proyecto real: `/home/fercho/WS3_proyecto`, rama `main`.
Remoto: https://github.com/FernandoVB01/WS3_Robots
No confundir con una copia antigua en `Documents/Codex/.../work/WS3_Robots`.

Anfitrión VirtualBox: Ubuntu 26.04.1, ROS Lyrical. No instalar Jazzy encima.
Contenedor Docker `ws3-jazzy`, imagen `ws3-jazzy:harmonic`: Ubuntu 24.04.5,
ROS Jazzy y Gazebo Harmonic 8.15.0. `/ws` monta el proyecto real. Usuario 1000:1000.
Se compilaron 29 paquetes y pasaron las cuatro pruebas numéricas.

En cada terminal ROS del contenedor:

```bash
docker exec -it --user 1000:1000 ws3-jazzy bash
source /ws/contenedor/entorno.sh
```

Esto selecciona Cyclone DDS, dominio 33, configuración de participantes y
DISPLAY=:1. Xephyr/Openbox están abiertos a 1280×720, con Gazebo y RViz lado a lado.
La VM usa renderizado por software y simula lentamente. No cerrar ni suspender
la VM mientras continúe la grabación.

## Terminado y verificado

| Prueba | Muestras | Tiempo registrado [s] | RMSE Gazebo/referencia [m] |
|---|---:|---:|---:|
| prueba_omni | 403 | 20.10 | 0.0589094610 |
| JRL | 1821 | 90.999 | 0.0694575016 |

PNG/CSV/JSON y validación: `evidencias/trayectorias/prueba_omni/` y
`evidencias/trayectorias/JRL/`. Los controladores terminaron; los datos son
finitos, con tiempos crecientes y métricas recalculadas desde CSV.
JRL registra cero muestras desactualizadas según la auditoría del plotter.

Videos reales, finalizados y comprobados con ffprobe:
- `evidencias/videos/01_prueba_omni.mp4`: 169.73 s.
- `evidencias/videos/02_JRL.mp4`: 744 s.
Ambos H.264, 1280×720, 15 fps, sin acelerar.

El primer intento JRL perdió actualización de odometría y se descartó. Está
separado localmente en diagnóstico y no se usa en el informe ni en la entrega.
La repetición completa con Cyclone DDS sí es válida. No se modificó el xacro
para estas pruebas.

## Lo que sigue corriendo: office_0

Procesos activos: simulación, SLAM/RViz, Nav2, filtro de huella, explorador,
FFmpeg y cierre autónomo. **No abrir otra simulación ni sobrescribir este video.**

Video actual del anfitrión:
`/home/fercho/WS3_proyecto/evidencias/videos/03_office_0.mp4`

El archivo MP4 puede no reproducirse hasta que FFmpeg cierre correctamente.
Se excluye de este commit mientras está abierto. Los mapas `pequeno.pgm/yaml`
son puntos de recuperación de una exploración incompleta; necesitan revisión.

Comprobar avance desde Ubuntu:

```bash
tail -n 12 ~/WS3_proyecto/evidencias/logs/office_0_exploracion_filtrada.jsonl
cat ~/WS3_proyecto/evidencias/logs/office_0_cierre_autonomo.log
cat ~/WS3_proyecto/evidencias/logs/office_0_cierre_autonomo.json
```

El JSON de cierre no existirá hasta terminar. `cierre_autonomo.py` está lanzado
con `docker exec -d`: espera a que termine el explorador, guarda el mapa, captura
la pantalla, envía SIGINT a FFmpeg y verifica el video con ffprobe. Funciona sin
el chat. Deja Gazebo/SLAM/Nav2 abiertos para inspección posterior.

El explorador tiene límites de 25 destinos y 350 segundos simulados desde su
inicio original (t=73), y luego intenta volver al inicio. Un destino rechazado
no equivale a zona recorrida; revisar el mapa y el registro. `no_more_frontiers`
tampoco garantiza cobertura completa.

Archivos de PID dentro del contenedor: `/home/ws3/run/{launch,mapping,nav2,
filtro,explorador,record,cierre}.pid`. Verificar el comando del proceso antes de
señalarlo. No matar el cierre autónomo al cambiar de chat. La identidad de los
procesos se comprueba con su tiempo de inicio para evitar reutilización de PID.

## Ajustes utilizados en el mapeo

- Dos lidars originales a 40 Hz en office_0.
- `filtrar_huella.py`: transforma retornos al marco base_link y elimina solamente
  puntos dentro de x ±0.343 m, y ±0.2585 m. Se observaron retornos del propio robot
  que bloqueaban Nav2. El SLAM actual comenzó de cero con el filtro.
- SLAM y Nav2 usan `/do100_0000/sensors/lidar2d_0/scan_filtrado`.
- Nav2: tolerancia angular final 3.14159 rad (para explorar basta la posición),
  MPPI batch_size=500. Aplicar `bash /ws/contenedor/ajustar_nav2.sh` al reiniciarlo.
- `exploracion_bt.xml` conserva el árbol de navegación de Nav2 y amplía a 2000 ms
  la espera de confirmación de acciones/servicios. Con 20 ms se observaron abortos
  por latencia. El explorador selecciona este árbol por destino.
- Paso físico inicial 1 ms, posteriormente 2 ms. Se ensayó brevemente 4 ms sin
  mejora clara y se volvió a 2 ms. Están los registros de esas llamadas.
- El explorador se reinició una vez con `--resume-log` para conservar el origen
  y los destinos tras ampliar la espera. El mapa SLAM no se reinició entonces.
- Los archivos de diagnóstico/arranque no sustituyen los resultados finales.

## Siguientes pasos

1. Esperar el cierre autónomo de office_0. Inspeccionar PGM/YAML, captura y video.
   Si falta cobertura accesible, continuar el mismo SLAM con otra grabación,
   conservando las tomas anteriores y explicando los límites reales.
2. Con el mapa guardado y el MP4 finalizado, cerrar los lanzadores con SIGINT y
   verificar que no queden servidores Gazebo. No usar pkill indiscriminado.
3. Iniciar office_4 usando los comandos de `contenedor/LEEME.md`, sustituyendo
   world/configs por office_4. Los archivos de vistas ya existen.
4. Para reducir carga se preparó `generar_robot_mapeo.sh 10`, que genera la
   configuración y ajusta solo la frecuencia de ambos lidars a 10 Hz. **Todavía
   no se ha validado en una simulación.** Ejecutarlo sin simulación activa y luego
   lanzar `simulation.launch.py world:=office_4 generate:=false`. Revisar que
   aparezcan los scans, TF y mapa antes de explorar. Si falla, usar generate:=true
   para regenerar el modelo original a 40 Hz.
5. Iniciar filtro, SLAM, Nav2 y aplicar ajustar_nav2.sh. Grabar con FFmpeg en
   `04_office_4.mp4`, guardar record.pid e iniciar el explorador en segundo plano:

   ```bash
   python3 /ws/contenedor/explorar_fronteras.py --max-goals 35 \
     --max-sim-seconds 600 --bounds -3.22 -11.73 28.78 6.42 --ros-args \
     -r /tf:=/do100_0000/tf -r /tf_static:=/do100_0000/tf_static
   ```

   Guardar explorador.pid. Lanzar el cierre autónomo para office_4/grande con
   `docker exec -d`, cargando entorno.sh y redirigiendo la salida a un log.
6. Guardar `grande.pgm/yaml` mediante map_saver_cli. Revisar cobertura, no solo
   existencia de archivos. Mapas y videos de office_4 todavía no existen.
7. Al terminar todas las pruebas, actualizar INFORME.md/VALIDACION.md/guías y
   generar el informe LaTeX con las gráficas reales, mapas y limitaciones.
8. Crear archivo de entrega sin build/install/log/.git ni dependencias descargadas
   de Clearpath; conservar `dependencies.repos` para reproducibilidad.
9. Añadir los videos finalizados a GitHub, revisar tamaño (GitHub limita archivos
   grandes; si hace falta recomprimir una copia y verificarla, conservando el
   original). Actualizar este estado y publicar la entrega.

## Publicación y seguridad de archivos

Este commit contiene solo videos cerrados de las dos trayectorias. Los videos
abiertos y diagnósticos descartados se conservan localmente, sin publicarlos como
entrega. `.gitignore` los excluye; para añadir un video finalizado usar
`git add -f evidencias/videos/03_office_0.mp4` después de comprobarlo.

La autenticación de GitHub debe completarse en la VM si todavía está pendiente.
Nunca pedir al usuario que envíe contraseñas o tokens al chat.
