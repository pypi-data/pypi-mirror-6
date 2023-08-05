""" This is Tapan's first module. """
""" This method takes a list as input and prints all values
be it nested or at the same level"""

def printNestedList(the_list, indentations = 0, shouldIndent = False):
    for listElement in the_list:
        if isinstance(listElement, list):
            printNestedList(listElement, indentations + 1, shouldIndent)
        else:
            if shouldIndent:
                for tab_count in range(indentations):
                    print("\t", end='')
            print(listElement)
        
    
