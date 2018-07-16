# Sophia Fondell
# 7/11/18
# A script that accepts an iso file as arg and prints out the image's filesystem

import pycdlib
import argparse
import os
import shutil

try:
	from cStringIO import StringIO as BytesIO
except ImportError:
	from io import BytesIO

def build_path(img_name):
	'''A function to build the full path to the specified iso file'''
	cwd = os.getcwd()
	path = cwd + '/' + img_name
	return path


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Read the contents of an iso disk image.')
	parser.add_argument('image', metavar='img', type=str, help='an image to be read')
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
	with open('squashfs.iso', 'wb') as f:
		shutil.copyfileobj(extracted_img, f)

	# CLOSE ORIGINAL BOOT.ISO
	iso.close()

	# OPEN SQUASHFS.ISO
	iso = pycdlib.PyCdlib()
	iso.open('squashfs.iso')

	# PRINT ALL FILE IDENTIFIERS IN ROOT DIRECTORY OF SQUASHFS.ISO
	for child in iso.list_children(iso_path='/'):
		print(child.file_identifier())
