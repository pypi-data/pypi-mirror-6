
I got tired of not having a good cross-platform module for accessing the clipboard in Python, so I put this together. 
It is a module that loads a copy() and paste() function depending on what your operating system (or window manager) is.

It has the following requirements:
    Windows - No requirements. You dont need the win32 module installed.
    Mac - Requires the pbcopy and pbpaste, which come with OS X.
    Linux - Requires the xclip command, which possibly comes with the os. If not, run sudo apt-get install xclip. Or have the gtk or PyQt4 modules installed.
    Pyperclip runs on both Python 2 and Python 3.

Usage is simple:
    import pyperclip
    pyperclip.copy('The text to be copied to the clipboard.')
    spam = pyperclip.paste()


Change Log:
1.2 Use the platform module to help determine OS.
1.3 Changed ctypes.windll.user32.OpenClipboard(None) to ctypes.windll.user32.OpenClipboard(0), after some people ran into some TypeError
