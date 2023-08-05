"""this is my first commit code source."""



def print_lol(thelists,indent=False,level=0):
    """this function is running print the array"""
    for thelist in thelists:
        if isinstance(thelist, list):
            print_lol(thelist,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print('--')
            print(thelist)
    #function end
        
