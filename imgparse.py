# Script to parse iso filesystems
# Required functionality:
# 1. List all files in iso filesystem
# 2. List files in specified iso filesystem directory
# 3. Search for specified file in all of iso filesystem
# 4. Search for specified file in specified iso filesystem directory

import os
import argparse
import glob
from pylorax.imgutils import mount, umount

class MountedImage(object):
	'''A class to encapsulate the nested images in the boot.iso as one object with context manager methods'''
	def __init__(self, filename):
		'''Constructor for the MountedImage class'''
		self.filename = filename
		self.iso = None
		self.squashfs = None
		self.rootfs = None

	def __enter__(self):
		'''Context manager method for setting up filepaths and mounting the nested disk images'''
		self.iso = mount(self.filename, opts='ro,loop')
		squashimg = os.path.join(self.iso, 'LiveOS/squashfs.img')
		self.squashfs = mount(squashimg, opts='ro,loop')
		rootimg = os.path.join(self.squashfs, 'LiveOS/rootfs.img')
		self.rootfs = mount(rootimg, opts='ro,loop')
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		'''Context manager method for unmounting nested disk images with required params'''
		for mount in (self.rootfs, self.squashfs, self.iso):
			if mount is not None:
				umount(mount, lazy=True)

def iter_files(rootdir):
	'''Iterate through files & directories in param rootdir using os.walk()'''
	for root, dirs, files in os.walk(rootdir):
		for f in files:
			yield os.path.join(root, f)

def iter_fileglobs(rootdir, fileglobs):
	'''Iterate throgh fileglobs in specified param rootdir'''
	for fileglob in fileglobs:
		for f in glob.glob(os.path.join(rootdir, fileglob.lstrip('/'))):
			yield f

def init_parser():
	'''A function to initialize the flags and arguments for the commandline parser'''
	parser = argparse.ArgumentParser(description='Display the filesystem of an iso image')
	parser.add_argument('liveiso',
						help='file name of iso image to parse')
	