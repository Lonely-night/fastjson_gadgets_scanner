#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
Created on 2019/8/10 

@author: tmy
"""
from lib import *


if __name__ == '__main__':
    m2_dir = "/Users/xxxxxxx/.m2/"
    jar_file_list = get_file_list(m2_dir)
    jar_file_list = clean(jar_file_list)
    decomplied_jar_list = read_file("./jar_list.txt")
    print("num:" + str(len(jar_file_list)))
    for jar_file in jar_file_list:
        if jar_file not in decomplied_jar_list:
            print jar_file
            write_file("./jar_list.txt", jar_file)
            decomplier(jar_file)
