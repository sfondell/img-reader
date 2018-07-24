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

def init_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument('liveiso', help='filename of live image to be parsed')

	modes = parser.add_mutually_exclusive_group(required=True)
	modes.add_argument('--list-all', action='store_true',
					help='list all files in the image\'s rootfs image filesystem')
	modes.add_argument('--ls', metavar='FILEGLOB', nargs='+',
					help='list the given FILEGLOBS')

	return parser

if __name__ == '__main__':
	parser = init_parser()
	args = parser.parse_args()

	with MountedImage(args.liveiso) as live:
		if args.list_all:
			filenames = list(iter_files(live.rootfs))
		elif args.ls:
			filenames = list(iter_fileglobs(live.rootfs, args.ls))
		else:
			assert('allegedly should never happen')

		if len(filenames) == 0:
			parser.error('no files found')

		for f in filenames:
			outf = f[len(live.rootfs):]
			print(outf)

	# parser = argparse.ArgumentParser(description='Search a disk image\'s filesystem for a specified executable.')
	# parser.add_argument('image', metavar='img', type=str, help='an image to be read')
	# parser.add_argument('cmd', metavar='cmd', type=str, help='executable command/file to search for in iso file')
	# args = parser.parse_args()
	# path = build_path(args.image) # Is this necesary? Full path not needed if in cwd
	
	# # DECLARE NEW ISO OBJECT AND INITIALIZE BY OPENING FILE SPECIFIED IN ARGS
	# iso = pycdlib.PyCdlib()
	# iso.open(args.image)

	# # PRINT ALL FILE IDENTIFIERS IN ROOT DIRECTORY (DEBUGGGING PURPOSES)
	# for child in iso.list_children(iso_path='/'):
	# 	print(child.file_identifier())

	# print()

	# # PRINT ALL FILE IDENTIFIERS IN LIVEOS DIRECTORY (DEBUGGING PURPOSES)
	# for child in iso.list_children(iso_path='/LIVEOS'):
	# 	print(child.file_identifier())

	# # EXTRACT SQUASHFS.IMG FROM ISO AND THEN OPEN IT LOCALLY AND READ CHILDREN FILE IDENTIFIERS
	# extracted_img = BytesIO()
	# iso.get_file_from_iso_fp(extracted_img, iso_path='/LIVEOS/SQUASHFS.IMG;1')
	
	# # WRITE BINARYIO OBJECT HOLDING SQUASHFS.IMG TO AN ISO IN CWD
	# extracted_img.seek(0)
	# with open('squashfs.img', 'wb') as f:
	# 	shutil.copyfileobj(extracted_img, f)

	# # CLOSE ORIGINAL BOOT.ISO
	# iso.close()

	# # RUN COMMANDS TO MOUNT AS WE CAN'T OPEN SQUASHFS.IMG USING THIS LIBRARY
	# os.system('sudo mount -o loop squashfs.img /mnt')

	# # GET ORIGINAL DIRECTORY BEFORE WE CD AND MOVE ROOTFS.IMG BACK TO ORIGINAL WD
	# owd = os.getcwd()
	# os.chdir('/mnt/LiveOS/')
	# copy_str = 'cp rootfs.img ' + owd
	# os.system(copy_str)

	# # SWITCH BACK TO ORIGINAL DIRECTORY TO REMOVE SQUASHFS.IMG FROM MOUNT & MOUNT ROOTFS.IMG
	# os.chdir(owd)
	# os.system('sudo umount /mnt')
	# os.system('sudo mount -o loop rootfs.img /mnt')

	# # CHANGE DIRECTORY TO /MNT SO WE CAN LOOK AT THE ISO'S FILESYSTEM
	# os.chdir('/mnt')
	# sbin = os.listdir('/usr/sbin')
	# if (args.cmd in sbin):
	# 	print('%s is present in the specified iso: %s' % (args.cmd, args.image))
	# else:
	# 	print('ERROR: %s is missing from the specified iso: %s' % (args.cmd, args.image))

	# # UNMOUNT ROOTFS AND DELETE BOTH INTERMEDIATE IMG FILES
	# os.chdir(owd)
	# os.system('sudo umount /mnt')
	# os.remove('squashfs.img')
	# os.remove('rootfs.img')
	