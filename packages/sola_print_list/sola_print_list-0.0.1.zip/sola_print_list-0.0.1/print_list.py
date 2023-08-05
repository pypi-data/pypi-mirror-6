def print_list(sola):
    for i in sola:
        if isinstance(i,list):
            print_list(i)
        else:
            print(i)

            


        
