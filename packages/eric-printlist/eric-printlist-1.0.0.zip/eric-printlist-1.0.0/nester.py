'''
nester.py
打印一个list，list中可以包含其他list。
'''

def print_lol(the_list, level):
    '''print_lol函数打印list。'''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for num in range(level):
                print('\t', end="")
            print(each_item)
