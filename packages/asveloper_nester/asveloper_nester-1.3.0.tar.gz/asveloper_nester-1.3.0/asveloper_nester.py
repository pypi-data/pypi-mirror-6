def print_list(the_list,indent=False,level=0):
        for my_list in the_list:
                if isinstance(my_list,list):
                        print_list(my_list,indent,level+1)

                else:
                        if indent:
                                for tab_space in range(level):
                                        print('\t',end='')
                        else:
                                print(my_list)

