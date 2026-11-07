# Entregables del Workshop 3

Lista contrastada con la consigna del docente compartida por el grupo.
Este archivo es una lista de control; no declara completa la entrega.

## Primera parte: odometría y controlador propios

- [x] Controlador Python para el modelo omnidireccional mecanum de 45°.
- [x] Trayectoria de prueba y comparación entre referencia, odometría calculada y posición respecto al mundo de Gazebo.
- [x] Trayectoria JRL: Jhon, Raziel y Luis.
- [x] Gráficas, CSV y métricas de las dos ejecuciones completas.
- [x] Videos de ambas trayectorias con Gazebo y RViz en pantalla dividida.

Los resultados corresponden a simulación. No se hicieron mediciones con un robot físico.
Las pruebas numéricas por sí solas no se presentan como evidencia de Gazebo.

## Segunda parte: mapeo y controlador de fábrica

- [ ] Completar y revisar el mapa del entorno pequeño office_0.
- [ ] Completar y revisar el mapa del entorno grande office_4.
- [ ] Conservar ambos mapas en PGM, junto con sus YAML.
- [ ] Revisar los videos de mapeo con Gazebo y RViz simultáneamente.

office_0 tiene una primera toma y mapa parciales. La repetición está en curso;
consultar CONTINUAR_AQUI.md y los logs office_0_r2 antes de iniciar procesos.
La existencia de un PGM no implica que el entorno esté completamente explorado.
El mapeo usa el controlador de fábrica de Clearpath, SLAM y Nav2.

## Archivos de entrega

- [ ] Carpeta de trabajo empaquetada en .tar o .zip, con los códigos implementados.
- [x] Markdown INFORME.md con respuestas a las preguntas 2.1–2.5.
- [ ] Revisión final del Markdown con todos los resultados y limitaciones reales.
- [ ] Videos de trayectoria y mapeo en tiempo real, con pantalla dividida.
- [ ] Dos mapas PGM y sus YAML comprobados.

El Markdown debe responder:
1. Diferencias entre modelos cinemáticos diferencial y omnidireccional.
2. Ventajas de ambos modelos.
3. Propuesta de aplicación del modelo omnidireccional.
4. Implementación de esa propuesta en Ecuador.
5. Recomendaciones.

El usuario también solicitó código LaTeX con una redacción natural. Se preparará
al terminar las pruebas, como complemento: no sustituye el Markdown solicitado
por el docente. No se exige un PDF en la consigna compartida.

## Procedencia y evidencias

La base es el repositorio del docente: https://github.com/davatorr1009/workshop_03.
Se conserva su procedencia en el informe. Las imágenes de referencia de src/ no
se consideran evidencias de nuestras ejecuciones. Los intentos incompletos o
fallidos deben distinguirse de las pruebas válidas.
