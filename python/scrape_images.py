#!/usr/bin/env python
import os
import sys
import argparse
import datetime
from shutil import copyfile

OUTPUT_DIR = 'parsed_images'
INPUT_DIR = 'images'
IMG_LIST_DIR = 'image_lists'
IMG_EXTENSION = '.jpg'
ROOT_DIR = '..'
IMAGE_COLUMN_NAME = 'Image File Names'

def get_images(root_dir, csvfile):
	infile = os.path.join(root_dir, IMG_LIST_DIR, csvfile)
	images = []
	try:
		with open(infile, 'r') as f:
			reader = csv.reader(f)
			header = reader.next()
			try:
				c = header.index(IMAGE_COLUMN_NAME)
			except:
				print 'ERROR: {} needs image list in column "{}"'.format(
						csvfile, IMAGE_COLUMN_NAME)
				sys.exit(1)
			for r in reader:
				images.append(r[0] + IMG_EXTENSION)
		f.close()
		return images
	except:
		print 'ERROR: Could not open {} or create {}'.format(
				input_filename, output_filename)
		sys.exit(1)

def run(input_filename, image_folder_dir):
	root_dir = os.path.abspath(os.path.join(os.getcwd(), ROOT_DIR))
	image_folder_dir = os.path.join(root_dir, image_folder_dir)
	i = datetime.datetime.now()
	f, e = os.path.splitext(input_filename)
	out = f + '_{}_{}_{}_{}_{}'.format(
					  i.month, i.day, i.year, i.hour, i.minute)

	parsed_dir = os.path.join(root_dir, OUTPUT_DIR)

	if not os.path.exists(parsed_dir):
		os.makedirs(parsed_dir)

	out_dir = os.path.join(parsed_dir, out)
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	print 'Computing image list from {}...'.format(input_filename)
	image_list = get_images(root_dir, input_filename)
	print 'Searching for {} images in {}...'.format(len(image_list), image_folder_dir)
	print 'Saving to {}...'.format(out_dir)

	img_found = 0
	missing = []

	if os.path.exists(image_folder_dir):
		for i in image_list:
			src = os.path.join(image_folder_dir, i)
			dst = os.path.join(out_dir, i)
			if os.path.isfile(src):
				copyfile(src, dst)
				print 'Found image {}...'.format(i)
				img_found += 1
			else:
				missing.append(i)

		print 'Could not find the following images:\n{}'.format(', '.join(missing))

		print 'Found {} images'.format(img_found)
	else:
		print 'ERROR: Image search directory does not exist!'
		sys.exit(1)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--input_filename', nargs=1,
						required=True, help='Filename to parse')
	parser.add_argument('-d', '--input_dir', nargs=1,
						help='Directory of images to sort through',
						default=[INPUT_DIR])
	args = parser.parse_args()

	run(args.input_filename[0], args.input_dir[0])
