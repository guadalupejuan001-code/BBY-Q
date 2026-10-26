# BBY Q E003 - aprendizaje nativo en el espacio Ether

## Por qué cambia la arquitectura

E001/E002 calculaban hipótesis en Python y guardaban un objeto JSON/BQL2
dentro de Inverse Ether Memory. Eso demostraba persistencia, pero el espacio
era principalmente un transporte de resultados. E003 introduce un operador
nativo propio de BBY Q que **lee, interpreta y transforma relaciones desde
las direcciones lógicas de la QuantumRuntime existente**. No usa SOVENGI,
Transformers, modelos de terceros, qubits automáticos ni motor paralelo.

El cálculo de activaciones y errores **está implementado en C++ de BBY Q**;
Ether no contenía previamente aprendizaje semántico. Sigue ejecutándose
en CPU clásica. Es un prototipo de operador de aprendizaje en el espacio,
no una prueba de inteligencia general o ventaja cuántica.

## La representación es el espacio

Solo existe una autoridad persistente: el archivo RVPC2 de REVERSE-PC,
cuyo estado es Inverse Ether Memory más el núcleo integrado.

- Base decimal lógica: 7000000000000000000.
- Base+0, +1 y +2: firma de entidad espacial 66, 81, 3.
- Base+8..11: contador de experiencias (32 bits little endian).
- Base+64..68: cinco relaciones ponderadas de un byte con signo.
- Fondo global cero: ninguna relación vacía ocupa una celda particular,
  ni se crea un qubit por byte.

Las plantillas iniciales son bias, signal, pressure, action y
signal_action. Son **relaciones que reciben evidencia**, no respuestas
a cada combinación de entradas. Las cinco plantillas están fijadas para
este microentorno: descubrir relaciones nuevas sigue siendo investigación.

La inferencia consulta cinco direcciones lógicas mediante InverseMemory.read
y combina sus activaciones. Después de observar la consecuencia, solo
cuando una predicción es errónea, actualiza los pesos relacionados con
el error, acotados a [-48,48]. Los cambios de relaciones y contador
se ejecutan en **una transacción XI de la misma QuantumRuntime**.
No se conserva un dict Python ni un archivo lateral de pesos.

## Seguridad, autoridad y procedencia

Se usa REVERSE-PC fijado en 063d871c27de2d4f10904ec5c3e1363c2fe16d86,
cuya dependencia verificada es Mundo X
e2778d962af22f6f1a0794058dd4685fc2573966. No se modifican los
repositorios de origen. El encuadre RVPC2 de BBY Q es interoperable con
el ejecutable original reverse_pc; reproduce solo los bytes de transporte,
**no otro motor de estado**. FNV-1a detecta corrupción accidental pero no
autentica datos adversarios.

E003 rechaza archivos E001/E002 sin su firma espacial. Durante las pruebas
cada variante reside en su propio RVPC2: no son dos autoridades del mismo
agente. Se mantiene el bloqueo exclusivo en el mismo archivo .lock.

La interfaz nativa:

- new ARCHIVO: nacimiento, no sobrescribe un archivo existente.
- predict ARCHIVO señal presión acción: lectura sin modificación.
- learn ARCHIVO señal presión acción resultado: actualiza y guarda RVPC2.
- inspect ARCHIVO: relaciones, contador, qubits, enlaces y tamaño.
- session ARCHIVO: recibe líneas L señal presión acción resultado y
  P señal presión acción. Solo confirma al final; ante cualquier error
  se descarta el lote y no se emiten respuestas prematuras.

## Compilación reproducible

Preparar el REVERSE-PC anterior siguiendo su README y scripts/setup-ether.sh,
compilar el ejecutable reverse_pc y reutilizar exactamente su overlay Ether:

    g++ -std=c++17 -O2 -Wall -Wextra -pthread \
      -DREVERSE_PC_HAVE_BOUNDED_PRODUCT_IMPORT=1 \
      -I /path/REVERSE-PC/build/ether-compat \
      -I /path/REVERSE-PC/src \
      -I /path/REVERSE-PC/deps/mundo-x/native/include \
      ai/native/ether_relations.cpp -o bbyq-space
    ./bbyq-space new entity.rvp
    ./bbyq-space predict entity.rvp 0.3 -0.4 1
    ./bbyq-space learn entity.rvp 0.3 -0.4 1 0
    ./bbyq-space inspect entity.rvp
    BBYQ_SPATIAL_BINARY=./bbyq-space PYTHONPATH=ai python ai/bench/spatial_campaign.py

El workflow bbyq-spatial.yml compila contra la dependencia fijada y
ejecuta pruebas sobre REVERSE-PC real.

## Comparación y posibles refutaciones

Cinco semillas 42..46; 400 experiencias de entrenamiento; 240 observaciones
nuevas por semilla; acciones alternadas. El entorno world.py oculta los
coeficientes; estos nunca pasan al agente. El conjunto holdout es disjunto
y sus predicciones no modifican el estado. El baseline es el mismo aprendiz
sin entrenamiento (hipótesis de fondo cero). Se registra un control negativo
con paridad/XOR no lineal en las mismas semillas.

Métricas: precisión, errores, qubits, enlaces, excepciones, bytes RVPC2,
duración de lote incluyendo commit, reinicio, corrupción, atomicidad y
lectura del mismo RVPC2 por la CLI original REVERSE-PC.

Esta fase no recupera todavía contextos aprendidos como E002 ni descubre
sus propios operadores generales. La próxima investigación es crecimiento
de relaciones por evidencia y reorganización con rollback y retención.
