#!/usr/bin/env python
import os
import sys
import csv
import argparse
import datetime


class ReorderCsv(object):
	ROOT_DIR = '..'
	OUTPUT_DIR = 'converted_csvs'
	INPUT_DIR = 'product_lists'
	MASTER_FILE = 'master_product_list.csv'

	def __init__(self, input_filename, target_filename):
		i = datetime.datetime.now()
		f, e = os.path.splitext(input_filename)
		out = f + '_{}_{}_{}_{}_{}'.format(
						  i.month, i.day, i.year, i.hour, i.minute) + e
		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.infile = os.path.join(self.root_dir, self.INPUT_DIR, input_filename)
		self.outfile = os.path.join(self.root_dir, self.OUTPUT_DIR, out)
		self.infile_name = input_filename
		self.targetfile = target_filename

	def reorder(self):
		print 'Opening {}...'.format(self.infile)
		print 'Saving output file as {}...'.format(self.outfile)

		out_header = []
		reordered_header = []

		out_dir = os.path.join(self.root_dir, self.OUTPUT_DIR)
		if not os.path.exists(out_dir):
			os.makedirs(out_dir)

		try:
			with open(self.targetfile, 'r') as ft:
				target_csv = csv.reader(ft)
				out_header = target_csv.next()[1:]
				reordered_header = [r for r in target_csv if self.infile_name in r]
				if len(reordered_header) > 1:
					print 'ERROR: multiple csv files with same name ({})'.format(
							self.infile_name)
					sys.exit(1)
				if len(reordered_header) == 0:
					print 'ERROR: no csv files with name {}'.format(self.infile_name)
					sys.exit(1)
				reordered_header = reordered_header[0][1:]
			ft.close()
		except:
			print 'ERROR: Could not open {}'.format(self.targetfile)
			sys.exit(1)
		try:
			with open(self.infile, 'r') as fi, open(self.outfile, 'w') as fo:
				in_csv = csv.reader(fi)
				writer = csv.DictWriter(fo, fieldnames=reordered_header)
				header = csv.DictWriter(fo, fieldnames=out_header)
				header.writeheader()
				for r in csv.DictReader(fi):
					writer.writerow(r)
			fi.close()
			fo.close()
		except:
			print 'ERROR: Could not open {} or create {}'.format(self.infile, self.outfile)
			sys.exit(1)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--input_filename', nargs=1,
						help='Filename to parse')
	parser.add_argument('-t', '--target_filename', nargs=1,
						help='Filename to match', default=[ReorderCsv.MASTER_FILE])
	args = parser.parse_args()

	ReorderCsv(args.input_filename[0], args.target_filename[0]).reorder()
