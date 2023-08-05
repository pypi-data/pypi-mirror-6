def dx_print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            dx_print_lol(each_item)
        else:
            print(each_item)
