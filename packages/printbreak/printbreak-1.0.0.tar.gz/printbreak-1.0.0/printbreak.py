"""This is the "printbreak.py" module, and it provides ine function called print_lol which prints lists
the may or may not contain nested lists"""

def print_lol(the_list):
    """This Function takes a positional argument called "the_list" which is any python list ( of
possibly nested lists) Each data item in the provided list is printed to the screen on it's own lines."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
