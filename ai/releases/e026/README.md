# E026 TwoFacts — candidato de composición en XI

Este candidato conserva la cápsula y la semilla E025 auténticas. Enlaza un adaptador XI delante del programa recuperado y redirige sus dos salidas finales a una continuación XI. El análisis de cada consulta, la recuperación de hechos y la generación de cada respuesta siguen en el mismo programa nativo.

## Contrato acotado

Reconoce cuatro formas diseñadas, en minúsculas ASCII y con un sujeto de 1 a 31 letras:

- `que es SUJETO y que requiere`
- `que es SUJETO y que necesita`
- `what is SUJETO and what does it require`
- `what is SUJETO and what does it need`

Admite un signo `?` final. Conserva el sujeto explícito en las dos consultas. Las variantes necesita/need se normalizan en XI a la consulta canónica requiere/require. La respuesta es la concatenación de dos respuestas atómicas del agente, con un espacio. No se añaden hechos en el adaptador, no se construyen respuestas en Python/JS y no se presentan estos patrones diseñados como gramática aprendida.

Una petición que no coincide exactamente conserva la ruta E025. No se interpretan órdenes de enseñanza ni de escritorio como segunda cláusula. El espacio temporal `8800000000000000000..+511` se limpia al salir; las pruebas lo comprueban nativamente.

## Construcción y pruebas en el ejecutor configurado

```sh
python3 ai/releases/e026/regression.py /ruta/reverse_pc /ruta/evidencia/e026
python3 ai/releases/e026/test.py /ruta/reverse_pc /ruta/evidencia/e026 /ruta/evidencia/composition
```

El primer comando reconstruye E025 sin alterar sus fuentes ni sus hashes, compila el enlace candidato, empaqueta una cápsula con versión E026-TwoFacts-dev y aplica las 31 comprobaciones existentes al candidato. El segundo compara respuestas completas con dos consultas atómicas independientes y examina referentes desconocidos, negación/contradicción, referentes mixtos no admitidos y limpieza.

La semilla RVPC2 permanece idéntica a E025. La cápsula cambia de hash e identidad de datos: este candidato no reemplaza automáticamente memorias privadas Android y no está desplegado en REVERSE-PC. Cualquier promoción deberá preservar esas memorias y verificar una migración compatible.

## Alcance de la evidencia

El primer intento pasó 48/48 consultas de desarrollo y falló 0/48 en las variantes. Ese conjunto dejó de ser reservado al utilizar su resultado para corregir el adaptador. La ejecución corregida usa sujetos nuevos, pero sus cuatro formas están diseñadas explícitamente: mide transferencia de sujetos dentro de ese contrato, no generalización a estructuras lingüísticas desconocidas.

Los resultados reales y las referencias a cada intento se guardan en docs/autonomy/ESTADO.json y en el registro del ciclo. Las transcripciones completas y las cápsulas probadas se conservan en los artefactos de CI. No se modifica el constructor de recuperación exacta E025 para eludir sus comprobaciones de identidad.
