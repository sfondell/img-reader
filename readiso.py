# Sophia Fondell
# 7/11/18
# A script that accepts an iso file as arg and prints out the image's filesystem

import pycdlib
import argparse
import os

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
	
	iso = pycdlib.PyCdlib()
	subdir = args.image + '/LIVEOS'
	iso.open(subdir)

	# for child in iso.list_children(iso_path='/LIVEOS'):
	# 	print(str(child.file_identifier()))

	# for child in iso.list_children(iso_path='/LIVEOS'):
	# 	if ('SQUASHFS.IMG' in str(child.file_indentifier())):
	# 		iso.open(child)

	# for child in iso.list_children(iso_path='/LIVEOS'):
	# 	idf = str(child.file_identifier())
	# 	if ('SQUASHFS.IMG' in idf):
	# 		subdir_iso = pycdlib.PyCdlib()
	# 		subdir_iso.open()
	# 		for subchild in subdir_iso.list_children(iso_path='/'):
	# 			print(subchild.file_identifier())
