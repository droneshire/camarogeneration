#!/usr/bin/python


from Tkinter import *
from ttk import *
from PIL import ImageTk, Image
import os
import sys
import glob

from reorder_csv import ReorderCsv
from scrape_images import ScrapeImages
import erase_images
import util

FTP_SERVER_ADDR = 'gmqjl.sgamh.servertrust.com'

import logger
LOG_FILE= './logs/{}.log'.format(__name__)
log = logger.get_logger(__name__, LOG_FILE)

class CgGui(object, Frame):
	ROOT_DIR = '.'
	UI_DIR = 'ui'
	IMG_DIR = os.path.join(UI_DIR,'images')
	LOGO = 'cg_logo.jpg'

	def __init__(self):
		Frame.__init__(self, name='camaro_gen_tool')
		self.master.title('Camaro Generation File Tool')
		self.pack(expand=Y, fill=BOTH)

		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.ftp_popup = None

		# Visual separation in the log
		log.info('Log Start')

		# File dialogs
		self.ifile_var = StringVar()
		self.pfile_var = StringVar()
		self.do_erase = IntVar()

		self.session = None
		self.server = StringVar()
		self.user = StringVar()
		self.pwd = StringVar()
		self.server.set('')
		self.user.set('')
		self.pwd.set('')
		self.thumbnail_listbox = None

		self.err_count = 0

		self.img_list_file = ''
		self.product_list_file = ''

		self.create_panel()

	def create_panel(self):
		panel = Frame(self, name='panel')
		panel.pack(side=TOP, fill=BOTH, expand=Y)

		# create the notebook
		nb = Notebook(panel, name='notebook')

		# extend bindings to top level window allowing
		#   CTRL+TAB - cycles thru tabs
		#   SHIFT+CTRL+TAB - previous tab
		#   ALT+K - select tab using mnemonic (K = underlined letter)
		nb.enable_traversal()
		nb.pack(fill=BOTH, expand=Y, padx=2, pady=3)

		self.create_image_tab(nb)
		self.create_csv_process_tab(nb)

	def create_image_tab(self, nb):
		# frame to hold contentx
		frame = Frame(nb)

		starting_row = 2
		self.add_logo(frame, starting_row + 3)

		icsv=Label(frame, text="Image List CSV").grid(row=starting_row, column=0)
		bar1=Entry(frame, textvariable=self.ifile_var, width=50).grid(
					row=starting_row, column=1,columnspan=3, rowspan=1)

		#Buttons
		bbutton= Button(frame, text="Browse", command=self.browseimgcsv)
		bbutton.grid(row=starting_row, column=4, padx=10, sticky = W)

		eb= Button(frame, text="Process Image List", command=self.scrape_imgs_handle)
		eb.grid(row=starting_row+2, column=3, sticky = W + E, padx=5, pady=5, columnspan=2, rowspan=1)

		fb = Button(frame, text='Setup FTP', command=self.set_ftp)
		fb.grid(row=starting_row+3, column=3, sticky = W + E, padx=5, pady=5,columnspan=2, rowspan=1)

		rb = Checkbutton(frame, text='Erase Images After Parsing', variable=self.do_erase)
		rb.grid(row=starting_row+2, column=2, sticky = S + W, padx=5, pady=5)

		cb = Button(frame, text="Close", command=self.master.quit)
		cb.grid(row=starting_row+4 , column=3, sticky = W + E, padx=5, pady=5, columnspan=2, rowspan=1)

		# Image sizing
		icsv=Label(frame, text="Thumbnail Width Size").grid(
					row=starting_row+2, column=1, sticky = S)
		scrollbar = Scrollbar(frame, orient=VERTICAL)
		self.thumbnail_listbox =Listbox(frame, selectmode=MULTIPLE, yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.thumbnail_listbox.yview)
		self.thumbnail_listbox.grid(row=starting_row+3, column=1, sticky = W, padx=5, pady=5, columnspan=1, rowspan=3)

		for i in range(10):
			self.thumbnail_listbox.insert(END, str((i+1) * 50))

		frame.rowconfigure(1, weight=1)
		frame.columnconfigure((0,1), weight=1, uniform=1)

		# add to notebook (underline = index for short-cut character)
		nb.add(frame, text='Process Images', underline=0, padding=2)

	def create_csv_process_tab(self, nb):
		# frame to hold contentx
		frame = Frame(nb)

		starting_row = 1

		self.add_logo(frame, starting_row + 2)

		reordercsv=Label(frame, text="Product List CSV").grid(row=starting_row, column=0)
		bar2=Entry(frame, textvariable=self.pfile_var, width=50).grid(
					row=starting_row, column=1, columnspan=3, rowspan=1)

		#Buttons
		self.bbutton1= Button(frame, text="Browse", command=self.browseproductcsv)
		self.bbutton1.grid(row=starting_row, column=4, padx=10, sticky = W)

		self.cbutton1= Button(frame, text="Process Product List", command=self.reorder_csv_handle)
		self.cbutton1.grid(row=starting_row+3, column=3, sticky = W + E, padx=5, pady=5, columnspan=2, rowspan=1)

		self.close_button = Button(frame, text="Close", command=self.master.quit)
		self.close_button.grid(row=starting_row+4 , column=3, sticky = W + E, padx=5, pady=5, columnspan=2, rowspan=1)

		frame.rowconfigure(1, weight=1)
		frame.columnconfigure((0,1), weight=1, uniform=1)

		# add to notebook (underline = index for short-cut character)
		nb.add(frame, text='Process CSV', underline=1, padding=2)

	def add_logo(self, master, row):
		# Logo
		img_file = os.path.join(self.root_dir, self.IMG_DIR, self.LOGO)
		img = ImageTk.PhotoImage(Image.open(img_file))
		logo = Label(master, image=img)
		logo.image = img
		logo.grid(row=row, column=0, columnspan=2, rowspan=3,
				  sticky=W+S)

	def update_img_list_csv(self):
		self.ifile_var.set(self.img_list_file)

	def update_product_list_csv(self):
		self.pfile_var.set(self.product_list_file)

	def cycle_label_text(self, event):
		self.label_index += 1
		self.label_index %= len(self.LABEL_TEXT) # wrap around
		self.label_text.set(self.LABEL_TEXT[self.label_index])

	def browseimgcsv(self):
		self.img_list_file = self.browsefile()
		self.update_img_list_csv()

	def browseproductcsv(self):
		self.product_list_file = self.browsefile()
		self.update_product_list_csv()

	def browsefile(self):
		from tkFileDialog import askopenfilename
		Tk().withdraw()
		return askopenfilename()

	def popup_err(self, err_msg):
		err = Toplevel()
		err.title('ERROR')
		cbtn = Button(err, text="OK", command=err.destroy, padding='5 5 5 5')
		cbtn.grid(row=2 , column=0)
		popup = Label(err, text=err_msg,
			wraplength=200, anchor=W, justify=CENTER)
		popup.grid(row=1, column=0)
		Label(err, text="").grid(row=3, column=0)
		self.err_count +=1
		err.focus_force()
		log.error(err_msg)

	def popup_success(self, msg):
		success = Toplevel()
		success.title('SUCCESS')
		cbtn = Button(success, text="OK", command=success.destroy, padding='5 5 5 5')
		cbtn.grid(row=2 , column=0)
		self.popup = Label(success, text=msg,
			wraplength=200, anchor=W, justify=CENTER)
		self.popup.grid(row=1, column=0)
		Label(success, text="").grid(row=3, column=0)
		success.focus_force()
		log.info(msg)


	def set_ftp(self):
		self.ftp_popup = Toplevel()
		self.ftp_popup.title('Setup FTP')

		server=Label(self.ftp_popup, text="FTP Server").grid(row=0, column=0)
		Entry(self.ftp_popup, textvariable=self.server, width=50).grid(
					row=0, column=1,columnspan=2, rowspan=1)
		user=Label(self.ftp_popup, text="FTP Username").grid(row=1, column=0)
		Entry(self.ftp_popup, textvariable=self.user, width=50).grid(
					row=1, column=1,columnspan=2, rowspan=1)
		pwd=Label(self.ftp_popup, text="FTP Password").grid(row=2, column=0)
		Entry(self.ftp_popup, textvariable=self.pwd, width=50).grid(
					row=2, column=1,columnspan=2, rowspan=1)

		okbtn = Button(self.ftp_popup, text="Connect", command=self.process_ftp)
		okbtn.grid(row=3 , column=1, sticky = W + E,columnspan=2, rowspan=1)
		cbtn = Button(self.ftp_popup, text="Close", command=self.ftp_popup.destroy)
		cbtn.grid(row=4 , column=1, sticky = W + E,columnspan=2, rowspan=1)

		self.ftp_popup.focus_force()

	def process_ftp(self):
		print self.server.get(), self.user.get(), self.pwd.get()
		if self.server.get():
			try:
				print('Connecting to {}...'.format(self.server.get()))
				self.session = ftplib.FTP(self.server.get())
				self.session.login(self.user.get(), self.pwd.get())
				self.popup_success('Connected to {}'.format(self.server.get()))
			except:
				print('Could not connect to {}'.format(self.server.get()))
				self.session = None
				self.popup_err('ERROR: Could not connect to {}'.format(self.server.get()))
		self.ftp_popup.destroy()
		self.server.set('')
		self.user.set('')
		self.pwd.set('')

	def scrape_imgs_handle(self):
		if self.img_list_file:
			imgdir = os.path.abspath(os.path.join(
					os.getcwd(), ScrapeImages.ROOT_DIR, ScrapeImages.INPUT_DIR))
			err_count = self.err_count
			thumbnail_sizes = [(x+1) * 50 for x in list(self.thumbnail_listbox.curselection())]
			ScrapeImages(self.img_list_file, imgdir, self.do_erase.get(), self.session,
						self.popup_err, thumbnail_sizes).parse_images()
			if err_count == self.err_count:
				self.popup_success('SUCCESS: Images parsed')
		else:
			self.popup_err('ERROR: No csv file selected')

	def reorder_csv_handle(self):
		if self.product_list_file:
			masterfile = os.path.abspath(os.path.join(os.getcwd(), ReorderCsv.MASTER_FILE))
			err_count = self.err_count
			ReorderCsv(self.product_list_file, masterfile, self.popup_err).reorder()
			if err_count == self.err_count:
				self.popup_success('SUCCESS: Reordered product csv')
		else:
			self.popup_err('ERROR: No csv file selected')

if __name__ == "__main__":
	CgGui().mainloop()
	for f in glob.glob("*.pyc"):
		os.remove(f)

