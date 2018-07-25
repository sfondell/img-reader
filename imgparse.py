# Script to parse iso filesystems
# Required functionality:
# 1. List all files in iso filesystem
# 2. List files in specified iso filesystem directory
# 3. Search for specified file in all of iso filesystem
# 4. Search for specified file in specified iso filesystem directory

import pycdlib
import argparse
import os
import shutil
import glob
import subprocess

try:
	from cStringIO import StringIO as BytesIO
except ImportError:
	from io import BytesIO

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
		self.iso = mount(self.filename)
		squashimg = os.path.join(self.iso, 'LiveOS/squashfs.img')
		self.squashfs = mount(squashimg)
		rootimg = os.path.join(self.squashfs, 'LiveOS/rootfs.img')
		self.rootfs = mount(rootimg)
		return self

	def __exit__(self, exception_type, exception_value, traceback):
		'''Context manager method for unmounting nested disk images with required params'''
		for mount in (self.rootfs, self.squashfs, self.iso):
			if mount is not None:
				umount()


def build_path(img_name):
	'''A function to build the full path to the specified iso file'''
	cwd = os.getcwd()
	path = cwd + '/' + img_name
	return path

def mount(img_path):
	'''A function to encapsulate mounting a disk image'''
	mount_str = 'sudo mount -o loop ' + img_path + ' /mnt'
	os.system(mount_str)
	return '/mnt'

def umount():
	'''A function to encapsulate unmounting a disk image'''
	umount_str = 'sudo umount /mnt'
	os.system(umount_str)

def iter_files(rootdir):
	'''A function to iterate through a specified param rootdir using os.walk'''
	for root, dirs, files in os.walk(rootdir):
		for f in files:
			yield os.path.join(root, f)

def iter_fileglobs(rootdir, fileglobs):
	'''A function to iterate through fileglobs in a specified param rootdir'''
	for fileglob in fileglobs:
		for f in glob.glob(os.path.join(rootdir, fileglob.lstrip('/'))):
			yield f

def get_packages(rootdir):
	'''A function to return all of the packages installed in a disk image'''
	pkgs = subprocess.check_output(['rpm', '--root', '/mnt', '-qa'])
	pkglist = pkgs.decode('utf-8').split('\\')
	return pkglist

def init_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('liveiso', help='filename of live image to be parsed')

	modes = parser.add_mutually_exclusive_group(required=True)
	modes.add_argument('--list-all', action='store_true',
					help='list all files in the image\'s rootfs image filesystem')
	modes.add_argument('--ls', metavar='FILEGLOB', nargs='+',
					help='list the given FILEGLOBS')
	modes.add_argument('--list-pkgs', action='store_true',
					help='list all packages installed in the image')

	return parser

if __name__ == '__main__':
	parser = init_parser()
	args = parser.parse_args()

	with MountedImage(args.liveiso) as live:
		if args.list_all:
			imgdata = list(iter_files(live.rootfs))
		elif args.ls:
			imgdata = list(iter_fileglobs(live.rootfs, args.ls))
		elif args.list_pkgs:
			imgdata = get_packages(live.rootfs)
		else:
			# This should never be reached because of the parser object
			pass

		if len(imgdata) == 0:
			if (args.list_all or args.ls):
				parser.error('no matching files found')
			else:
				parser.error('no matching packages found')

		for f in imgdata:
			outf = f[len(live.rootfs):]
			print(outf)