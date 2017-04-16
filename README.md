# camarogeneration
File management

To Reorder a CSV File:
1) Open master_product_list.csv

2) On a new line, type in the filename of the list you want to reorder

3) For each of columns, match the header from your input file to golden header

4) Run the following in the command line:
		cd C:\Users\Erika\Dropbox\camarogeneration\python
		python reorder_csv.py -f name_of_file.csv
	NOTE: the name_of_file.csv needs to match the filename
	      entered into the master_product_list.csv in step 2

5) The reordered csv file will be placed into the C:\Users\Erika\Dropbox\camarogeneration\converted_csvs\ folder with the same name as the input file only with a timestamp added to it. E.g. if input filename was input.csv, the output will be input_4_15_2017_16_53.csv

To Parse Images from CSV File List:
1) Create an image csv file. This needs to have a column in it with "Image File Names"

2) Place image csv file into the C:\Users\Erika\Dropbox\camarogeneration\image_lists folder

3) Place images into the C:\Users\Erika\Dropbox\camarogeneration\images folder

4) Run the following in the command line:
		cd C:\Users\Erika\Dropbox\camarogeneration\python
		python scrape_images.py -f name_of_image_list_file.csv
	NOTE: the name_of_image_list_file.csv needs to match the filename
	      of the file placed into the image_lists folder in step 1
	NOTE: if you want to upload via FTP, use the -u option at the end of the
		  command (i.e. python scrape_images.py -f name_of_image_list_file.csv -u)
        NOTE: if you want to erase the images after copying them, add the '-e' flag (i.e. python scrape_images.py -f name_of_image_list_file.csv -e)

5) The correct images will be copied into the C:\Users\Erika\Dropbox\camarogeneration\parsed_images folder.  All images will be erased from the C:\Users\Erika\Dropbox\camarogeneration\images folder once the correct ones have been copied.

To erase images after they are copied using scrape_images.py:
1) Run the following in the command line:
		cd C:\Users\Erika\Dropbox\camarogeneration\python
		python erase_images.py
WARNING: Make sure you use this erase script only AFTER you have copied over all files!
