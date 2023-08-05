"""this is my first commit code source."""



def print_lol(thelists,level):
    """this function is running print the array"""
    for thelist in thelists:
        if isinstance(thelist, list):
            print_lol(thelist,level+1)
        else:
            for tab_stop in range(level):
                print("\t")
            print(thelist)
    #function end
        
