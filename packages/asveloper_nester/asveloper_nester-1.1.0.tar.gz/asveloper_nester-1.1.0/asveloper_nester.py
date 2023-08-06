def print_list(the_list,level):
        for my_list in the_list:
                if isinstance(my_list,list):
                        print_list(my_list,level+1)

                else:
                        for tab_space in range(level):
                                print('\t',end='')

                        print(my_list)

