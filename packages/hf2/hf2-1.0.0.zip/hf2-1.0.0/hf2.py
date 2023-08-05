"""roop denis"""
def roop(listname):
    """diguiropp"""
    for i in listname:
        if isinstance(i,list):
            roop(i)
        else:
            print (i)