from distutils.core import setup
import py2exe

setup(
    name = "miCoach backup",
    version = "1.0",
    description = "Tool to save your workouts from Adidas miCoach to your computer",
    author = "Manuel Vonthron",
    author_email = "manuel.vonthron@acadis.org",
    url = "https://github.com/gliss/micoach-backup",
    
    # py2exe
    windows = [{
        "script": "micoach-backup",
        "icon_resources": [(0, "icon.ico")],
        "copyright": "Copyright (c) 2012, Manuel Vonthron",
        "version": "1.0",
    }],
    zipfile = None,
    options = {
        "py2exe": {
            "includes": ["PySide.QtXml", "configobj"],
            "dll_excludes": ["MSVCP90.dll", "w9xpopen.exe"],
            "bundle_files": 1,
            'compressed': 1,
            'optimize': 2,
        }
    },
)
