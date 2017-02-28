miCoach Backup
=====

**miCoach backup** ~~is~~ was a tool to save your workouts from [Adidas miCoach] to your computer.

Adidas as since shut down *miCoach* (which makes this tool both retrospectively usefull and unusable now). You can still migrate your data to Runtastic (that Adidas bought) by following the instruction here: https://www.runtastic.com/import/runtastic/adidas.

Description
----

**miCoach backup** contains two things:

  - a Python implementation of *Adidas miCoach* API 
  - a small GUI for selecting and saving you workouts


Usage 
-----
**Requirements**
  - a computer and a *miCoach* account...

No requirements with the win32 binary, from the Python source code:
  - [Python](http://www.python.org) 2.6+
  - [PySide](http://www.pyside.org)
  - [ConfigObj](http://www.voidspace.org.uk/python/configobj.html)

**Installation**

No installation needed. Just move the program wherever you like.

**Usage**

1. Run `micoach-backup`
2. Enter your *miCoach* credentials
3. Select workouts to be downloaded (by default the tool only looks for newly added workouts )
4. Wait a few seconds, you're all done!


Screenshot
----

![miCoach backup](http://acadis.org/images/micoach/screenshot-chooseView.png)

What else
----

**miCoach backup** is not longer developped, nor usable since Adidas shut down the servers.

The SOAP API let's you do pretty much everything the [website](http://www.micoach.com/) can do and even a lot more. So far you will only be able to save your workouts on you computer.

Licensing
---------

This program and its documentation are released under the terms of the
BSD license.

XML manipulation library (simplexml.py) by Mariano Reingar, LGPL license

----
2012, Manuel Vonthron <manuel.vonthron@acadis.org>

  [Adidas miCoach]: http://www.micoach.com/ 

