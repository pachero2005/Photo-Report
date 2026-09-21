[app]

# (str) Título de tu aplicación
title = Photo Report

# (str) Nombre del paquete (sin espacios ni mayúsculas)
package.name = photoreport

# (str) Dominio del paquete (basado en tu usuario de GitHub)
package.domain = org.pachero2005

# (list) Código fuente a incluir (en la raíz)
source.dir = .

# (list) Extensiones de archivos a incluir
source.include_exts = py,png,jpg,jpeg,kv,json

# (str) Versión de la aplicación
version = 0.1

# (list) Dependencias de la aplicación (incluyendo pillow y pyjnius usados en tu código)
requirements = python3,kivy,pillow,pyjnius

# (str) Orientación soportada de la pantalla
orientation = portrait

# (bool) Indicar si la aplicación debe ejecutarse a pantalla completa
fullscreen = 0

# (list) Permisos de Android necesarios para la cámara y almacenamiento
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) API de Android de destino
android.api = 33

# (int) API mínima de Android compatible
android.minapi = 21

# (list) Arquitecturas soportadas (arm64-v8a es estándar hoy en día)
android.archs = arm64-v8a

[buildozer]

# (int) Nivel de registro (0 = error, 1 = info, 2 = debug con comandos detallados)
log_level = 2

# (int) Mostrar advertencia si se ejecuta como root (útil para GitHub Actions)
warn_on_root = 1
