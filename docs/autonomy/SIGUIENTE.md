# Siguiente ciclo: composición sobre relaciones compartidas

## Estado real
BBY Q es principal. Principio del usuario: estados mínimos por Ether, aprendizaje e inferencia XI. E033 nativo en PR40, rama feature/bbyq-minimal-relations-20261029, código probado 284172e5b0a7b73ffd75b8fa7676a776fcb5791c. Resolver referencias reales al comenzar; notas y código tienen revisiones separadas. CI https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40802286565 completed/success.

Checkpoint preferido: ai/checkpoints/e033/minimal-model.rvp.gz.b64, RVPC2 SHA256 e61d68b755c741d77c9fcf13f4612fc8df343276ec03f9c981b1c630d7eec433, cápsula compatible SHA256 14334cc91e164ee0299bda3a0a785bd8b0f5e3f41fab744f747d8de1a63dd4f2. E032 anterior permanece en ai/checkpoints/e032/temporal-model.rvp.gz.b64, SHA f1c2ace6a8d35643c0ae68103f3cb0aa33a0325c9fea004f00fd5e38d60ffb56. El modelo E033 solo añade22 marcos aprendidos, sin hechos del examen. Modelo completo856177bytes,122091gzip; crecimiento2836gzip. No sobrescribir memoria privada al restaurarlo.

Código, cápsula, fuentes y transcripciones en https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40802286565/artifacts/12866434141; caducidad del artefacto 2027-01-27T01:45:04Z. El checkpoint durable del repositorio no depende de ese plazo. Si falta el artefacto, reconstruir fuentes con padres/pins fijados; no asumir disponible un binario histórico.

## Comprobado

- 168/168 consultas nuevas con24 entidades y4 relaciones, frente a0/168 en E032 sobre los mismos hechos/preguntas.22 formas desde44 ejemplos, código fijo durante enseñanza.
- Diccionarios compartidos (24 entidades y12 valores para96 eventos), índice de hechos, caché invalidada al corregir, duplicados sin estado adicional, conflictos conservadores y reconstrucción nativa @rel source N.
- Crecimiento por96 hechos:30038bytes frente a97378del archivo textual E027; gzip4286frente a12819. Se preserva texto normalizado mediante marco/roles, no mayúsculas originales. No es una prueba de mínimo informacional absoluto.
- Región nueva exacta8400000000000000000 longitud73728. Fuente original sin ocupación y checkpoint libre antes de enseñar. Ninguna memoria previa cambia al enseñar NI al ingresar96 hechos, salvo metadato de idioma.
-1069 verificaciones E033;144 consultas temporales conservadas. Regresiones E027429/E028464/E029285/E025 original31/candidato31/W4u21, acción[4,2]. CLI de diccionario perro/dog conservada.
- Diagnóstico de desarrollo anterior:20/32→27/32. No reutilizarlo como test reservado nuevo. Persisten5 fallos abiertos de explicación/paráfrasis/pasos/traducción.

Se corrigieron dos defectos de aislamiento antes de aceptar el candidato:850... ya pertenecía a E025; después la auditoría detectó tablas remanentes fuera de la región declarada pese al paso funcional. El build y el examen ahora rechazan esos casos. E032 original nunca se sobrescribió.

## Objetivo concreto siguiente

Componer dos consultas de relaciones compartidas con procedencia y seguimiento de entidad, reutilizando diccionarios/índices en lugar de duplicar texto o añadir un motor externo. Primero declarar roles, tipos de relación y resolución de referencias para evitar confundir entidades que comparten nombre. Mantener separados tiempo de ocurrencia y orden de revisiones; el diario actual no resuelve fechas absolutas.

Requisitos: comprobar el HEAD, la reserva/ciclos y el ejecutor actuales; restaurar E033 limpio con cápsula compatible; conservar E032; fijar nuevas historias y familias de entidades separadas ANTES de evaluar. Aprendizaje e inferencia dentro de XI/Ether. No modificar ni fusionar SOVENGI.

Aceptación: consultas nuevas de dos propiedades con fuentes correctas y antecedente inequívoco; abstenerse ante propiedad faltante o conflicto; preservar168 respuestas de relaciones y144 temporales, repetir regresiones pertinentes y medir crecimiento/latencia. Conservar el anterior si falla. No declarar generación abierta ni ventaja de velocidad por comparación entre runners distintos.

Límites actuales:32 marcos,96 entidades,96 valores y255 eventos. Extender mediante paginación o migración verificable, sin perder diario ni checkpoints. W4u solo verificado en fixtures/acción nativa, no ingeniería autónoma ni Android. Usar exclusivamente el workflow bbyq-e029/native-e029 ubuntu-latest y pins REVERSE-PC a1b935ae0adf38615996bac92727e95289ad7cc1/Mundo X e2778d962af22f6f1a0794058dd4685fc2573966. Actualizar ESTADO, SIGUIENTE y registro también ante fallo; terminar el ciclo y esperar activación.
