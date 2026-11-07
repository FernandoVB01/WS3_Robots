# Validación y procedencia

Repositorio original: https://github.com/davatorr1009/workshop_03
Commit base: `2dd570fa2691df231331c01257ede128f96914de`.

Pruebas locales: `python -m unittest discover -s tests -v`.
Resultado: 4 pruebas satisfactorias, que verifican signos y magnitudes de movimientos básicos,
transformación a 90 grados, 100 combinaciones de cinemática directa/inversa, continuidad,
derivadas y margen geométrico de las dos trayectorias añadidas.

Estas pruebas no sustituyen la ejecución de ROS 2, la dinámica de contacto de Gazebo,
el mapeo SLAM ni la revisión de los videos. No se dispone de esos resultados desde Windows.
El margen comprobado corresponde a la trayectoria deseada; el robot puede desviarse.

## Comprobación en Ubuntu — 6 de noviembre de 2026

- Fuente revisada: commit `843ac6e3d9320d81bf9f91e1a8ebd8a8e9fd3398`.
- Sistema observado: Ubuntu 26.04.1 LTS (resolute), x86_64.
- ROS observado: solo `/opt/ros/lyrical`, con `ROS_DISTRO=lyrical`.
- No se encontraron ejecutables `gz`/`gazebo` ni paquetes instalados que
  coincidan con `*gazebo*`, `*gz-sim*` o `*ros-gz*`.
- Las cuatro pruebas numéricas se ejecutaron de nuevo en Linux y pasaron.
- El instalador ahora comprueba la versión de Ubuntu y evita mezclar otra
  distribución ROS antes de instalar paquetes. Se verificó que se detiene en
  este Ubuntu 26.04 antes de ejecutar `sudo`.
- En este diagnóstico inicial aún no se había compilado ni ejecutado Gazebo.
  La validación posterior en contenedor se detalla abajo.

Los comandos, salidas y códigos de retorno están en `evidencias/diagnostico/`.
Estos registros son evidencia de diagnóstico y pruebas numéricas, no de
ejecución del robot. La ejecución debe continuar en Ubuntu 24.04 / Jazzy /
Harmonic. Durante el diagnóstico inicial no se instalaron paquetes ROS en el sistema 26.04.

## Ejecución en contenedor Jazzy / Harmonic

Con autorización del usuario se instaló Docker y ACL en la VM anfitriona. ROS
Lyrical permanece en el anfitrión; el contenedor utiliza Ubuntu 24.04.5, Jazzy
y Gazebo 8.15.0. Las seis dependencias Clearpath coinciden con los commits de
`src/dependencies.repos` (véase `evidencias/diagnostico/clearpath_fetch.log`).

- Resolución de dependencias: completada con rosdep.
- Compilación: 29 paquetes, 3 min 19 s, código de salida 0.
- Pruebas numéricas en el contenedor: 4 aprobadas.
- `prueba_omni`: controlador finalizado; 403 muestras finitas, tiempo creciente
  hasta 20.10 s y métricas recalculadas desde el CSV coincidentes con el JSON.
- Video de `prueba_omni`: H.264, 1280 × 720, 15 fps; 169.73 s incluyendo espera
  y vista final. Es una captura real de Gazebo y RViz, sin acelerar.
- JRL: controlador finalizado; 1821 muestras finitas, tiempo creciente hasta
  90.999 s. Las tres métricas RMSE se recalcularon desde el CSV y coinciden con
  el JSON. Cero muestras con reloj o ruedas desactualizados según la auditoría
  incorporada al plotter (umbral 0.5 s).
- Video JRL: H.264, 1280 × 720, 15 fps, 744 s, captura real sin acelerar.
- El primer intento JRL se descartó por congelación de odometría; se conserva
  separado en diagnóstico y no sustenta los resultados del informe.
- No se modificó el xacro: las dos trayectorias completas utilizan el modelo
  original y la cinemática implementada en el proyecto.
- Mapas: en ejecución; se documentarán por separado al guardar PGM/YAML.

Los avisos NaN iniciales ocurren durante la transición al controlador de ruedas
y cesan después de la orden cero; se comprobaron velocidades finitas antes de
la trayectoria. El cierre del lanzador se ajustó para ejecutar una sola vez la
limpieza de los procesos hijos de Gazebo. Se añadieron argumentos opcionales
de configuración visual para grabar sin modificar las vistas predeterminadas.
