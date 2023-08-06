"""
Test
"""
def pp_list  (tt,judge=True,level=0):
    for pp in tt:
        if isinstance(pp,list):
            pp_list(pp,judge,level+1)
        else:
            if judge:
               for tab_show in range(level):
                print("\t",end='')
            print(pp)


# The end

