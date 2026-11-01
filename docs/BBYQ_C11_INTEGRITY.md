# C11 — Auditoría de memoria real y compatibilidad QML/QRL

La comprobación tiene dos niveles. El primero verifica las huellas SHA-256 de los checkpoints históricos versionados del repositorio, reconstituyendo sus bytes RVPC2 sin reentrenar ni modificar los archivos. También verifica el checkpoint real E022 y el manifiesto del paquete X09.

El segundo nivel **no puede declararse superado sin la entrega binaria verificable X09/X10**. El repositorio contiene el manifiesto histórico, pero no incluye el archivo de unos 50 MB con los componentes originales. El resultado de pruebas con una sesión X10 sintética, aunque sea exitoso, no sustituye ese segundo nivel.

```sh
node integration/c11/audit.mjs
node integration/c11/audit.mjs --x10-build /ruta/a/build-x10-verificado
```

El segundo comando usa una sesión X10 temporal inicializada desde la semilla restaurada y verificada por SHA; comprueba 480 registros históricos, una respuesta tradicional, QML VQC2, QRL2, y que la huella del estado original y la cantidad de lecciones permanezcan idénticas tras las operaciones.

**Regla de publicación:** si solo pasa la primera etapa, el resultado será `manifest_only_until_restored`; nunca se presentará como validación de todos los entrenamientos reales.
