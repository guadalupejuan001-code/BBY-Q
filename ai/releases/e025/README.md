# BBY Q E025 + W4u 0.1

Esta entrega recupera exactamente el agente incluido en `REVERSE-v2.5.0.apk`:
BBY Q `E025-Chain-1`, 64 temas/cuentas y motor W4u 0.1 sin cambios.
La APK de origen tiene SHA-256
`a30683669e1f63b0e3134704c83f4e2c053a0429e469cc9b7deafba3157effed`.

El respaldo anterior solo conservaba las fuentes hasta E023. Los commits E025
declarados dentro de la APK no estaban publicados ni disponibles en el respaldo.
Por eso esta carpeta conserva el programa XI recuperado por desensamblado,
el bytecode original, su estado RVPC2 y el currículo XI de actualización, con
sus hashes. No se atribuye al código recuperado el historial Git perdido.

`build.py` recompila el XI y compara todas las instrucciones normalizadas,
reconstruye la cápsula RXE2 exactamente y verifica cada módulo del currículo.
Conserva el bytecode original para mantener la identidad del agente y su memoria
privada al actualizar. No repite su entrenamiento.

```sh
python3 ai/releases/e025/build.py /ruta/reverse_pc /ruta/salida
python3 ai/releases/e025/test.py /ruta/reverse_pc /ruta/pruebas
```

El anfitrión REVERSE requiere el límite de 524.288 overrides para ampliar
la memoria. `--assets /ruta/REVERSE-PC/reverse-os-android/app/src/main/assets`
instala la cápsula, W4u y las migraciones en el proyecto Android.

Las pruebas comprueban saludos ES/EN, conocimiento del escritorio, aprendizaje
persistente en procesos separados, una orden W4u real, rechazo transaccional
de una entrada excesiva y 70.000 escrituras adicionales de memoria.
No representan una medición de conversación abierta general.
