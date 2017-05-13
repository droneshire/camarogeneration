#!/usr/bin/env python
import os
import sys
import argparse

INPUT_DIR = '../../images'

def erase(image_folder_dir, root_dir):
	image_folder_dir = os.path.join(root_dir, image_folder_dir)

	if os.path.exists(image_folder_dir):
		print 'Erasing images in {}...'.format(image_folder_dir)
		for imgfile in os.listdir(image_folder_dir):
			img = os.path.join(image_folder_dir, imgfile)
			os.remove(img)
	else:
		print 'ERROR: Image search directory does not exist!'
		sys.exit(1)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--input_dir', nargs=1,
						help='Directory of images to sort through',
						default=[INPUT_DIR])
	args = parser.parse_args()

	erase(args.input_dir[0])
