'''这是"nester.py"模块，提供了一个名为print_lol()的函数来打印列表，其中包含或不包含嵌套列表。'''

def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
