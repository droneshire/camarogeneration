from setuptools import setup, find_packages
from Tkinter import *
import subprocess
import sys
import os
from shutil import copyfile

# get the version included in the __init__
import cgtools.util

folders = [
        ]

fnames = [os.path.join('cgtools','README.md'),
          os.path.join('cgtools','ui_images','logo.jpg'),
	      os.path.join('cgtools','cg_tools.bat'),
         ]

def remove_first_dir(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return os.path.join(*allparts[1:])

root = Tk()
root.title('Home Directory Util')
cgtools.util.SetHomeDir(root, root.quit).mainloop()

datafiles_dir = cgtools.util.get_data_folder()
ret = {}
for folder in folders:
    for d, _, files in os.walk(folder):
        ret[os.path.join(datafiles_dir, remove_first_dir(d))] = [os.path.join(d,f) for f in files]

for fname in fnames:
    print 'add', fname
    dirname = os.path.dirname(os.path.join(datafiles_dir, remove_first_dir(fname)))
    if dirname in ret:
        ret[dirname].append(fname)
    else:
        ret[dirname] = [fname]

datafiles = []
for k, v in ret.iteritems():
    datafiles.append((k, v))

for d in datafiles:
    print d

setup(
    name='cg-tools',
    version='1.0.0',
    author='Ross Yeager',
    author_email='ryeager.design@gmail.com',
    url='https://github.com/rossyeager/camarogeneration',
    install_requires=['Tkinter', 'PIL'] ,
    packages=find_packages(),
    data_files=datafiles,
    entry_points={
        'console_scripts': ['install-shortcuts = cgtools.install_shortcuts:main',]
    }
)
