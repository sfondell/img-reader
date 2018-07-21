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
		self.sqashfs = mount(squashimg)
		rootimg = os.path.join(self.squashfs, 'LiveOS/rootfs.img')
		self.rootfs = mount(rootimg)
		return self

	def __exit__(seldf, exception_type, exception_value, traceback):
		'''Context manager method unmounting nested disk images with required params'''
		for mount in (self.rootfs, self.squashfs, self.iso):
			if mount is not None:
				umount(mount)


def build_path(img_name):
	'''A function to build the full path to the specified iso file'''
	cwd = os.getcwd()
	path = cwd + '/' + img_name
	return path

def mount(img_name):
	'''A function to encapsulate mounting a disk image'''
	mount_str = 'sudo mount -o loop ' + img_name + ' /mnt/' + img_name[:-4]
	os.system(mount_str)

def umount(img_name):
	'''A function to encapsulate unmounting a disk image'''
	umount_str = 'sudo umount /mnt/' + img_name[:-4]
	os.system(umount_str)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Search a disk image\'s filesystem for a specified executable.')
	parser.add_argument('image', metavar='img', type=str, help='an image to be read')
	parser.add_argument('cmd', metavar='cmd', type=str, help='executable command/file to search for in iso file')
	args = parser.parse_args()
	path = build_path(args.image) # Is this necesary? Full path not needed if in cwd
	
	# DECLARE NEW ISO OBJECT AND INITIALIZE BY OPENING FILE SPECIFIED IN ARGS
	iso = pycdlib.PyCdlib()
	iso.open(args.image)

	# PRINT ALL FILE IDENTIFIERS IN ROOT DIRECTORY (DEBUGGGING PURPOSES)
	for child in iso.list_children(iso_path='/'):
		print(child.file_identifier())

	print()

	# PRINT ALL FILE IDENTIFIERS IN LIVEOS DIRECTORY (DEBUGGING PURPOSES)
	for child in iso.list_children(iso_path='/LIVEOS'):
		print(child.file_identifier())

	# EXTRACT SQUASHFS.IMG FROM ISO AND THEN OPEN IT LOCALLY AND READ CHILDREN FILE IDENTIFIERS
	extracted_img = BytesIO()
	iso.get_file_from_iso_fp(extracted_img, iso_path='/LIVEOS/SQUASHFS.IMG;1')
	
	# WRITE BINARYIO OBJECT HOLDING SQUASHFS.IMG TO AN ISO IN CWD
	extracted_img.seek(0)
	with open('squashfs.img', 'wb') as f:
		shutil.copyfileobj(extracted_img, f)

	# CLOSE ORIGINAL BOOT.ISO
	iso.close()

	# RUN COMMANDS TO MOUNT AS WE CAN'T OPEN SQUASHFS.IMG USING THIS LIBRARY
	os.system('sudo mount -o loop squashfs.img /mnt')

	# GET ORIGINAL DIRECTORY BEFORE WE CD AND MOVE ROOTFS.IMG BACK TO ORIGINAL WD
	owd = os.getcwd()
	os.chdir('/mnt/LiveOS/')
	copy_str = 'cp rootfs.img ' + owd
	os.system(copy_str)

	# SWITCH BACK TO ORIGINAL DIRECTORY TO REMOVE SQUASHFS.IMG FROM MOUNT & MOUNT ROOTFS.IMG
	os.chdir(owd)
	os.system('sudo umount /mnt')
	os.system('sudo mount -o loop rootfs.img /mnt')

	# CHANGE DIRECTORY TO /MNT SO WE CAN LOOK AT THE ISO'S FILESYSTEM
	os.chdir('/mnt')
	sbin = os.listdir('/usr/sbin')
	if (args.cmd in sbin):
		print('%s is present in the specified iso: %s' % (args.cmd, args.image))
	else:
		print('ERROR: %s is missing from the specified iso: %s' % (args.cmd, args.image))

	# UNMOUNT ROOTFS AND DELETE BOTH INTERMEDIATE IMG FILES
	os.chdir(owd)
	os.system('sudo umount /mnt')
	os.remove('squashfs.img')
	os.remove('rootfs.img')
	