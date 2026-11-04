# QChat100: primer generador de conversación entrenado en XI

El modelo predice una palabra cada vez a partir de la pregunta, el contexto
anterior y las palabras ya producidas. La inferencia no consulta una tabla de
respuestas ni usa el chat X08 como sustituto. Se conserva el resto de BBY Q.

## Qué se entrenó

Se utiliza el registro GHZ de 100 cúbits del CompactCore original. La pregunta
y el prefijo generado se codifican con puertas Clifford. Se leen 99
correlaciones ZZ y la coherencia X de los 100 sitios. Esas 100 lecturas exactas
alimentan 768 productos clásicos y un árbol de salida de profundidad 7.

El árbol aprende mediante SGD binario64 implementado en XI. El circuito de
características es fijo; los parámetros entrenados son los pesos de salida.
Por tanto, la exactitud algebraica corresponde al estado cuántico y sus
puertas Clifford. No se atribuye exactitud matemática a los pesos decimales.
Python/Node tokenizan, transportan datos y registran resultados; no calculan
las predicciones ni las actualizaciones del optimizador.

La versión inicial tiene 75 tokens de salida y conocimiento limitado al corpus
incluido. Aprende saludos, identidad y definiciones breves del proyecto. Puede
fallar en preguntas y continuaciones nuevas; no es un modelo general de lenguaje.
Los resultados completos, incluidos errores, están en `release/training-report.json`.

La implementación analítica equivalente produce las mismas respuestas. Esta
entrega demuestra entrenamiento e inferencia ejecutables sobre los 100 cúbits,
no una ventaja de aprendizaje cuántico ni superioridad frente a X08.

## Conversar

```sh
node bbyq.mjs quantum qchat100 prepare NUEVA_SESION --runtime=/ruta/REVERSE-PC
node bbyq.mjs quantum qchat100 turn NUEVA_SESION mensaje-1 hola
node bbyq.mjs quantum qchat100 ask NUEVA_SESION 'quien eres'
node bbyq.mjs quantum qchat100 status NUEVA_SESION
```

`turn` guarda el historial y evita repetir una solicitud con el mismo ID.
`ask` realiza una consulta sin publicar cambios. Los pesos del checkpoint
permanecen inmutables durante la conversación. Un seguimiento explícito como
“dime más” transmite la última pregunta temática como contexto al modelo.

## Reproducir el entrenamiento o continuarlo

```sh
python3 integration/qchat100/train.py --runtime=/ruta/REVERSE-PC --output=NUEVO_ENTRENAMIENTO --epochs=60 --corpus=integration/qchat100/release/training-corpus.json --history-policy=all
python3 integration/qchat100/train.py --runtime=/ruta/REVERSE-PC --output=OTRA_VERSION --epochs=10 --initial=NUEVO_ENTRENAMIENTO/trained.rvp --corpus=MIS_EJEMPLOS.json
```

El corpus JSON separa `train`, `heldout` y, opcionalmente, `fresh_questions`.
Cada fila contiene `input`, `response` y `previous`. Las palabras nuevas se
añaden conservando sus IDs anteriores, hasta 128 entradas en este árbol.
Para continuar sin olvidar temas, incluir ejemplos anteriores como repaso.
La salida requiere una carpeta vacía y no sustituye los modelos existentes.

El modelo es independiente de la APK Android 1.0, que conserva su motor anterior.
