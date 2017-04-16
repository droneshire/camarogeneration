#!/usr/bin/env python
import os
import sys
import csv
import argparse
import datetime

MASTER_FILE = 'master_product_list.csv'
ROOT_DIR = '..'
OUTPUT_DIR = 'converted_csvs'
INPUT_DIR = 'product_lists'

def run(input_filename, target_filename):
	i = datetime.datetime.now()
	f, e = os.path.splitext(input_filename)
	out = f + '_{}_{}_{}_{}_{}'.format(
					  i.month, i.day, i.year, i.hour, i.minute) + e
	root_dir = os.path.abspath(os.path.join(os.getcwd(), ROOT_DIR))
	in_file = os.path.join(root_dir, INPUT_DIR, input_filename)
	output_filename = os.path.join(root_dir, OUTPUT_DIR, out)
	print 'Opening {}...'.format(in_file)
	print 'Saving output file as {}...'.format(output_filename)

	out_header = []
	reordered_header = []

	out_dir = os.path.join(root_dir, OUTPUT_DIR)
	if not os.path.exists(out_dir):
		os.makedirs(out_dir)

	try:
		with open(target_filename, 'r') as ft:
			target_csv = csv.reader(ft)
			out_header = target_csv.next()[1:]
			reordered_header = [r for r in target_csv if input_filename in r]
			if len(reordered_header) > 1:
				print 'ERROR: multiple csv files with same name ({})'.format(
						input_filename)
				sys.exit(1)
			if len(reordered_header) == 0:
				print 'ERROR: no csv files with name {}'.format(input_filename)
				sys.exit(1)
			reordered_header = reordered_header[0][1:]
		ft.close()
	except:
		print 'ERROR: Could not open {}'.format(target_filename)
		sys.exit(1)
	try:
		with open(in_file, 'r') as fi, open(output_filename, 'w') as fo:
			in_csv = csv.reader(fi)
			writer = csv.DictWriter(fo, fieldnames=reordered_header)
			header = csv.DictWriter(fo, fieldnames=out_header)
			header.writeheader()
			for r in csv.DictReader(fi):
				writer.writerow(r)
		fi.close()
		fo.close()
	except:
		print 'ERROR: Could not open {} or create {}'.format(in_file, output_filename)
		sys.exit(1)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--input_filename', nargs=1,
						help='Filename to parse')
	parser.add_argument('-t', '--target_filename', nargs=1,
						help='Filename to match', default=[MASTER_FILE])
	args = parser.parse_args()

	run(args.input_filename[0], args.target_filename[0])
