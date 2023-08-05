def print_lol(the_list,indent = False,level = 0,fn = sys.stdout):
    for i in the_list:
        if isinstance(i,list):
            print_lol(i,indent,level+1,fn)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t',end = '',file = fn)
            print(i,file = fn)
