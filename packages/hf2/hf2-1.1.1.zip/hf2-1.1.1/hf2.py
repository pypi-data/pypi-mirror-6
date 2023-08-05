"""roop denis"""
def roop(listname,suojin):
    """diguiropp"""
    for i in listname:
        if isinstance(i,list):
            roop(i,suojin+1)
        else:
            for tab_stop in range(suojin):
                print "\t",
            print i