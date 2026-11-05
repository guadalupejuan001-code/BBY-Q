# E01 — base de equilibrio de BBY Q

Protocolo registrado en `95bf0526` antes de la campaña. Selección por validación;
prueba final abierta después de congelar candidatos. Los cuatro componentes
cumplen los pisos definidos para sus tareas actuales. No se calcula un
porcentaje de inteligencia general.

| Componente y prueba | Antes | E01 |
| --- | --- | --- |
| VQC3, clasificación IID (256 casos) | 97.66% | 97.66% |
| VQC3, clasificación OOD (256 casos) | 97.66% | 96.48% |
| QRL3, dirección en 42 pares distintos | 33/42 | 40/42 |
| QRL3, trayectorias nuevas con destinos variados | 72/84 | 81/84 |
| QChat100, respuestas exactas (103 entradas) | 71/103 | 95/103 |
| QMemory, asociaciones binarias reservadas | 3000/3000 | 3000/3000 |
| QMemory, error cuadrático de lectura | 0.0012548 | 0.0001012 |

VQC3 mantiene su resultado IID y reduce ligeramente el error Brier de ambas
muestras; su exactitud OOD baja 1,17 puntos. Ese retroceso se conserva en la
evidencia y está dentro del máximo de dos puntos registrado. No se escogió
otro modelo después de examinar la prueba final.

QChat100 necesitó tres variantes de codificación. Las dos primeras mejoraron
la abstención pero fallaron los pisos de lenguaje; se descartaron. El candidato
aceptado filtra palabras funcionales genéricas antes del mismo circuito y
aprende sus respuestas mediante SGD en XI. Conserva el 94,83% del currículo
original. En prueba responde correctamente 36/42 entradas con vectores de
características no vistos durante el entrenamiento; las otras entradas pueden
compartir vectores con frases practicadas. No es conversación general.

Los estados cuánticos Clifford de QChat100 siguen siendo exactos; sus pesos
aprendidos usan aritmética binary64. El control analítico produce las mismas
respuestas. El control clásico de memoria también resuelve la tarea binaria.
Estas pruebas no demuestran ventaja cuántica.

## Modelos y reanudación

VQC3 conserva 1.000 cúbits simulados y pasa a 11.500 episodios. QRL3 conserva
1.000 y pasa a 11.512. QChat100 conserva 100 cúbits y suma 74.660 actualizaciones.
QMemory conserva 1.000 cúbits y continúa 20 actualizaciones de sus puertas
sobre el modelo previo. Se conservan los originales y los modelos de cada
familia; E01 está en `integration/balance/release`.

```sh
node bbyq.mjs quantum balanced status
node bbyq.mjs quantum balanced ask 'qué es memoria'
node bbyq.mjs quantum balanced act 3 6
python3 integration/balance/verify.py
```

Los comandos históricos conservan sus perfiles anteriores. El perfil E01 y la
APK 2.1 usan los modelos seleccionados. La APK archiva modelos anteriores,
conserva lecciones e historial y aplica nuevos ángulos sin borrar asociaciones
binarias existentes. Un agente V3 que haya recibido entrenamiento adicional
en el teléfono conserva sus parámetros personales; los contadores muestran
qué modelo está activo. Las identidades desconocidas y la corrupción detienen
la migración y revierten toda la transacción.

En Android, XI admite el contexto de QChat solo para las formas de seguimiento
de su currículo. El generador conserva su propio antecedente durante un máximo
de 32 turnos; las órdenes de memoria y de V3 no lo sustituyen. Ese antecedente
se guarda en la misma transacción y se elimina al vaciar el contexto breve.

La siguiente etapa necesita conocimiento y tareas más amplios, transferencia
a problemas nuevos y mejor comprensión contextual. La base presente permite
medir esos avances sin confundir pruebas de integración con inteligencia.
