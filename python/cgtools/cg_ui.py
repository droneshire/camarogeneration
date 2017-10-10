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

import logger

class CgUi(object, Frame):
	ROOT_DIR = util.get_data_folder()
	LOG_DIR = 'logs'
	IMG_DIR = 'ui_images'
	LOGO = 'logo.jpg'
	THUMBNAILS = {'-0':0, '-1':0, '-2T':0, '-2':0}

	def __init__(self):
		log_dir = os.path.join(util.default_root_dir(), self.LOG_DIR)
		if not os.path.exists(log_dir):
					os.makedirs(log_dir)
		LOG_FILE= os.path.join(log_dir, '{}.log'.format(__file__))
		self.log = logger.get_logger(__file__, LOG_FILE)

		Frame.__init__(self, name='camaro_gen_tool')
		self.master.title('Camaro Generation File Tool')
		self.pack(expand=Y, fill=BOTH)

		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.ftp_popup = None

		# Visual separation in the log
		self.log.info('Log Start')

		# File dialogs
		self.ifile_var = StringVar()
		self.pfile_var = StringVar()
		self.do_erase = IntVar()
		self.do_copy_original = IntVar()
		self.do_copy_pdf = IntVar()
		self.size0 = IntVar()
		self.size1 = IntVar()
		self.size2t = IntVar()
		self.size2 = IntVar()

		self.size0.set(50)
		self.size1.set(100)
		self.size2t.set(150)
		self.size2.set(500)


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

		# Create input folders if not already there
		dirs = []
		root_dir = os.path.abspath(os.path.join(os.getcwd(), ScrapeImages.ROOT_DIR))
		dirs.append(os.path.join(root_dir, ScrapeImages.INPUT_DIR))
		dirs.append(os.path.join(root_dir, ReorderCsv.INPUT_DIR))
		dirs.append(os.path.join(root_dir, ScrapeImages.IMG_LIST_DIR))
		for dir in dirs:
			util.make_sure_path_exists(dir)

		# Create UI
		self.create_panel()

	def create_panel(self):
		panel = Frame(self, name='panel')
		panel.pack(side=TOP, fill=BOTH, expand=Y)

		# create the notebook
		nb = Notebook(panel, name='notebook')
		menubar = Menu(panel)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="Update Home Directory", command=self.update_home_dir)
		filemenu.add_separator()
		filemenu.add_command(label="Exit", command=self.master.quit)
		menubar.add_cascade(label="File", menu=filemenu)
		menubar.add_command(label="Help", command=self.display_help)
		self.master.config(menu=menubar)

		# extend bindings to top level window allowing
		#   CTRL+TAB - cycles thru tabs
		#   SHIFT+CTRL+TAB - previous tab
		#   ALT+K - select tab using mnemonic (K = underlined letter)
		nb.enable_traversal()
		nb.pack(fill=BOTH, expand=Y, padx=2, pady=3)

		self.create_image_tab(nb)
		self.create_csv_process_tab(nb)


	def update_home_dir(self):
		hdir = Toplevel()
		hdir.title('Set Home Directory')
		hdir.focus_force()
		util.SetHomeDir(hdir, hdir.destroy)

	def display_help(self):
		helpmsg = ''
		with open('README.md', 'r') as f:
			for l in f:
				helpmsg += l
		help = Toplevel()
		help.title('Help')
		help.focus_force()
		l = Label(help, text=helpmsg,
			wraplength=500, anchor=W, justify=LEFT)
		l.grid(row=1, column=0)
		cbtn = Button(help, text="OK", command=help.destroy, padding='5 5 5 5')
		cbtn.grid(row=2 , column=0)


	def create_image_tab(self, nb):
		# frame to hold contentx
		frame = Frame(nb)

		starting_row = 0
		starting_column = 0
		self.add_logo(frame, starting_row + 2)

		icsv=Label(frame, text="Image List CSV").grid(row=starting_row, column=starting_column)
		bar1=Entry(frame, textvariable=self.ifile_var, width=40).grid(
					row=starting_row, column=starting_column+1,columnspan=4, rowspan=1)

		#Buttons
		bbutton= Button(frame, text="Browse", command=self.browseimgcsv)
		bbutton.grid(row=starting_row, column=starting_column+5, padx=5, pady=5, sticky=W+E)

		eb= Button(frame, text="Process Image List", command=self.scrape_imgs_handle)
		eb.grid(row=starting_row+1, column=starting_column+5, sticky = W + E, padx=5, pady=5)

		fb = Button(frame, text='Setup FTP', command=self.set_ftp)
		fb.grid(row=starting_row+2, column=starting_column+5, sticky = W + E, padx=5, pady=5)

		# cb = Button(frame, text="Close", command=self.master.quit)
		# cb.grid(row=starting_row+3 , column=starting_column+5, sticky = W + E, padx=5, pady=5)

		# Image sizing
		entry_width = 3

		rb = Checkbutton(frame, text='Erase Images', variable=self.do_erase)
		rb.grid(row=starting_row+1, column=starting_column+3, sticky=W, padx=5, pady=5,columnspan=2)
		rb = Checkbutton(frame, text='Include Original', variable=self.do_copy_original)
		rb.grid(row=starting_row+1, column=starting_column+1, padx=5, pady=5,columnspan=2)
		rb = Checkbutton(frame, text='Include PDF', variable=self.do_copy_pdf)
		rb.grid(row=starting_row+1, column=starting_column, sticky=E, padx=5, pady=5,columnspan=1)



		image_sizing_row_start = starting_row+2
		image_sizing_column = starting_column+1
		lsize0=Label(frame, text="Photo Size 0 (Width)").grid(
					row=image_sizing_row_start, column=image_sizing_column, sticky = E)
		bsize0 =Entry(frame, textvariable=self.size0, width=entry_width).grid(
					row=image_sizing_row_start, column=image_sizing_column+1, sticky = W, padx=5, pady=5)
		lsize1=Label(frame, text="Photo Size 1 (Width)").grid(row=image_sizing_row_start+1, column=image_sizing_column, sticky = E)
		bsize1 =Entry(frame, textvariable=self.size1, width=entry_width).grid(
					row=image_sizing_row_start+1, column=image_sizing_column+1, sticky = W, padx=5, pady=5)

		lsize2t=Label(frame, text="Photo Size 2T (Width)").grid(row=image_sizing_row_start, column=image_sizing_column+2, sticky = E)
		bsize2t =Entry(frame, textvariable=self.size2t, width=entry_width).grid(
					row=image_sizing_row_start, column=image_sizing_column+3, sticky = W, padx=5, pady=5)
		lsize2 =Label(frame, text="Photo Size 2 (Width)").grid(row=image_sizing_row_start+1, column=image_sizing_column+2, sticky = E)
		bsize2 =Entry(frame, textvariable=self.size2, width=entry_width).grid(
					row=image_sizing_row_start+1, column=image_sizing_column+3, sticky = W, padx=5, pady=5)

		frame.rowconfigure(1, weight=1)
		frame.columnconfigure((0,1), weight=1, uniform=1)

		# add to notebook (underline = index for short-cut character)
		nb.add(frame, text='Process Images', underline=0, padding=2)

	def create_csv_process_tab(self, nb):
		# frame to hold contentx
		frame = Frame(nb)

		starting_row = 0

		self.add_logo(frame, starting_row + 2)

		reordercsv=Label(frame, text="Product List CSV").grid(row=starting_row, column=0)
		bar2=Entry(frame, textvariable=self.pfile_var, width=50).grid(
					row=starting_row, column=1, columnspan=4, rowspan=1)

		#Buttons
		self.bbutton1= Button(frame, text="Browse", command=self.browseproductcsv)
		self.bbutton1.grid(row=starting_row, column=5, padx=5, sticky = W+E)

		self.cbutton1= Button(frame, text="Process Product List", command=self.reorder_csv_handle)
		self.cbutton1.grid(row=starting_row+1, column=5, sticky = W+E, padx=5, pady=5)

		# self.close_button = Button(frame, text="Close", command=self.master.quit)
		# self.close_button.grid(row=starting_row+2 , column=5, sticky = W+E, padx=5, pady=5)

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
		logo.grid(row=row, column=0, sticky=N+S+E+W, columnspan=1, rowspan=4)

	def update_img_list_csv(self):
		self.ifile_var.set(self.img_list_file)

	def update_product_list_csv(self):
		self.pfile_var.set(self.product_list_file)

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
			wraplength=300, anchor=W, justify=CENTER)
		popup.grid(row=1, column=0)
		Label(err, text="").grid(row=3, column=0)
		self.err_count +=1
		err.focus_force()
		self.log.error(err_msg)

	def popup_success(self, msg):
		success = Toplevel()
		success.title('SUCCESS')
		cbtn = Button(success, text="OK", command=success.destroy, padding='5 5 5 5')
		cbtn.grid(row=2 , column=0)
		self.popup = Label(success, text=msg,
			wraplength=300, anchor=W, justify=CENTER)
		self.popup.grid(row=1, column=0)
		Label(success, text="").grid(row=3, column=0)
		success.focus_force()
		self.log.info(msg)


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
			self.THUMBNAILS['-0'] = self.size0.get()
			self.THUMBNAILS['-1'] = self.size1.get()
			self.THUMBNAILS['-2T'] = self.size2t.get()
			self.THUMBNAILS['-2'] = self.size2.get()
			if sum(1 for x in self.THUMBNAILS.values() if x == 0) == len(self.THUMBNAILS):
				thumbnail_sizes = None
				print 'None'
			else:
				thumbnail_sizes = self.THUMBNAILS
			ScrapeImages(self.img_list_file, imgdir, self.do_erase.get(), self.do_copy_original.get(),
				self.do_copy_pdf.get(), self.session, self.popup_err, thumbnail_sizes).parse_images()
			if err_count == self.err_count:
				self.popup_success('SUCCESS: Images parsed')
		else:
			self.popup_err('ERROR: No csv file selected')

	def reorder_csv_handle(self):
		if self.product_list_file:
			masterfile = os.path.abspath(os.path.join(
				os.getcwd(), ReorderCsv.ROOT_DIR, ReorderCsv.MASTER_FILE))
			err_count = self.err_count
			ReorderCsv(self.product_list_file, masterfile, self.popup_err).reorder()
			if err_count == self.err_count:
				self.popup_success('SUCCESS: Reordered product csv')
		else:
			self.popup_err('ERROR: No csv file selected')

if __name__ == "__main__":
	CgUi().mainloop()
	for f in glob.glob("*.pyc"):
		os.remove(f)

