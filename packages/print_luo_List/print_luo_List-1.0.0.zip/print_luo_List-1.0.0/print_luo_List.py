***
print nested list
***
def printList(the_list):
    for metalist in the_list:
        if isinstance(metalist,list):
            printList(metalist)
        else:
            print metalist
