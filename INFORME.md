# Workshop 3: modelo omnidireccional y mapeo

Integrantes: Jhon Frank Caicedo Coronel, Raziel Alejandro Espinoza Vargas y Luis Fernando Velez Burgos.
Iniciales utilizadas: J, R y L.

## 2.1 Diferencias entre modelos cinemáticos

Un robot diferencial ideal tiene dos velocidades de control: avance y giro. En su marco corporal, la velocidad lateral es cero; para alcanzar una posición a su costado debe combinar traslación y rotación. Esta restricción es no holonómica. Sus velocidades dependen del radio de rueda y de la distancia entre ruedas.

El robot omnidireccional con cuatro ruedas mecanum a 45 grados puede controlar avance, desplazamiento lateral y giro de manera independiente bajo el modelo ideal. Los rodillos permiten generar componentes laterales de movimiento. Cada velocidad de rueda combina las tres velocidades del chasis; los signos dependen de la disposición de los rodillos y del orden de las ruedas. En esta implementación se usa FL, FR, RL, RR y las convenciones del Dingo-O del taller.

## 2.2 Ventajas de cada modelo

| Criterio | Diferencial | Mecanum |
|---|---|---|
| Mecánica y mantenimiento | Menos actuadores y mecánica más sencilla | Cuatro actuadores y rodillos que requieren mantenimiento |
| Maniobras | Puede girar sobre sí mismo; requiere maniobras para trasladarse lateralmente | Se desplaza lateralmente sin cambiar orientación |
| Control ideal | Modelo de menor dimensión | Permite controlar simultáneamente x, y y orientación |
| Superficie | Las ruedas convencionales suelen tolerar mejor irregularidades | Adecuado para pisos firmes, lisos y nivelados |
| Odometría | Acumula error por deslizamiento y parámetros incorrectos | También acumula error; la interacción de rodillos añade sensibilidad al deslizamiento |

La selección depende del entorno. La omnidireccionalidad no implica automáticamente mayor precisión, eficiencia ni capacidad de carga.

## 2.3 Propuesta de aplicación

Se propone un robot para transportar insumos entre recepción, almacenamiento y estaciones de trabajo de una clínica. El desplazamiento lateral facilita aproximarse a un mostrador y alinear una bandeja manteniendo su orientación. Se utilizaría lidar para construir el mapa, localización sobre ese mapa y planificación de rutas. La carga debería fijarse y el diseño incluir detección de obstáculos, parada de emergencia y límites de velocidad.

## 2.4 Implementación en Ecuador

Como propuesta de piloto, se seleccionaría una clínica de Quito, Guayaquil o Cuenca con rutas interiores de piso nivelado. Primero se medirían puertas, pendientes y espacio de giro, y se identificarían trayectos frecuentes de bajo riesgo. Luego se construiría el mapa y se probaría el transporte de cargas inertes fuera del horario de atención. La siguiente etapa sería una operación supervisada en un área delimitada.

El presupuesto debería considerar repuestos de ruedas y rodillos, baterías, disponibilidad de mantenimiento local y capacitación del personal. Se compararían tiempo de entrega, intervenciones humanas, autonomía y costo por recorrido con el procedimiento actual. La ampliación dependería de resultados medidos, evaluación institucional y requisitos aplicables; no se presupone una implementación ya realizada ni costos verificados.

## 2.5 Recomendaciones

- Comprobar los signos de cada rueda con avance, desplazamiento lateral y giro antes de una trayectoria completa.
- Mantener unidades SI y distinguir marco corporal, marco inicial, mundo y mapa.
- Reiniciar la simulación entre trayectorias para conservar la posición inicial y margen a las paredes.
- Recorrer lentamente los entornos al mapear y volver a zonas conocidas para favorecer cierres de lazo.
- Conservar juntos cada PGM y su YAML, que contiene resolución, origen y umbrales.
- No confundir odometría con posición verdadera. En este trabajo la referencia de posición es Gazebo, no una medición de hardware físico.
- El controlador implementado es cinemático de lazo abierto: transforma velocidades deseadas sin corregir el error de pose. Como mejora futura se propone realimentación y perfiles suaves de velocidad.

## Implementación y procedencia

Base: [repositorio del profesor](https://github.com/davatorr1009/workshop_03), conservado en `src/`. Los nodos ROS, lanzadores, mundos, integración de odometría y visualización provienen de esa base. Se implementaron las transformaciones y cinemáticas directa/inversa en `kinematics.py`, se conectaron al controlador y al cálculo de odometría, se añadieron `prueba_omni` y `JRL`, y se extendió la exportación con CSV y métricas JSON.

El modelo usa r = 0.05 m, lx = 0.285 m y ly = 0.1854 m. La trayectoria JRL mantiene la orientación del chasis y combina rectas y arcos. Incluye el acceso inicial, conexiones y algunos trazos recorridos dos veces: un robot que permanece en el suelo no puede levantar un lápiz entre letras.

## Comparación experimental: completar después de ejecutar

Estado: código preparado y pruebas numéricas locales; pendiente validación en ROS/Gazebo. No se han generado mapas ni grabado videos en esta preparación.

En RViz: blanco = deseada, azul = posición de Gazebo, naranja = odometría. En el PNG la referencia se dibuja negra discontinua. Los CSV contienen tiempo y coordenadas de las tres curvas. Los JSON resumen RMSE, error máximo y error final de posición, calculados sobre las muestras registradas. Las poses disponibles se emparejan al recibir la referencia, por lo que hay latencia de muestreo; no se hace sincronización exacta de sensores.

| Ejecución | RMSE Gazebo–referencia [m] | RMSE odometría–referencia [m] | RMSE odometría–Gazebo [m] |
|---|---|---|---|
| prueba_omni | Pendiente | Pendiente | Pendiente |
| JRL | Pendiente | Pendiente | Pendiente |

Después de ejecutar, copiar los valores de los JSON y comentar en qué tramos aumenta el error. Una separación entre odometría y Gazebo puede ser compatible con deslizamiento, errores de integración y latencias; la gráfica por sí sola no identifica una causa única.

Mapas previstos: `office_0` (11 × 9.75 m) y `office_4` (32 × 18.15 m), según el repositorio. Registrar áreas no exploradas y limitaciones observadas. Adjuntar las evidencias reales antes de entregar.
