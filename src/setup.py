from distutils.core import setup
import py2exe

setup(
    name = "miCoach backup",
    version = "0.9",
    description = "miCoach backup is a tool to save your workouts from Adidas miCoach to your computer",
    author = "Manuel Vonthron",
    author_email = "manuel.vonthron@acadis.org",
    url = "https://github.com/gliss/micoach-backup",
    
    # py2exe
    windows = [{
        "script": "micoach-backup",
        "icon_resources": [(0, "gui/images/icon.ico")],
        "copyright": "Copyright (c) 2012, Manuel Vonthron",
        "version": "0.9",
    }],
    zipfile = None,
    options = {
        "py2exe": {
            "includes": ["PySide.QtXml", "configobj"],
            "dll_excludes": ["MSVCP90.dll", "w9xpopen.exe"],
            "bundle_files": 1
        }
    },
)
