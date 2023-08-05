'''
Created on Dec 26, 2013

@author: chandru
Module to print objects in a collection by nesting through the collection
'''

""" Recursively print items within the collection 
    My First Python code """
def print_coll(coll, tabs):
    for each_item in coll:
        if isinstance(each_item, list):
            print_coll(each_item, tabs+1)
        else:
            for tab_stop in range(tabs):
                print("\t");
                
            print(each_item)
            


            