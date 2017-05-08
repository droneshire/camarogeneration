#!/usr/bin/env python

import ntpath
import sys
import os
import glob

def printf(text):
	sys.stdout.write(text)
	sys.stdout.write('\n')

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def rename_jpgs(path):
	for file in glob.glob("*.jpg"):
		newname = file.split('-')
		os.system('mv {} {}'.format(file, newname[0] + '.jpg'))