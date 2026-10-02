# Arquitectura prevista

Una aplicación web privada para dos operadores. React y TypeScript para la interfaz; Django/DRF y PostgreSQL para biblioteca y revisiones; Celery y Redis para despachar trabajos; FFmpeg para medios. Despliegue central Linux, archivos compartidos y acceso privado.

La interfaz usará proxies y peticiones paginadas. La base de datos conservará el estado durable; los workers podrán reintentar sin producir entregas duplicadas mediante claves e inspección de resultados. Modelos y servicios se conectarán mediante adaptadores con capacidades explícitas.

La muestra pública usa tiempos enteros en microsegundos e intervalos [inicio, fin). Permite reordenar y repetir material. Incluye intro/outro; excluye transiciones solapadas y cambios de velocidad. Validar duraciones no resuelve por sí mismo timebases, VFR o sincronía de un render.

## YouTube

La documentación pública revisada permite subir vídeos, traducir metadatos y programar publicaciones bajo condiciones. Para audio adicional documenta un recorrido en Studio; no se promete una API pública de carga de doblajes.

[API de vídeos](https://developers.google.com/youtube/v3/docs/videos) · [Pistas multilingües](https://support.google.com/youtube/answer/13338784?hl=en).

No hay pruebas de publicación ni benchmarks de medios en esta muestra. Las integraciones pertenecen a fases posteriores.
