#-*- coding: utf-8 -*-
"""Graphical User Interfaces Procedures for PYthon.

 The guippy emulate various operations of computer users. It provides the
ability for emulate keyboards, mouses, window system, and clipboards. By using
this, you can run your computer automatically.

 This is a Pyhon 3rd party library. Written in pure Python. You need to Python
programming, but it is very easy to use. And you can easily and safely install.

example.

   >>> import guippy
   >>> gp = guippy.Guippy()
   >>> gp.catch()
   >>> gp.punch()


Let's get started.
"""
__version__ = '0.1.2'
__author__ = 'TakesxiSximada'
__credits__ = (__author__, )

# from . import mouse
# from . import keyboard
# from . import window
# from . import clipboard
# from . import api
# from . import error
# from . import shortcut
# from . import application
#from . import *  # import all objects in guippy.
from .mouse import Mouse
from .keyboard import Keyboard
from .window import Window
from .clipboard import Clipboard
from .guippy import Guippy


__all__ = (
    # in guippy module
    'Guippy',
    # in other modules
    'mouse', 'keyboard', 'window', 'clipboard',
    'Mouse', 'Keyboard', 'Window', 'Clipboard',
    'api', 'error', 'shortcut', 'application',
    )
