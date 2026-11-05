# E02 — un ciclo común para BBY Q

E01 conservaba una sesión y dirigía cada solicitud a un especialista. E02 añade
una tarea persistente con evidencia común, dependencias entre componentes,
verificación de la respuesta y evaluación con aprendizaje transaccional.

La misión utiliza una regla binaria guardada y 1.000 valores numéricos.
QMemory recupera la regla; VQC3 clasifica las observaciones; XI deduce un destino
0/6 mediante clase XOR regla; QRL3 propone un paso desde una posición 0–6;
una cabeza de QChat100 aprende a expresar la acción propuesta. XI verifica que
la frase coincida con la acción. Si falta una premisa, pide información.
La regla de la tarea no elige la acción del actor QRL.

Los componentes tienen parámetros propios y un espacio de trabajo compartido.
Consumen el resultado del componente anterior y responden al resultado de una
misma tarea. No equivalen a una red diferenciable única ni a razonamiento general
en lenguaje libre. Las demás capacidades X10 conservan sus rutas y sus turnos
se registran en el mismo diario de la entidad.

## Prueba reservada y controles

El protocolo se registró en `2d9a701f` antes de entrenar. Dos candidatos iniciales
fallaron la validación. El refinamiento elimina datos irrelevantes del
verbalizador y evita castigar al actor cuando una premisa anterior era errónea.
El candidato refinado obtuvo 52/56 tareas y 56/56 frases en validación; después
se congeló y se abrió la prueba final. No se cambió la selección con esa prueba.

| Condición, mismas 112 tareas reservadas | Correctas |
| --- | ---: |
| Entidad completa | 106/112 |
| Memoria borrada | 59/112 |
| Observables de VQC anulados | 51/112 |
| Planificador sustituido por azar | 70/112 |
| Observables del verbalizador anulados | 0/112 |
| Coordinador congelado al comenzar el refinamiento | 106/112 |

La última fila conserva 252 episodios anteriores del coordinador. La continuación
mejora Brier de 0,05985 a 0,05180; no mejora la exactitud en esa comparación.
Una prueba independiente de retroalimentación comprueba que modificar el
aprendizaje común puede cambiar una decisión posterior a abstención. Los
controles demuestran dependencias del sistema y calibración. No demuestran
ventaja cuántica; los circuitos se ejecutan en simulación clásica.

El verbalizador acierta 112/112 acciones y todas las premisas ausentes provocan
abstención. Extiende los 75 tokens originales con cinco palabras y aprende
cuatro frases cortas. La cabeza conversacional E01 se conserva aparte.
La comprobación adicional de retención conserva los pisos E01: VQC 122/128 IID
y 122/128 OOD; QRL 40/42 pares, 31/32 y 32/32 episodios.

## Aprendizaje común

La campaña usa una observación, regla y resultado comunes para entrenar
percepción, actor, memoria y voz. El coordinador aprende la probabilidad del
éxito común. VQC usa una etiqueta verificada; el actor recibe crédito solo con
premisas correctas; la memoria practica escritura/lectura de la regla; la voz
recibe como objetivo la acción efectivamente propuesta. Los gradientes,
circuitos, inferencias y verificaciones se ejecutan en XI. Python y Java
transportan datos y controlan archivos o transacciones.

| Modelo | Contador aceptado |
| --- | ---: |
| VQC3 | 11.932 ejemplos |
| QRL3 | 11.885 episodios/actualizaciones de política |
| QMemory | 42 actualizaciones cuánticas |
| QChat100, cabeza de acciones | 78.860 actualizaciones |
| Coordinador compartido | 504 evaluaciones aprendidas |

En Android se puede evaluar una tarea una sola vez. El resultado actualiza el
coordinador. Si fue una muestra sintética y existe una regla que el usuario
enseñó explícitamente, sus objetivos verificables permiten actualizar también
los especialistas. Para datos externos, se pueden proporcionar `clase` y `regla`
como corrección supervisada. No se reciclan predicciones como etiquetas.
El actor terminal o con una premisa errónea no recibe un gradiente injustificado.

Los objetivos de memoria del usuario se conservan en un diario de supervisión
separado que solo se consulta al aprender. La inferencia lee QMemory. La
actualización de sus ángulos se calcula en una copia; las asociaciones
existentes permanecen intactas.

Cada tarea conserva entrada, traza, workspace, objetivo disponible y SHA-256.
La evaluación restaura el contexto de esa tarea, conserva los pesos y contadores
actuales y confirma cambios y comprobantes en una sola transacción. Un reintento
no aprende dos veces; evidencia alterada o un fallo revierten la operación.
E01 y los estados anteriores se conservan. Los agentes V3 con entrenamiento
personal mantienen sus parámetros al migrar.

## Uso

En Android: enseñar una asociación, abrir «Resolver una misión» y evaluar con
«Evaluar última tarea». El diálogo identifica el ejemplo como sintético. El
nombre BBY Q se conserva hasta que X decida el nuevo nombre.

```text
memoria guarda faro 1
mision {"memoria":"faro","posicion":3,"muestra":620511}
evaluar {"tarea":"ID_DEVUELTO","resultado":1}
```

`datos` puede sustituir a `muestra` con exactamente 1.000 números finitos.
No se admiten ambas fuentes juntas. Las muestras sintéticas son un entorno
de prueba; no sensores del teléfono ni navegación física.

```sh
python3 integration/entity/verify.py
python3 integration/entity/train.py --output build/nueva-campana
python3 integration/entity/train.py --output build/refinamiento-nuevo --refine-from RUTA_BASE_252
```

La siguiente campaña requiere tareas y pruebas reservadas nuevas: la prueba
E02 ya se abrió. Faltan razonamiento y transferencia más amplios, lenguaje rico,
planes largos y conocimiento compartido entre dominios. Este ciclo ofrece una
base concreta para medir esos avances.
