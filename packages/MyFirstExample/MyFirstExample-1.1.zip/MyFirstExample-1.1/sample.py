def separateItem(arg0,arg1=0,arg2=False):
    for item in arg0:
        if isinstance(item,list):
            separateItem(item,arg1+1,arg2);
        else:
            if(arg2):
                for index in range(arg1):
                    print("\t",end="");
            print(item);
