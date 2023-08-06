"""
Test
"""
def pp_list  (tt):
    for pp in tt:
        if isinstance(pp,list):
            pp_list(pp)
        else:
            print(pp)

# The end
