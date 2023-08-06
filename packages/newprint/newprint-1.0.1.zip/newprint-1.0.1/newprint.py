"""this can help you print a list"""
def print_lol(the_list,indent=False,level=0):
    """这只是一个测试"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each_item)
            
