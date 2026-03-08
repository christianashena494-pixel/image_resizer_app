[app]
title = Image Resizer
package.name = imageresizer
package.domain = org.example

version = 1.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,bmp,gif

orientation = portrait
fullscreen = 0

requirements = python3,kivy,pillow

# Android settings
android.api = 34
android.minapi = 21
android.build_tools = 34.0.0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
