#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
Created on 2019/8/7 

@author: tmy
"""
from lib import *

import javalang
import javalang.tree
tree = javalang.parse.parse("package javalang.brewtab.com; class Test {}")
a = 1