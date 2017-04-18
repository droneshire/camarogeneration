#!/usr/bin/env python

import ntpath
import sys

def printf(text):
	sys.stdout.write(text)
	sys.stdout.write('\n')

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)