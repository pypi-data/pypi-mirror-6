def print_list(sola,level = 0):   
    for i in sola:
        if isinstance(i,list):
            print_list(i,level+1)
        else:
            for tab_no in range(level):
                print(level,end='')
                print("\t",end='')
            print(i)

            


        
