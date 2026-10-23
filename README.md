# BBY Q — laboratorio de señales físicas y ópticas

**Proyecto independiente** dedicado a estudiar cómo un Galaxy Watch4 Classic recibe luz y cómo convertir señales reales en experimentos reproducibles.

## Estado: prototipo Wear OS 0.1.0

- Registro de acelerómetro, giroscopio y luz ambiental, si el reloj los expone.
- Lectura del pulso óptico procesado (BPM) con permiso `BODY_SENSORS`.
- Integración **opcional** de muestras PPG digitalizadas (verde/rojo/infrarrojo) mediante el SDK oficial de Samsung. Para habilitarla se requiere el AAR licenciado, permisos y soporte real del reloj.
- Sesiones voluntarias de hasta 60 segundos, CSV local privado, sin acceso a Internet ni grabación oculta.

El código fuente de la aplicación Android está en `app/`. La compilación inicial no exige SDK de Samsung.

### Compilación

Requisitos: JDK 17, Android SDK 35, Gradle 8.9.

```sh
gradle --no-daemon :app:assembleDebug
```

APK de desarrollo: `app/build/outputs/apk/debug/app-debug.apk`.

Para el SDK opcional, coloca el archivo oficial `samsung-health-sensor-api.aar` en `app/libs/`. Su licencia y distribución pertenecen a Samsung; **el SDK no se incluye en este repositorio**.

### Documentación

- [Receptor óptico y procedimiento de captura](docs/RECEPTOR_OPTICO.md)
- [Plan experimental de BBY Q](ROADMAP.md)

**Límite físico importante:** un fotodiodo mide luz real, pero su salida digital PPG es clásica. Eso permite instrumentación y control mediante señales reales, no prueba de coherencia ni entrelazamiento cuántico con un estado de software.

Proyecto independiente: sin dependencias del repositorio Mundo X.
