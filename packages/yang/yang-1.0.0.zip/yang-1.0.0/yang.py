movies = ["aa","bb","cc",["dd","ee",["ff"]]]
def yang(alist,indent=False,level=0):
    for each_item in alist:
        if isinstance(each_item,list):
            yang(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
                print(each_item)

