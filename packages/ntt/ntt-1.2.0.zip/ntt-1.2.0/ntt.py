"""
Test
"""
def pp_list  (tt,level=0):
    for pp in tt:
        if isinstance(pp,list):
            pp_list(pp,level+1)
        else:
            for tab_show in range(level):
                print("\t",end='')
            print(pp)

# The end

