def separateItem(product):
    for item in product:
        if isinstance(item,list):
            separateItem(item);
        else:
            print(item)
