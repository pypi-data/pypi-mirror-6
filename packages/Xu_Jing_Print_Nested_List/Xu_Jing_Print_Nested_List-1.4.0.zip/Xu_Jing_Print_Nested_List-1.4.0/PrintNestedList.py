__author__ = 'Xu Jing'

import sys


def print_nested_list(a_list, num=0, file=sys.stdout):
    for item in a_list:
        if isinstance(item, list):
            print_nested_list(item, num + num, file)
        else:
            for i in range(num):
                print("\t", end='', file=file)
            print(item, file=file)


