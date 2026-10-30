# X03: P01 diálogo con fuentes y P04 contexto de documentos

Este ciclo añade diálogo acotado, seguimiento de una fuente y búsqueda de texto
guardado sobre X02. La interpretación, el índice, el cálculo de coincidencias,
la decisión de responder y los bytes de respuesta se ejecutan en XI. Los scripts
Node ensamblan código o transportan bytes; no eligen una respuesta.

## P01: conversación que conserva su referencia

```
Estoy frustrado porque no entiendo mi código.
Me cuesta entender las funciones.
Explícame qué significa velario.
no entendí
dame un ejemplo
¿de dónde lo sabes?
```

Las primeras formas aceptan un tema nuevo y solicitan un ejemplo concreto cuando
no hay una explicación respaldada. Si encuentran contexto, muestran su fuente.
Los seguimientos conservan una referencia al texto, no una copia de la respuesta.
Pedir un ejemplo requiere que exista un ejemplo explícito en la fuente; si no
aparece, BBY Q lo dice. Una pregunta nueva sin evidencia o un borrado de contexto
invalida la referencia anterior.

`curriculum.json` declara dos entradas enseñadas: una definición de «aprender» y
un ejemplo. Se guardan en el mismo estado Ether, fuera del archivo de documentos.
No son una demostración de generación libre. Las otras definiciones y los datos
de los exámenes llegan mediante mensajes y documentos nuevos.

La conversación sigue limitada a las formas descritas. No se presenta como
conversación abierta comparable con un modelo generativo general ni como una
capacidad de reformular cualquier explicación. Una cita de un fragmento conserva
la información de la fuente; no demuestra comprensión semántica irrestricta.

## P04: datos de textos largos, con procedencia

Se reutiliza el archivo E027 de 512 fragmentos y 114.688 bytes. El texto se guarda
una sola vez. X03 añade títulos y límites de documentos, una correspondencia entre
documento y fragmentos y un cursor de búsqueda. Los fragmentos antiguos sin un
documento explícito se tratan como unidades independientes.

```
Guarda este texto: El taller ficticio tiene una puerta verde.
¿De qué color es la puerta del taller ficticio?
```

Para documentos que superan el buzón de 255 bytes se usa un flujo nativo:

```
@doc begin Informe de ensayo
@doc append <hasta 224 bytes UTF-8>
@doc append <otros bytes del mismo documento>
@doc end
```

`@doc abort` descarta únicamente el documento abierto. Mientras está abierto,
se rechazan otras escrituras de archivo y las consultas de ese flujo. El
importador adjunto trabaja sobre una copia y publica un archivo de salida nuevo
solo después de terminar todas las partes; no sobrescribe el archivo de entrada.

La búsqueda usa palabras completas, hasta ocho términos principales, exclusión
de palabras funcionales y comparación de mayúsculas. Cada ventana contiene uno o
dos fragmentos del mismo documento. Requiere al menos el 75 % de los términos
principales y recorre todo el archivo antes de dar una respuesta final. Una
versión distinta con la misma puntuación y sin solaparse produce dos citas y una
petición de aclaración. Una coincidencia parcial dentro de una palabra cortada
por un límite de fragmento no cuenta como palabra completa.

No es búsqueda semántica ni un resumidor: devuelve fragmentos literales con
`[#NNN]`, posiblemente un intervalo de dos fragmentos. Puede rechazar sinónimos
o no hallar una relación que abarque más texto que su ventana. La mayor prueba
de documento de este ciclo usa 13.760 bytes y 62 fragmentos; el límite de archivo
de 114.688 bytes procede del almacenamiento existente, no de una prueba nueva
de comprensión sobre todo ese tamaño.

## Trabajo por pasos, sin modificar el runtime

Se conservan el intérprete y su presupuesto de un millón de instrucciones por
ejecución. Una búsqueda procesa cuatro ventanas por paso. Si falta trabajo,
queda un cursor explícito y se responde con un estado pendiente. `@read next`
continúa y `@read cancel` cancela. Otro mensaje cancela una búsqueda pendiente;
no se reutiliza un resultado parcial como respuesta final.

`ask.mjs` coordina las continuaciones leyendo solo ese estado de control. La
selección de texto sigue siendo XI. Las respuestas normalizan los saltos de línea
del fragmento a espacios para conservar compatibilidad con el adaptador de
cápsulas; el archivo guardado conserva sus bytes originales. No se arregló ni se
amplió el transporte general de entrada, y no se modificó C++.

## Construcción y uso

Padre: X02, cápsula SHA-256
`910ec3d796abdbc3b6d99e690766f49b4c0b3430165c1dcda027932227b287c7`.
Desde la raíz del proyecto:

```
node ai/personal/x03/build.mjs /ruta/reverse_pc /ruta/build-x02 /ruta/build-x03-nuevo
node ai/personal/x03/import.mjs /ruta/reverse_pc /ruta/build-x03 entrada.rvp nueva-con-texto.rvp "Informe" texto.txt
node ai/personal/x03/ask.mjs /ruta/reverse_pc /ruta/build-x03 nueva-con-texto.rvp nueva-respuesta.rvp "¿Cuál es el código del módulo zafiro?"
```

Ambos auxiliares exigen un archivo de salida nuevo. Solo aceptan texto UTF-8;
el importador conserva saltos de línea y no parte un carácter entre mensajes.
No interpreta títulos o texto como órdenes ejecutables.

Para migrar una copia de E038/X01/X02:

```
node ai/personal/x03/migrate.mjs /ruta/reverse_pc /ruta/build-x03 entrada.rvp nueva-x03.rvp
```

Una memoria anterior a X02 usa dos programas XI sucesivos sobre la copia. La
salida se publica cuando ambos terminan. La migración monolítica desde E038
superaba el presupuesto original y se descartó; no se elevó el presupuesto para
ocultarlo. Una memoria X02 compatible puede usar directamente `upgrade.xi`.
Los espacios ocupados por otros datos provocan rechazo sin publicar una memoria.

Los exámenes históricos derivados conservan sus aserciones. Se adaptan los hashes
de versión, la comparación con las regiones nuevas y, para el antiguo E038, la
llamada al migrador por fases. Los exámenes originales permanecen intactos.

Runtime REVERSE-PC `a1b935ae0adf38615996bac92727e95289ad7cc1`, Mundo X
`e2778d962af22f6f1a0794058dd4685fc2573966`. No se cambió el runtime, no se publicó
código y no se actualizó una APK ni una memoria personal real.
