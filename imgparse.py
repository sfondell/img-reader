# Script to parse iso filesystems
# Required functionality:
# 1. List all files in iso filesystem
# 2. List files in specified iso filesystem directory
# 3. Search for specified file in all of iso filesystem
# 4. Search for specified file in specified iso filesystem directory

import os
import argparse

def mount(ing_name):
    '''A function to encapsulate mounting a disk image file'''
    mount_str = 'sudo mount -o loop ' + img_name + ' /mnt'
    os.system(mount_str)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a disk image\'s filesystem')
    parser.add_argument('image', metavar='img', type=str, help='image to be parsed')
    parser.add_argument('cmd', metavar='cmd', type=str, help='
