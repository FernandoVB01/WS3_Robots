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
