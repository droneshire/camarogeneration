#!/usr/bin/env python
import os
import sys
import argparse
import datetime
import csv
from shutil import copyfile

import urllib
import ftplib

import erase_images

FTP_SERVER_ADDR = 'gmqjl.sgamh.servertrust.com'

def my_print(text):
	print text

class ScrapeImages(object):
	ROOT_DIR = '..'
	OUTPUT_DIR = 'parsed_images'
	INPUT_DIR = 'images'

	IMG_LIST_DIR = 'image_lists'
	IMG_EXTENSION = '.jpg'
	IMAGE_COLUMN_NAME = 'Image File Names'

	FTP_STOR_CMD = 'STOR '
	FTP_LIST_CMD = 'LIST '
	FTP_IMG_DIR = 'product_images'

	def __init__(self, input_file, image_dir, erase_imgs=False,
				 ftp_session=None, output=my_print):
		self.do_erase = erase_imgs

		self.input_file = input_file
		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.image_dir = os.path.join(self.root_dir, image_dir)

		self.session = ftp_session

		self.fmt_out = output

	def get_images(self, csvfile):
		infile = os.path.join(self.root_dir, self.IMG_LIST_DIR, csvfile)
		images = []
		try:
			with open(infile, 'r') as f:
				reader = csv.reader(f)
				header = reader.next()
				try:
					c = header.index(self.IMAGE_COLUMN_NAME)
				except:
					self.fmt_out('ERROR: {} needs image list in column "{}"'.format(
							csvfile, self.IMAGE_COLUMN_NAME))
					sys.exit(1)
				for r in reader:
					images.append(r[0] + self.IMG_EXTENSION)
			f.close()
			return images
		except:
			self.fmt_out('ERROR: Could not open {}'.format(infile))
			sys.exit(1)

	def parse_images(self):
		i = datetime.datetime.now()
		f, e = os.path.splitext(self.input_file)
		out = f + '_{}_{}_{}_{}_{}'.format(
						  i.month, i.day, i.year, i.hour, i.minute)

		parsed_dir = os.path.join(self.root_dir, self.OUTPUT_DIR)

		if not os.path.exists(parsed_dir):
			os.makedirs(parsed_dir)

		out_dir = os.path.join(parsed_dir, out)
		if not os.path.exists(out_dir):
			os.makedirs(out_dir)

		self.fmt_out('Computing image list from {}...'.format(self.input_file))
		image_list = self.get_images(self.input_file)
		self.fmt_out('Searching for {} images in {}...'.format(len(image_list), self.image_dir))
		self.fmt_out('Saving to {}...'.format(out_dir))

		img_found = 0
		missing = []

		if os.path.exists(self.image_dir):
			for i in image_list:
				src = os.path.join(self.image_dir, i)
				dst = os.path.join(out_dir, i)
				if os.path.isfile(src):
					copyfile(src, dst)
					self.fmt_out('Found image {}...'.format(i))
					img_found += 1
					if self.session is not None:
						f = open(src, 'rb')
						command = self.FTP_STOR_CMD + src
						session.cwd(self.FTP_IMG_DIR)
						ftp.retrlines(self.FTP_LIST_CMD + self.FTP_IMG_DIR)
						self.session.storbinary(command, f)
						f.close()
				else:
					missing.append(i)
			if self.session is not None:
				self.session.quit()

			self.fmt_out('Could not find the following images:\n{}'.format(', '.join(missing)))

			self.fmt_out('Found {} images'.format(img_found))
			if self.do_erase:
				erase_images.erase(self.image_dir, self.root_dir)
		else:
			self.fmt_out('ERROR: Image search directory does not exist!')
			sys.exit(1)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--input_file', nargs=1,
						required=True, help='Filename to parse')
	parser.add_argument('-d', '--input_dir', nargs=1,
						help='Directory of images to sort through',
						default=[ScrapeImages.INPUT_DIR])
	parser.add_argument('-u', '--upload_ftp', help='Upload images via ftp',
						action='store_true')
	parser.add_argument('-e', '--erase', help='Erase image folder after copy',
						action='store_true')
	args = parser.parse_args()

	session = None
	if args.upload_ftp:
		try:
			print('Connecting to {}...'.format(FTP_SERVER_ADDR))
			l = raw_input('Enter ftp login: ')
			p = raw_input('Enter ftp password: ')
			session = ftplib.FTP(FTP_SERVER_ADDR, p, l)
		except:
			print('Could not connect to {}'.format(FTP_SERVER_ADDR))
			sys.exit(1)
		print('Connected')

	ScrapeImages(args.input_file[0], args.input_dir[0], args.erase, session).parse_images()
