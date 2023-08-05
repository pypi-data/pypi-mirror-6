""" This is Tapan's first module. """
""" This method takes a list as input and prints all values
be it nested or at the same level"""

def printNestedList(the_list):
    for listElement in the_list:
        if isinstance(listElement, list):
            printNestedList(listElement)
        else:
            print(listElement)
        
    
