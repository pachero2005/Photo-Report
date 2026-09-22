[app]

# (str) Title of your application
title = Control de Lotes

# (str) Package name
package.name = controllotes

# (str) Package domain (needed for android packaging)
package.domain = org.inspection

# (list) Source files to include (let it include json for states and jpg/png)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Source files to exclude (optional)
#source.exclude_exts = spec

# (list) List of directory to include (from source.dir)
source.include_dirs = assets

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,pillow,pyjnius

# (list) Supported orientations
orientation = portrait

#
# Android specific
#

# (int) Target Android API, should be as high as possible. 
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 24

# (bool) Use AndroidX
android.enable_androidx = True

# (list) Permissions
android.permissions = CAMERA, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (list) The format used to package the app for each architecture
android.archs = arm64-v8a, armeabi-v7a

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 1
