from distutils.core import setup
import py2exe

setup(
    name = "miCoach backup",
    version = "1.0",
    description = "miCoach backup is a tool to save your workouts from Adidas miCoach to your computer",
    author = "Manuel Vonthron",
    author_email = "manuel.vonthron@acadis.org",
    url = "https://github.com/gliss/micoach-backup",
    
    # py2exe
    windows = ["micoach-backup"],
    options = {
        "py2exe": {
            "includes": ["PySide.QtXml", "configobj"],
            "dll_excludes": ["MSVCP90.dll"]
        }
    },
)
