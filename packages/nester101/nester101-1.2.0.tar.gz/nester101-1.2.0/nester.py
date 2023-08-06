def print_list(list_arg,level=0):
    for list_item1 in list_arg:
        if isinstance(list_item1,list):
            print_list(list_item1,level+1)
        else:
            for num in range(level):
                print("\t",end='')
            print(list_item1)
