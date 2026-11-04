# BBY Q: 100 cúbits simulados con álgebra exacta

Un registro de 100 en el CompactCore original de XI/Ether. El estado inicial
GHZ conecta los 100. Ocupa 3.300 bytes de tableau y no usa MPS, coeficientes
flotantes, truncamiento ni tolerancias para sus operaciones de estado.

El perfil certifica H, S, X, Y, Z, CX y CZ. Los signos y las operaciones del
tableau son discretos. Las probabilidades de medición son 0, 1/2 o 1, todas
representables exactamente. La fase global no observable se omite.

"Exacto" describe este conjunto de puertas. No afirma soportar rotaciones
arbitrarias con exactitud matemática ni estados arbitrarios de 2^100 amplitudes.
T, RX, RY y RZ se rechazan antes de ejecutar. Este registro no es todavía un
modelo conversacional entrenado ni evidencia de ventaja sobre otros modelos.

El código XI ejecuta las puertas en el runtime existente. Python y Node solo
validan el perfil, transportan programas y publican checkpoints. El verificador
independiente de Pauli está limitado a las pruebas.

## Uso

Compilar REVERSE-PC con el Ether fijado en las revisiones de la CI. Después:

```sh
node bbyq.mjs quantum exact100 prepare NUEVA_SESION --runtime=/ruta/REVERSE-PC/build/reverse_pc
node bbyq.mjs quantum exact100 audit NUEVA_SESION
node bbyq.mjs quantum exact100 apply NUEVA_SESION circuito.xi
node bbyq.mjs quantum exact100 export NUEVA_SESION NUEVO_ARCHIVO.rvp
```

`circuito.xi` acepta puertas certificadas con direcciones literales
10000..10099, comentarios, cabecera XI y un `halt` final opcional:

```text
#!reverse-pc-machine-v1
s 10099
h 10017
cz 10017 10084
halt
```

Las versiones guardadas son inmutables; HEAD se publica después de verificar
el candidato. Los archivos de VQC3/QRL3 y la APK anterior se conservan.
La sesión guarda hasta 4.096 puertas conocidas para verificar su inversa.
Es un límite del perfil de auditoría, no un límite físico universal.

## Verificación

```sh
python3 integration/exact100/validate.py --runtime=/ruta/reverse_pc --output=build/exact100/validation.json
```

Se comprueban los 100 estabilizadores del GHZ, la causalidad de los 100 sitios,
ocho circuitos de fases y conexiones largas mediante 100 estabilizadores
independientes por circuito, doce mediciones completas, la inversión y la
restauración del checkpoint. El certificado independiente verifica rango y
conmutación. Todas las comparaciones de observables son exactas, sin epsilon.
