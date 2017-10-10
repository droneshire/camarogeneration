#!/usr/bin/env python

from Tkinter import *
import ntpath
import sys
import os
import glob

FILE_NAME = 'homedir.txt'

def default_root_dir():
	root_dir = os.path.join(os.path.expanduser('~'), 'cgtools')
	if not os.path.exists(root_dir):
		os.makedirs(root_dir)
	return root_dir

def get_data_folder():
	root_dir = default_root_dir()
	dir_file = os.path.join(root_dir, FILE_NAME)
	home_dir = ''
	if os.path.isfile(dir_file):
		with open(dir_file, 'r') as f:
			for line in f:
				home_dir = line
			if os.path.exists(home_dir):
				root_dir = home_dir
	return root_dir

def make_sure_path_exists(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

def printf(text):
	sys.stdout.write(text)
	sys.stdout.write('\n')

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def rename_jpgs(path):
	os.chdir(path)
	for file in glob.glob("*.jpg"):
		newname = file.split('-')
		os.system('mv {} {}'.format(file, newname[0] + '.jpg'))

class SetHomeDir(object, Frame):

	def __init__(self, parent, exit_callback):
		Frame.__init__(self, parent)
		self.dir_var = StringVar()
		self.home_dir = None
		self.exit_callback = exit_callback

		home_dir=Label(self.master, text="Home Directory")
		home_dir.pack(side=LEFT)
		bar1=Entry(self.master, textvariable=self.dir_var, width=35)
		bar1.pack(side=LEFT, padx=5, pady=5)
		bbtn= Button(self.master, text="Browse", command=self.browse_dir)
		bbtn.pack(side=LEFT, padx=5, pady=5)
		cbtn = Button(self.master, text="OK", command=self.update_root_dir)
		cbtn.pack(side=BOTTOM,padx=5, pady=5)

	def update_root_dir(self):
		file = os.path.join(default_root_dir(), FILE_NAME)
		with open(file, 'w') as f:
			print 'Updating root dir: '
			if self.home_dir is not None:
				f.write(self.home_dir)
				print self.home_dir
			else:
				f.write(default_root_dir())
				print default_root_dir()
			f.close()

		self.exit_callback()

	def browsefile(self):
		from tkFileDialog import askdirectory
		Tk().withdraw()
		return askdirectory()

	def browse_dir(self):
		self.home_dir = self.browsefile()
		self.dir_var.set(self.home_dir)
