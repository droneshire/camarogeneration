#!/usr/bin/python


from Tkinter import *
from PIL import ImageTk, Image
import os
import sys

from reorder_csv import ReorderCsv
from scrape_images import ScrapeImages
from scrape_images import path_leaf, my_print
import erase_images

FTP_SERVER_ADDR = 'gmqjl.sgamh.servertrust.com'

class CgGui(object):
	ROOT_DIR = '.'
	UI_DIR = 'ui'
	IMG_DIR = os.path.join(UI_DIR,'images')
	LOGO = 'cg_logo.jpg'

	def __init__(self, master):
		self.master = master
		master.title('Camaro Generation File Tool')
		self.filename=""
		self.root_dir = os.path.abspath(os.path.join(os.getcwd(), self.ROOT_DIR))
		self.ftp_popup = None

		rows = 1
		# File dialogs
		self.ifile_var = StringVar()
		self.pfile_var = StringVar()
		self.do_erase = IntVar()

		imagcsv=Label(master, text="Image List CSV").grid(row=1, column=0)
		bar1=Entry(master, textvariable=self.ifile_var, width=50).grid(
					row=rows, column=1,columnspan=3, rowspan=1)

		reordercsv=Label(master, text="Product List CSV").grid(row=2, column=0)
		bar2=Entry(master, textvariable=self.pfile_var, width=50).grid(
					row=rows+1, column=1,columnspan=3, rowspan=1)

		#Buttons
		self.bbutton= Button(master, text="Browse", command=self.browseimgcsv)
		self.bbutton.grid(row=rows, column=4)

		self.bbutton1= Button(master, text="Browse", command=self.browseproductcsv)
		self.bbutton1.grid(row=rows+1, column=4)

		self.cbutton0= Button(master, text="Process Image List", command=self.scrape_imgs_handle)
		self.cbutton0.grid(row=rows+2, column=4, sticky = W + E)

		self.radiobtn = Checkbutton(master, text='Erase Images After', variable=self.do_erase)
		self.radiobtn.grid(row=rows+2, column=3, sticky = W)

		self.ftpsetupbtn = Button(master, text='Setup FTP', command=self.set_ftp)
		self.ftpsetupbtn.grid(row=rows+3, column=3, sticky = W)

		self.cbutton1= Button(master, text="Process Product List", command=self.reorder_csv_handle)
		self.cbutton1.grid(row=rows+3, column=4, sticky = W + E)

		self.close_button = Button(master, text="Close", command=master.quit)
		self.close_button.grid(row=rows+4 , column=4, sticky = W + E)

		# Logo
		img_file = os.path.join(self.root_dir, self.IMG_DIR, self.LOGO)
		img = ImageTk.PhotoImage(Image.open(img_file))
		logo = Label(master, image=img)
		logo.image = img
		logo.grid(row=3, column=0, columnspan=2, rowspan=3,
				  sticky=W+N+S, padx=5, pady=5)

		self.popup = None

		self.session = None
		self.server = StringVar()
		self.user = StringVar()
		self.pwd = StringVar()
		self.server.set('')
		self.user.set('')
		self.pwd.set('')

		self.img_list_file = ''
		self.product_list_file = ''

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
		toplevel = Toplevel()
		toplevel.title('ERROR')
		self.popup = Label(toplevel, text='ERROR: ' + err_msg,
			height=5, width=30)
		self.popup.grid(row=1, column=0)
		toplevel.focus_force()

	def popup_success(self, msg):
		toplevel = Toplevel()
		toplevel.title('SUCCESS')
		self.popup = Label(toplevel, text='SUCCESS: ' + msg,
			height=5, width=30)
		self.popup.grid(row=1, column=0)
		toplevel.focus_force()

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
			except:
				print('Could not connect to {}'.format(self.server.get()))
				self.session = None
				self.ftp_popup.destroy()
		self.server.set('')
		self.user.set('')
		self.pwd.set('')

	def scrape_imgs_handle(self):
		if self.img_list_file:
			print self.do_erase.get()
			imgdir = os.path.abspath(os.path.join(
					os.getcwd(), ScrapeImages.ROOT_DIR, ScrapeImages.INPUT_DIR))
			rc = ScrapeImages(self.img_list_file, imgdir, self.do_erase.get(), self.session
						).parse_images()
			self.popup_success('Images parsed')
		else:
			self.popup_err('No csv file selected')

	def reorder_csv_handle(self):
		if self.product_list_file:
			masterfile = os.path.abspath(os.path.join(os.getcwd(), ReorderCsv.MASTER_FILE))
			rc = ReorderCsv(self.product_list_file, masterfile).reorder()
			self.popup_success('Reordered product csv')
		else:
			self.popup_err('No csv file selected')

if __name__ == "__main__":
	root = Tk()
	my_gui = CgGui(root)
	root.mainloop()

