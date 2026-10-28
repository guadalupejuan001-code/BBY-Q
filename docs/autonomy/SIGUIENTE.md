# Siguiente ciclo

Estado al preparar la continuidad: se consultó `main` en `e8498b765a6a95aa556d0e816aab926257769391`; su checkpoint publicado es E022. Esto es una observación, no una selección fija para activaciones futuras.

## Objetivo inmediato

Comprobar que el ejecutor configurado puede reproducir y examinar el estado vigente antes de enseñar nuevas capacidades, resolviendo primero cualquier checkpoint o rama más reciente y localizando el estado real de W4u.

## Requisitos

- Acceso al repositorio y al ejecutor ya configurado.
- Leer `OBJETIVO.md`, `ESTADO.json`, este archivo y el registro enlazado por el estado.
- Resolver los HEAD y checkpoints actuales y comprobar si ya hay un ciclo activo.
- Si estos archivos aún no están en `main`, la rama de continuidad inicial es `autonomy/bbyq-w4u-daily-20261028`; contrastarla siempre con cambios posteriores.
- El ejecutor observado está definido en `.github/workflows/bbyq-e022.yml`, job `compositional-requests`, runner `ubuntu-latest`. No asumir que es el ejecutor actual si la configuración cambió.

## Instrucción pendiente exacta

Cuando se confirme acceso al canal autorizado de lanzamiento de GitHub Actions y E022 siga siendo la base pertinente, solicitar **una sola vez** el workflow configurado:

```sh
gh workflow run bbyq-e022.yml --repo guadalupejuan001-code/BBY-Q --ref main
```

Este comando se conserva como instrucción de despacho, **no se ha ejecutado** y no acredita que `gh` esté configurado. Usar únicamente un canal de lanzamiento ya configurado; no instalar ni sustituir un ejecutor para sortear un bloqueo. Resolver la referencia actual antes de despachar si la base cambió. Si el workflow ya está en curso, observarlo en lugar de duplicarlo.

## Criterio de aceptación

Una ejecución nueva identificada por ID, commit y URL concluye con evidencia nativa accesible, verifica la integridad y conservación del checkpoint y registra sus resultados. Un éxito histórico no satisface este criterio. Reproducir E022 tampoco se contará como aprendizaje nuevo.

Tras resolver este requisito, elegir una capacidad concreta de lenguaje, generación, contexto o generalización con un diagnóstico independiente antes/después; mantener el aprendizaje en XI/Ether y conservar los checkpoints anteriores. El siguiente objetivo debe quedar concretado a partir del diagnóstico real.

## Si falla

Registrar el error literal, los comandos realmente ejecutados y los que siguen pendientes. Actualizar `ESTADO.json`, este archivo y el registro del ciclo. No repetir el mismo despacho o entrenamiento sin un cambio verificable del acceso, la configuración o la hipótesis que explica el fallo.
