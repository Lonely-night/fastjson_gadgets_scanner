#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
Created on 2019/8/7 

@author: tmy
"""
from lib import *

#
if __name__ == '__main__':
    source_dir = "/Users/xxxxxxx/source/"
    file_list = os.listdir(source_dir)
    num = 1
    for _file in file_list:
        file = os.path.join(source_dir, _file)

        if os.path.isfile(file):
            continue
        files = get_java_file(file)
        for _file in files:
            print _file
            num += 1
            scanner(_file)

    print num






