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
