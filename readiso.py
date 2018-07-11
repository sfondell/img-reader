# Sophia Fondell
# 7/11/18
# A script that accepts an iso file as arg and prints out the image's filesystem

import hachoir
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
	path = build_path(args.image)
	