from distutils.core import setup

setup(
    name="pyperclip",
    version="1.3",
    maintainer="Alexander Cobleigh",
    author="Al Sweigart",
    platforms=["Windows", "OSX", "Linux"],
    author_email="al@coffeeghost.net",
    url="http://coffeeghost.net/2010/10/09/pyperclip-a-cross-platform-clipboard-module-for-python/",
    packages=["pyperclip",],
    data_files = [("", ["LICENSE.txt"])],
    license="LICENSE.txt",
    description="A cross-platform clipboard module for Python. ",
    long_description=open("README.txt").read(),
)
