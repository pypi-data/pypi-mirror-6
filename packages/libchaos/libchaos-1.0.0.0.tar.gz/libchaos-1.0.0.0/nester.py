#!/usr/bin/python3
#coding = utf-8

"""这是“nester.py”模块，提供了名为print_lol的函数
这个函数的作用是打印列表。"""

def print_lol(the_list):
    """这个函数取了一个位置参数，表示可以
     是任意列表。"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)

