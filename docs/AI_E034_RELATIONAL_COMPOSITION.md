# E034 — composición de relaciones en XI/Ether

BBY Q mantiene su inteligencia en XI/Ether. Este ciclo añadió aprendizaje de ocho formas y un operador nativo que consulta apertura y ubicación del mismo taller, comprueba ambas evidencias y responde con dos referencias. No requiere un modelo externo ni modifica SOVENGI.

## Resultado comprobado
- 48/48 preguntas compuestas sobre24 entidades reservadas; E033 anterior0/48. El operador E033 sobre los mismos marcos nuevos también0/48.
- 96/96 seguimientos tipados y24 controles de taller/libreta con el mismo texto de nombre.
- 168 consultas relacionales y144 temporales anteriores conservadas sobre el modelo E034 sin reenseñarlas.
- 761 verificaciones propias; reproducción E0331069 como verificación; E027429/E028464/E029285/E025 original31/candidato31/W4u21.
- Ante ausencia o conflicto en cualquiera de las propiedades, abstención sin mostrar media respuesta. Correcciones conservan fuentes anteriores y el diario.
- Durante las16 demostraciones nuevas, core, bindings y todas las memorias previas permanecieron exactos. El checkpoint se guardó antes de ingresar los hechos del examen.

## Estados y tamaño
El antecedente contiene dos bytes lógicos (ID internado y tipo), dentro de los bytes12/13 libres del encabezado E033. No copia nombres ni respuestas. El RVPC2 serializa también sus direcciones; dos bytes lógicos no significan dos bytes de crecimiento total del archivo.

| Medida | E033 | E034 |
|---|---:|---:|
| Checkpoint RVPC2 limpio | 856177 bytes | 863594 bytes |
| Checkpoint gzip | 122091 bytes | 123175 bytes |
| Cápsula RXE | 1333231 bytes | 1346841 bytes |
| Marcos relacionales aprendidos | 22 | 30 |

Crecimiento gzip1084bytes (aprox.1,1KB), cápsula13610bytes. Mediana observada163,84ms por consulta compuesta; pico RSS nativo39964KiB en el examen propio. No se afirma aceleración causal, mínimo teórico ni rendimiento Android.

## Qué se aprendió y qué se implementó
El código permanece fijo durante enseñanza/examen. XI induce prefijos/sufijos de las ocho formas nuevas desde dos demostraciones variadas por forma; los roles y los IDs de intención/relación los proporciona el docente. Los testigos iniciales se borran al consolidar cada marco. Historias trama[a-x], combinaciones y valores se fijaron antes de CI y no aparecen en las16 demostraciones nuevas.

Los tipos y el operador de unión están diseñados explícitamente:1=apertura de taller,5=ubicación de taller;2=ubicación de libreta,3=cita,4=baliza. Un nombre compartido es texto internado, no una identidad común a todos los tipos. Cuatro frases de seguimiento (dos españolas y dos inglesas) se implementan explícitamente; no se afirma aprendizaje general de pronombres. Fallos, cambios de tipo y entradas ajenas invalidan la referencia.

El operador todavía solo compone apertura/ubicación de talleres; no genera lenguaje abierto ni une arbitrariamente el archivo E027. Conserva límites32 marcos/96 entidades/96 valores/255 eventos. El orden del diario representa revisión de conocimiento, no tiempo absoluto de ocurrencia.

## Reproducción y evidencia
- Código probado: 7d8d8203d63ba8328d0f2ca6a236f20ae39f87e3, rama feature/bbyq-relational-composition-20261029, PR41 abierto/borrador.
- CI: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40808605984 — completed/success, job123233354332.
- Checkout real de CI (merge efímero): f4f02dbbcaaee8a6110acf397cd845191b9461ee; se identifica aparte del código y las notas.
- Artefacto: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40808605984/artifacts/12869038989, digest sha256:e58c84065c61d7a256c2cc1a7bf033721706df75966c82597ee82e98178cc622, caduca2027-01-27T02:49:15Z.
- Fuente: composition/composed-linked.xi; cápsula: composition/composed.rxe; exámenes: composition/transcripts.json y composition/lessons.json.
- Checkpoint durable: ai/checkpoints/e034/composition-model.rvp.gz.b64, SHA256 RVPC2 876d3f2a82698e9582f17043028d9a75b454e4b5ebaf7cc5949b65a5bac58a10; cápsula compatible a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28.
- Comandos y fallos: docs/autonomy/ejecuciones/composicion-relaciones-20261029-0242.json.

El primer intento fue detenido por la guardia al comprobar que830... pertenecía a W4u; no llegó a aprender. Se corrigió a encabezado840...+12/+13, comprobado libre en fuente y checkpoint. Una segunda revisión no lanzó CI por conflicto de notas; se reconciliaron las referencias antes del run exitoso. No se promovieron estados de los intentos fallidos.

El ejecutor sigue siendo el configurado: GitHub Actions native-e029/ubuntu-latest, REVERSE-PC a1b935ae0adf38615996bac92727e95289ad7cc1 y Mundo X e2778d962af22f6f1a0794058dd4685fc2573966. W4u verifica21 fixtures y una acción tipada[4,2] en el candidato; no se comprobó coordinación autónoma de repositorios ni integración activa en Android.
