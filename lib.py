#!/usr/bin/env python
# -*- coding: UTF-8 -*-


"""
Created on 2019/8/7 

@author: tmy
"""
import os
from javalang.parse import parse
from javalang.tree import *


black="""
org.apache.commons.collections4.comparators
org.python.core
org.apache.tomcat
org.apache.xalan
javax.xml
org.springframework.
org.apache.commons.beanutils
org.apache.commons.collections.Transformer
org.codehaus.groovy.runtime
java.lang.Thread
javax.net.
com.mchange
org.apache.wicket.util
java.util.jar.
org.mozilla.javascript
java.rmi
java.util.prefs.
com.sun.
java.util.logging.
org.apache.bcel
java.net.Socket
org.apache.commons.fileupload
org.jboss
org.hibernate
org.apache.commons.collections.functors
org.apache.myfaces.context.servlet
java.net.URL
junit.
org.apache.ibatis.datasource
org.osjava.sj.
org.apache.log4j.
org.logicalcobwebs.
org.apache.logging.
org.apache.commons.dbcp
com.ibatis.sqlmap.engine.datasource
org.jdom.
org.slf4j.
javassist.
oracle.net
org.jaxen.
java.net.InetAddress
java.lang.Class
com.alibaba.fastjson.annotation
org.apache.cxf.jaxrs.provider.
ch.qos.logback.
net.sf.ehcache.transaction.manager.
meituan
dianping
sankuai
maoyan
"""
black_list = black.strip().split("\n")


def get_file_list(path):
    """
    获取目录下所有文件
    :param path:
    :return:
    """
    path = os.path.abspath(path)
    _file_list = []

    if os.path.exists(path) is False:
        return _file_list

    file_list = os.listdir(path)
    for _file in file_list:
        file = os.path.join(path, _file)
        if os.path.isfile(file):
            if _file.endswith(".jar") and "javadoc" not in _file:
                _file_list.append(file)
        else:
            _file_list.extend(get_file_list(file))

    return _file_list


def get_java_file(source_path):
    if os.path.exists(source_path) is False:
        return []

    path = os.path.abspath(source_path)

    _file_list = []
    file_list = os.listdir(path)
    for _file in file_list:
        file = os.path.join(path, _file)
        if os.path.isfile(file):
            if _file.endswith(".java"):
                _file_list.append(file)
        else:
            _file_list.extend(get_java_file(file))
    return _file_list


def in_black(filename):
    """
    判断是否在黑名单中
    :param filename:
    :return:
    """
    new_filename = filename.replace("/", ".")
    for _black in black_list:
        if _black in new_filename:
            return True
    return False


def clean(file_list):
    cache = {}

    for _file in file_list:
        if in_black(_file):
            continue

        # 通过 dict 去重
        new_filename = _file.split("/")
        key = new_filename[:7]
        key = ''.join(key)
        cache[key] = _file
        # new_file.append(_file)
    return cache.values()


def decomplier(file):
    """
    反编译
    :param file:
    :return:
    """
    cmd = "java -jar ~/tools/FernFlower.jar " + file + "  /Users/xxxxxxx/source/   > /dev/null 2>&1"
    os.system(cmd)

    jar_file_name = file.split('/')[-1]
    jar_file_path = "/Users/xxxxxxx/source/" + jar_file_name

    target_dir = jar_file_name.split('.')[:-1]
    source_dir = '.'.join(target_dir)
    source_dir = '/Users/xxxxxxx/source/' + source_dir
    unzip_cmd = "unzip " + jar_file_path + " -d " + source_dir + " > /dev/null 2>&1"
    os.system(unzip_cmd)
    return source_dir


def get_class_declaration(root):
    """
    筛选出符合条件的类
    :param root:
    :return:
    """
    class_list = []
    black_interface = ("DataSource", "RowSet")
    for node in root.types:
        # 非类声明都不分析
        if isinstance(node, ClassDeclaration) is False:
            continue

        # 判断是否继承至classloader
        if node.extends is not None and node.extends.name == "ClassLoader":
            continue

        # 判断是否实现被封禁的接口
        interface_flag = False
        if node.implements is None:
            node.implements = []
        for implement in node.implements:
            if implement.name in black_interface:
                interface_flag = True
                break
        if interface_flag is True:
            continue

        # 判断是否存在无参的构造函数
        constructor_flag = False
        for constructor_declaration in node.constructors:
            if len(constructor_declaration.parameters) == 0:
                constructor_flag = True
                break
        if constructor_flag is False:
            continue

        class_list.append(node)
    return class_list


def write_file(filename, string):
    file_stream = open(filename, "a")
    file_stream.write(string + '\n')
    file_stream.close()


def read_file(filename):
    try:
        file_stream = open(filename, 'r')
        _contents = file_stream.read()
        file_stream.close()
        scanner_list = _contents.strip().split('\n')
    except:
        return []
    return scanner_list


def ack(method_node):
    """
    1、是否调用的lookup 方法，
    2、lookup中参数必须是变量
    3、lookup中的参数必须来自函数入参，或者类属性
    :param method_node:
    :return:
    """
    target_variables = []
    for path, node in method_node:
        # 是否调用lookup 方法
        if isinstance(node, MethodInvocation) and node.member == "lookup":
            # 只能有一个参数。
            if len(node.arguments) != 1:
                continue

            # 参数类型必须是变量，且必须可控
            arg = node.arguments[0]
            if isinstance(arg, Cast):    # 变量 类型强转
                target_variables.append(arg.expression.member)
            if isinstance(arg, MemberReference):  # 变量引用
                target_variables.append(arg.member)
            if isinstance(arg, This):       # this.name， 类的属性也是可控的
                return True
    if len(target_variables) == 0:
        return False

    # 判断lookup的参数，是否来自于方法的入参，只有来自入参才认为可控
    for parameter in method_node.parameters:
        parameter_name = parameter.name
        if parameter_name in target_variables:
            return True
    return False


def scanner(filename):
    file_stream = open(filename, 'r')
    _contents = file_stream.read()
    file_stream.close()

    # 字符串判断快速过滤
    if "InitialContext(" not in _contents:
        return False

    try:
        root_tree = parse(_contents)
    except:
        return False
    class_declaration_list = get_class_declaration(root_tree)
    for class_declaration in class_declaration_list:
        for method_declare in class_declaration.methods:
            if ack(method_declare) is True:
                string = "{file} {method}".format(file=filename, method=method_declare.name)
                print string
                write_file("./result.txt", string)
