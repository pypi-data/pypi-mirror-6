__author__ = 'leedongjun'

"""This is HFT.py module for studying Head first Python, It offers print_lol function
This function print out all element in the list including list in the list."""


def print_lol(the_list):
    """This function has the input which is "the_list", and it can be input python list.
    the list may have list in the element of list. It will print out the each item in the list
    and list of list."""

    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
