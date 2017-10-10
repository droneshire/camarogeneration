 #!/usr/bin/env python
import argparse
import csv
import datetime
import ftplib
import os
import sys
import urllib
import urllib2

from PIL import Image
from shutil import copyfile

import erase_images
import util


class ScrapeImages(object):
	ROOT_DIR = util.get_data_folder()
	OUTPUT_DIR = 'parsed_images'
	INPUT_DIR = 'images'
	THUMBNAIL_DIR = 'thumbnails'

	IMG_LIST_DIR = 'image_lists'
	IMG_EXTENSION = '.jpg'
	IMAGE_COLUMN_NAME = 'Image File Names'

	FTP_STOR_CMD = 'STOR '
	FTP_LIST_CMD = 'LIST '
	FTP_IMG_DIR = 'product_images'

	def __init__(self, input_file, image_dir, erase_imgs=False, do_copy_original=True,
				 do_copy_pdf=False, ftp_session=None, output=util.printf, thumbnail_sizes=None):
		self.do_erase = erase_imgs
		self.do_copy_original = do_copy_original
		self.do_copy_pdf = do_copy_pdf

		self.input_file = input_file
		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.image_dir = image_dir

		self.session = ftp_session

		self.fmt_out = output
		self.thumbnail_sizes = thumbnail_sizes

	def check_for_download(self, row, name):
		""" check to see if we should download any images from this row """
		download_image_increment = 0
		images = []
		for val in row:
			if not val.startswith('http'):
				continue
			download_img = name
			if download_image_increment:
				download_img += '_' + str(download_image_increment)
			download_img += self.IMG_EXTENSION
			save_file = os.path.join(self.image_dir, download_img)
			images.append(download_img)
			download_image_increment += 1
			
			if os.path.isfile(save_file):
				util.printf('Already downloaded {}, skipping...'.format(download_img))
				continue
			response = urllib2.urlopen(val)
			util.printf('Downloading {}...'.format(download_img))
			with open(save_file, 'w') as outfile:
				outfile.write(response.read())
		return images

	def get_images(self, csvfile):
		images = []
		try:
			with open(csvfile, 'r') as f:
				reader = csv.reader(f)
				header = reader.next()
				try:
					c = header.index(self.IMAGE_COLUMN_NAME)
				except:
					self.fmt_out('ERROR: {} needs image list in column "{}"'.format(
							csvfile, self.IMAGE_COLUMN_NAME))
					return []
				for row in reader:
					image_names = []
					downloads = self.check_for_download(row, row[c])
					if len(downloads):
						image_names.extend(downloads)
					else:
						image_names.append([row[c] + self.IMG_EXTENSION])
					images.extend(image_names)
			f.close()
			return images
		except:
			self.fmt_out('ERROR: Could not open {}'.format(csvfile))
			return []

	def parse_images(self):
		i = datetime.datetime.now()
		f, e = os.path.splitext(util.path_leaf(self.input_file))
		image_output_filename = f + '_{}_{}_{}_{}_{}_{}'.format(
						  i.month, i.day, i.year, i.hour, i.minute, i.second)

		parsed_dir = os.path.join(self.root_dir, self.OUTPUT_DIR)

		if not os.path.exists(parsed_dir):
			os.makedirs(parsed_dir)

		image_output_dir = os.path.join(parsed_dir, image_output_filename)
		if not os.path.exists(image_output_dir):
			os.makedirs(image_output_dir)

		util.printf('Computing image list from {}...'.format(self.input_file))
		image_list = list(set(self.get_images(self.input_file)))
		util.printf('Searching for {} images in {}...'.format(len(image_list), self.image_dir))
		util.printf('Saving to {}...'.format(image_output_dir))

		img_found = 0
		missing = []

		if os.path.exists(self.image_dir):
			for i in image_list:
				src = os.path.join(self.image_dir, i)
				src_pdf = os.path.splitext(src)[0] + '.pdf'
				dst = os.path.join(image_output_dir, i)
				if os.path.isfile(src):
					if self.do_copy_original:
						copyfile(src, dst)

					if self.thumbnail_sizes is not None:
						t_dir = os.path.join(image_output_dir, self.THUMBNAIL_DIR)
						if not os.path.exists(t_dir):
							os.makedirs(t_dir)

						for tb in self.thumbnail_sizes:
							with Image.open(src) as img:
								width = self.thumbnail_sizes[tb]
								size = (width, width)
								img.thumbnail(size, Image.ANTIALIAS)
								f, e = os.path.splitext(util.path_leaf(dst))
								imgname = os.path.join(
									t_dir,'{}{}.jpg'.format(f, tb))
								img.save(imgname)
								img.close()
					else:
						copyfile(src, dst)

					if self.do_copy_pdf:
						if os.path.isfile(src_pdf):
							copyfile(src_pdf, dst)
							util.printf('Found image {} and PDF...'.format(i))
						else:
							util.printf('Found image {}...'.format(i))


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
			if img_found != len(image_list):
				self.fmt_out('Could not find the following images:\n{}'.format(
							', '.join(missing)))

			# remove directory if nothing was placed in it
			try:
				os.rmdir(image_output_dir)
			except:
				pass

			util.printf('Found {} images'.format(img_found))
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
			f = raw_input('Enter ftp address: ')
			l = raw_input('Enter ftp login: ')
			p = raw_input('Enter ftp password: ')
			session = ftplib.FTP(f, p, l)
		except:
			util.printf('Could not connect to {}'.format(f))
			sys.exit(1)
		util.printf('Connected')

	root = os.path.abspath(os.path.join(os.getcwd(), ScrapeImages.ROOT_DIR))
	infile = os.path.join(root, ScrapeImages.IMG_LIST_DIR, args.input_file[0])
	imgdir = os.path.join(root, args.input_dir[0])

	ScrapeImages(infile, imgdir, args.erase, session).parse_images()
