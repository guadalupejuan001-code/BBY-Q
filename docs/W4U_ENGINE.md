# W4u 0.1 — work for u

**W4u es el motor de trabajo; BBY Q es la interfaz conversacional.**
REVERSE-PC es el anfitrión que observa ventanas y ejecuta programas internos.
El lenguaje aprendido E022 y su checkpoint continúan intactos. Esta entrega
añade un motor cooperativo acotado; no entrena un modelo general ni reproduce
las capacidades de Astra.

## Tres roles propios en XI

- `plan.xi`: registra el objetivo recibido y empieza un episodio nuevo.
- `explore.xi`: propone una ruta directa o abrir una ventana como prerrequisito.
- `verify.xi`: comprueba de forma independiente el plan completo, su relación
  con el objetivo, las capacidades y las precondiciones del paso actual.
- `advance.xi`: comprueba el resultado observado y permite verificar el paso
  siguiente. Una confirmación positiva sin la ventana esperada se rechaza.

Cada rol tiene registros propios dentro de **un RVPC2 compartido entre los
roles de W4u y BBY Q**. Se ejecutan secuencialmente. Son módulos simbólicos
diseñados, con una búsqueda de dos rutas y planes de hasta dos pasos; no son
copias independientes de un modelo de lenguaje ni agentes paralelos.
Java/JavaScript transportan datos y aplican operaciones tipadas. No interpretan
las órdenes ni sustituyen los algoritmos XI.

## Contrato para otras interfaces

La interfaz entrega un objetivo tipado en `A=8200000000000000000`:
`+64` operación, `+65` destino, `+67=1` intención admitida. Antes de planificar
entrega observaciones frescas: `+16` conexión, `+17` herramienta activa,
`+18` número de ventanas, `+32..63` cantidades por destino.

La región del motor es `M=8300000000000000000`:

| Registros | Significado |
|---|---|
| `+0=77`, `+1=1` | Identidad y versión del contrato |
| `+16` | 0 inactivo, 1 propuesto, 2 pendiente, 3 completo, 4 detenido |
| `+17..20` | Objetivo, destino, longitud del plan, pasos completados |
| `+32..34` | Resultado del planificador, explorador y verificador |
| `+80` | Confirmación tipada del anfitrión, 0 fallo / 1 éxito |
| `+128..131` | Dos pares operación/destino |
| `+512..543` | Capacidad por destino: 0 ausente, 1 abrir, 2 ejecutar RXE |
| `+640..671`, `+672..703` | Ventanas minimizadas y maximizadas por destino |
| `+710`, `+711` | Espacio actual y número total de ventanas minimizadas |

Operaciones: 1 abrir, 2 enfocar, 3 minimizar, 4 maximizar, 5 restaurar,
6 cerrar, 7 ordenar, 8 escritorio, 9 espacio, 10 ejecutar RXE.
Los destinos 1..10 son herramientas del escritorio, 13/14 espacios, 15 ventana
activa y 16..31 programas vinculados al catálogo de esa observación.

Un anfitrión llama a `plan`, `explore` y `verify` para obtener una acción en
`A+64/+65`. Después de ejecutarla suministra una observación nueva y llama a
`advance` y `verify`. La integración REVERSE compila también `W4u.rxe` para
consumidores de este contrato y enlaza los mismos módulos en `BBY-Q.rxe`.

La verificación observa apertura, enfoque, minimización, maximización, cierre,
restauración y cambio de espacio. La ejecución RXE, ordenar ventanas y las
operaciones sobre «esta ventana» utilizan el resultado tipado del anfitrión;
W4u no inspecciona visualmente la pantalla ni demuestra la corrección semántica
de un programa arbitrario.

## Uso desde BBY Q en REVERSE

- `maximiza calculadora`: si falta, abrir y después maximizar.
- `ejecuta programa 1` / `run program 1`: abrir si hace falta y ejecutar el RXE
  dentro del runtime nativo de REVERSE-PC.
- `abre programa 1`: abrir su ventana sin ejecutarlo.

Los números aparecen en Aplicaciones. Se vinculan a ruta e identidad exacta
del ejecutable y pueden cambiar al modificar el catálogo. Hasta 16 programas
se exponen en esta primera versión. Las aplicaciones conversacionales pueden
abrirse, pero no reciben la capacidad de ejecución directa.
El programa trabaja sobre el estado del escritorio anfitrión; la memoria privada
conversacional de BBY Q/W4u conserva su autoridad separada.

El anfitrión vuelve a comprobar el catálogo nativo, liga cada acción a la vista,
consume tickets y guarda el episodio antes de devolverlo. Reabrir una ventana
o reiniciar nunca despacha un plan guardado. Si se pierde una confirmación no
se repite automáticamente un programa que pudiera haberse ejecutado.

## Prueba del motor sin interfaz ni lenguaje

```bash
node ai/xi/w4u/tests/native-w4u.mjs /ruta/reverse_pc /ruta/evidencia-w4u
```

Las pruebas se ejecutan en el runtime XI real: planes con prerrequisitos,
ejecución con capacidades, observaciones que contradicen una confirmación,
propuestas corruptas, ventanas ambiguas, falta de conexión y fallos.
Las observaciones de este examen son fixtures. La integración y el RXE interno
se prueban adicionalmente en el repositorio REVERSE-PC.
