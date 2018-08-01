# Script to parse iso filesystems
# Required functionality:
# 1. List all files in iso filesystem
# 2. List files in specified iso filesystem directory
# 3. Search for specified file in all of iso filesystem
# 4. Search for specified file in specified iso filesystem directory

import argparse
import os
import glob
import subprocess
from hurry.filesize import size

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

def mount(img_path):
	'''A function to encapsulate mounting a disk image'''
	subprocess.run(['sudo', 'mount', '-o', 'loop', img_path, '/mnt'])
	return '/mnt'

def umount():
	'''A function to encapsulate unmounting a disk image'''
	subprocess.run(['sudo', 'umount', '/mnt'])

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
	pkgs = pkgs.decode('utf-8')
	pkglist = pkgs.split("\n")
	return pkglist

def get_diskusage(rootdir):
	'''A function that finds the total disk usage of each installed rpm and returns as a sorted 
	list of tuples of package name and disk usage from most to least'''
	pkglist = get_packages(rootdir)
	pkgdict = {}
	for i in pkglist:
		pkgdict[i] = 0
	for root, dirs, files in os.walk(rootdir):
		for f in files:
			try:
				pkg = subprocess.check_output(['rpm', '--root', '/mnt', '-qf', os.path.join(root, f)[4:]], stderr=subprocess.DEVNULL)
				pkg = pkg.decode('utf-8')[:-1]
				if ("\n" in pkg):
					lst = pkg.split("\n")
					for i in lst:
						pkgdict[i] += os.path.getsize(os.path.join(root, f))
				else:
					pkgdict[pkg] += os.path.getsize(os.path.join(root, f))
			except Exception:
				# The file is not owned by any specific package so we can ignore it
				pass

	sortedpkgs = [(i, pkgdict[i]) for i in sorted(pkgdict, key=pkgdict.get, reverse=True)]
	return sortedpkgs[:25]

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
	modes.add_argument('--list-usg', action='store_true',
					help='list the disk usage of the 25 largest rpms installed in the iso')

	return parser

if __name__ == '__main__':
	parser = init_parser()
	args = parser.parse_args()

	with MountedImage(args.liveiso) as live:
		result = []
		if args.list_all:
			filenames = list(iter_files(live.rootfs))
			result.append(filenames)
		elif args.ls:
			filenames = list(iter_fileglobs(live.rootfs, args.ls))
			result.append(filenames)
		elif args.list_pkgs:
			pkgs = get_packages(live.rootfs)
			result.append(pkgs)
		elif args.list_usg:
			usg = get_diskusage(live.rootfs)
			result.append(usg)
		else:
			# This should never be reached because of the parser object
			pass

		if len(result[0]) == 0:
			if (args.list_all or args.ls):
				parser.error('no matching files found')
			elif args.list_pkgs:
				parser.error('no matching packages found')
			else:
				parser.error('Could not find rpm disk image usage')


		if (args.list_usg):
			print('\n25 largest installed packages\n###############################\n')
			for tup in result[0]:
				print(tup[0], ':', size(tup[1]))
			print('\n###############################')
		else:
			for f in result[0]:
				print(f)