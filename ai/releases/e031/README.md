# E031: biblioteca léxica completa de las fuentes ES/EN fijadas
Solicitud: cargar ampliamente diccionario español e inglés. La instrucción nueva
del usuario sustituye el objetivo pendiente de reconciliar fuentes.
El léxico sellado antiguo admite 512 entradas: no se rellena ni sobrescribe.
Se incorpora una biblioteca consultable con datos completos de WordNet/MCR en
omwn/omw-data 406bf83b3c507a3d1f26e88252d5d66893fd36bf.
Conservar todas las acepciones, variantes y enlaces bilingües de esas fuentes.
No es todo el vocabulario existente de ambos idiomas ni un modelo preentrenado.

XI recibe @lex PALABRA, normaliza mayúsculas ASCII, calcula la página de datos,
compara la palabra completa UTF-8 y emite sus acepciones y equivalencias.
El anfitrión transporta la página completa solicitada por XI, sin buscar
palabras ni elegir respuestas. Los datos se preparan con Python y se alojan
en páginas de referencia externas; solo una página reside en el mismo RVPC2
del agente, región 8700000000000000000. Semilla, conocimientos y patrones
E030 conservados. Esto evita llenar el límite 524288 de excepciones o el
contenedor de 32 MiB del ejecutor configurado.

Es adquisición de referencia léxica; aún no induce razonamiento o gramática
desde definiciones ni incorpora automáticamente estas entradas en la
conversación general. Las glosas inglesas no se etiquetan como definiciones
españolas; donde la fuente no aporta glosas españolas se mantiene su ausencia.
No hay IA externa, inferencia Python o sustitución del motor XI.

## Reproducir y consultar
```sh
python3 ai/releases/e031/import_and_test.py deps/reverse/build/reverse_pc deps/omw evidence/dictionary
python3 ai/releases/e031/query.py deps/reverse/build/reverse_pc evidence/dictionary evidence/dictionary/dictionary-checkpoint.rvp es perro
python3 ai/releases/e031/query.py deps/reverse/build/reverse_pc evidence/dictionary evidence/dictionary/dictionary-checkpoint.rvp en dog
```
Consulta explícita con transporte de páginas; abrir solo la cápsula sin ese
transporte no instala los datos externos. El paquete de evidencias incluye
bancos binarios, diccionario comprimido completo, cápsula, checkpoint y licencias.
Fuente inglesa: Princeton WordNet, licencia WordNet.
Fuente española: MCR, CC BY 3.0; ver LICENSE de cada fuente en el paquete.
Resultados solo se declaran después de CI.

## Resultados comprobados
CI https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40793126384, código `e194d56096daf935caae33c7a9db0a130bc0fcec`:
88.950 entradas ES + 147.306 EN = **236.256**. La fuente española aporta
19.444 glosas (registros de definición) y las glosas inglesas provienen de los
archivos originales PWN 3.0, copia de datos `nltk/wordnet` fijada en
`ce91915ae38a341ae845be4d825ef6003cddf395`; no se importa ni ejecuta su motor Python.

152/152 consultas exactas, 24 Unicode, 75 expresiones de varias palabras;
158 controles totales. E025 original/candidato 31 cada uno y W4u 21 aprobados.
Se preservaron patrones E030 y el checkpoint original. No hubo entrenamiento
de comprensión ni razonamiento general nuevo.

Paquete completo de 105.628.254 bytes:
https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40793126384/artifacts/12862856143
Incluye bancos binarios, dataset comprimido, cápsula, checkpoint y transcripciones.
SHA256 del dataset comprimido:
`29fa0ef8a9e698a9a4129d5e02bcffca6801998f826a7b63739567b019a14ba4`.
93.442.728 bytes sin comprimir y 39.770.663 comprimidos; máximo de página
16.984 bytes. El transporte mantiene una sola página en RVPC2 para no
sobrescribir la memoria previa. Datos externos son referencia, no otra IA.

Atribución: Princeton WordNet, ed. Christiane Fellbaum (1998), MIT Press.
MCR: Aitor Gonzalez-Agirre, Egoitz Laparra y German Rigau (2012),
*Multilingual Central Repository version 3.0: upgrading a very large lexical
knowledge base*. Licencias originales incluidas en el paquete.
