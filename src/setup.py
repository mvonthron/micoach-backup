from distutils.core import setup
import py2exe
from config import VERSION

setup(
    name = "miCoach backup",
    version = VERSION,
    description = "Tool to save your workouts from Adidas miCoach to your computer",
    author = "Manuel Vonthron",
    author_email = "manuel.vonthron@acadis.org",
    url = "https://github.com/mvonthron/micoach-backup",
    
    # py2exe
    windows = [{
        "script": "micoach-backup",
        "icon_resources": [(0, "gui/images/icon.ico")],
        "copyright": "Copyright (c) 2013, Manuel Vonthron",
        "version": VERSION,
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
