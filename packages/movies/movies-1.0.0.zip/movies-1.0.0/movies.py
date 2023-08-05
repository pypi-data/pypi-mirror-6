def lst(movies):
    for x in movies:
        if isinstance(x,list):
            lst(x)
        else:
            print(x)
