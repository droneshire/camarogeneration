# camarogeneration
File management and image parsing.

## To Reorder a CSV File:
1) Open master_product_list.csv

2) On a new line, type in the filename of the list you want to reorder

3) For each of columns, match the header from your input file to golden header

4) Run the tool (can use the batch script provided) or run python cg_ui.py

5) Go to the 'Process CSV' tab. Browse for CSV and click 'Process Product List'

6) The reordered csv file will be placed into the converted_csvs folder with the same name as the input file only with a timestamp added to it. E.g. if input filename was input.csv, the output will be input_4_15_2017_16_53.csv

## To Parse Images from CSV File List:
1) Create an image csv file. This needs to have a column in it with "Image File Names"

2) Place image csv file into the image_lists folder

3) Place images into the images folder

4) Run the tool (can use the batch script provided) or run python cg_ui.py

5) Browse for the image list CSV

6) If you want images erased after being processed, check the 'Erase Images' checkbox

7) If you want thumbnails, set the widths as desired

8) Click 'Process Image List'

9) The correct images will be copied into the parsed_images folder.  All images will be erased from the images folder once the correct ones have been copied.
