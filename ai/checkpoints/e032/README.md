# Modelo temporal aprendido en XI

48 formas ES/EN, 96 ejemplos con roles supervisados. Checkpoint guardado antes de hechos temporales de examen. Conserva conocimiento y patrones E030.

RVPC2 SHA256: `f1c2ace6a8d35643c0ae68103f3cb0aa33a0325c9fea004f00fd5e38d60ffb56`.
Cápsula compatible: `d2c5e4ebb2b0c3b7af74abc881d6f8c1a5ff2e106f621d0ceba5cb312b525048`, PR #38.

Decodificar base64 y gzip para obtener RVPC2. No sobrescribir un estado privado existente. Ejemplo de restauración desde la raíz:

```sh
python3 -c "import base64,gzip,pathlib; p=pathlib.Path('ai/checkpoints/e032/temporal-model.rvp.gz.b64'); pathlib.Path('temporal-model.rvp').write_bytes(gzip.decompress(base64.b64decode(p.read_text())))"
sha256sum temporal-model.rvp
```

https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40795445276

Primera capacidad de posesión en tres categorías temporales; no fechas ni dominio general del idioma. Guardar el checkpoint previo permite comparar/retroceder.
