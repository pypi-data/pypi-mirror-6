__author__ = 'Xu Jing'

def printNestedList(aList, num):
    for item in aList:
        if isinstance(item, list):
            printNestedList(item, num + num)
        else:
            for i in range(num):
                print("\t", end = '')
            print(item)


