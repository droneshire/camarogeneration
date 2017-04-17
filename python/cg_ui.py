#!/usr/bin/python


from Tkinter import *
from PIL import ImageTk, Image
import os
import sys
import glob

from reorder_csv import ReorderCsv
from scrape_images import ScrapeImages
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
		self.cbutton0.grid(row=rows+2, column=4, sticky = W + E, padx=5, pady=5)

		self.radiobtn = Checkbutton(master, text='Erase Images After Parsing', variable=self.do_erase)
		self.radiobtn.grid(row=rows+2, column=3, sticky = W, padx=5, pady=5)

		self.ftpsetupbtn = Button(master, text='Setup FTP', command=self.set_ftp)
		self.ftpsetupbtn.grid(row=rows+3, column=3, sticky = W, padx=5, pady=5)

		self.cbutton1= Button(master, text="Process Product List", command=self.reorder_csv_handle)
		self.cbutton1.grid(row=rows+3, column=4, sticky = W + E, padx=5, pady=5)

		self.close_button = Button(master, text="Close", command=master.quit)
		self.close_button.grid(row=rows+4 , column=4, sticky = W + E, padx=5, pady=5)

		# Logo
		img_file = os.path.join(self.root_dir, self.IMG_DIR, self.LOGO)
		img = ImageTk.PhotoImage(Image.open(img_file))
		logo = Label(master, image=img)
		logo.image = img
		logo.grid(row=3, column=0, columnspan=2, rowspan=3,
				  sticky=W+N+S)

		self.session = None
		self.server = StringVar()
		self.user = StringVar()
		self.pwd = StringVar()
		self.server.set('')
		self.user.set('')
		self.pwd.set('')

		self.err_count = 0

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
		err = Toplevel()
		err.title('ERROR')
		cbtn = Button(err, text="OK", command=err.destroy,
					padx=5, pady=5)
		cbtn.grid(row=2 , column=0)
		popup = Label(err, text=err_msg,
			height=5, width=len(err_msg))
		popup.grid(row=1, column=0)
		Label(err, text="").grid(row=3, column=0)
		self.err_count +=1
		err.focus_force()

	def popup_success(self, msg):
		success = Toplevel()
		success.title('SUCCESS')
		cbtn = Button(success, text="OK", command=success.destroy,
						padx=5, pady=5)
		cbtn.grid(row=2 , column=0)
		self.popup = Label(success, text=msg,
			height=5, width=len(msg))
		self.popup.grid(row=1, column=0)
		Label(success, text="").grid(row=3, column=0)
		success.focus_force()


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
			ScrapeImages(self.img_list_file, imgdir, self.do_erase.get(), self.session,
						self.popup_err).parse_images()
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
	root = Tk()
	my_gui = CgGui(root)
	root.mainloop()
	for f in glob.glob("*.pyc"):
		os.remove(f)

