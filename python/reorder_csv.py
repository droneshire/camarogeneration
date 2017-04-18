#!/usr/bin/env python
import os
import sys
import csv
import argparse
import datetime

import util


class ReorderCsv(object):
	ROOT_DIR = '..'
	OUTPUT_DIR = 'converted_csvs'
	INPUT_DIR = 'product_lists'
	MASTER_FILE = 'master_product_list.csv'

	def __init__(self, input_file, target_filename, output=util.printf):
		i = datetime.datetime.now()
		f, e = os.path.splitext(util.path_leaf(input_file))
		out = f + '_{}_{}_{}_{}_{}'.format(
						  i.month, i.day, i.year, i.hour, i.minute) + e
		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.infile = input_file
		self.outfile = os.path.join(self.root_dir, self.OUTPUT_DIR, out)
		self.infile_name = input_file
		self.targetfile = target_filename

	def reorder(self):
		util.printf('Opening {}...'.format(self.infile))
		util.printf('Saving output file as {}...'.format(self.outfile))

		out_header = []
		reordered_header = []

		out_dir = os.path.join(self.root_dir, self.OUTPUT_DIR)
		if not os.path.exists(out_dir):
			os.makedirs(out_dir)

		try:
			with open(self.targetfile, 'r') as ft:
				target_csv = csv.reader(ft)
				out_header = target_csv.next()[1:]
				reordered_header = [r for r in target_csv if util.path_leaf(self.infile_name) in r]
				if len(reordered_header) > 1:
					self.fmt_out('ERROR: multiple csv files with same name ({})'.format(
							self.infile_name))
					sys.exit(1)
				if len(reordered_header) == 0:
					self.fmt_out('ERROR: no csv files with name {}'.format(self.infile_name))
					sys.exit(1)
				reordered_header = reordered_header[0][1:]
			ft.close()
		except:
			self.fmt_out('ERROR: Could not open {}'.format(self.targetfile))
			sys.exit(1)
		try:
			with open(self.infile, 'r') as fi, open(self.outfile, 'w') as fo:
				in_csv = csv.reader(fi)
				writer = csv.DictWriter(fo, fieldnames=reordered_header, extrasaction='ignore')
				header = csv.DictWriter(fo, fieldnames=out_header, extrasaction='ignore')
				header.writeheader()
				for r in csv.DictReader(fi):
					writer.writerow(r)
			fi.close()
			fo.close()
		except:
			self.fmt_out('ERROR: Could not open {} or create {}'.format(
						self.infile, self.outfile))
			sys.exit(1)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--input_filename', nargs=1,
						help='Filename to parse')
	parser.add_argument('-t', '--target_filename', nargs=1,
						help='Filename to match', default=[ReorderCsv.MASTER_FILE])
	args = parser.parse_args()

	root = os.path.abspath(os.path.join(os.getcwd(), ReorderCsv.ROOT_DIR))
	infile = os.path.join(root, ReorderCsv.INPUT_DIR, args.input_filename[0])

	ReorderCsv(infile, args.target_filename[0]).reorder()
