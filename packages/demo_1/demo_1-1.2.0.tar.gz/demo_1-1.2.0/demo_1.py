"""this is first demo to PYPI """
'''  ''is used too'''
# this is zhushi  oo

def print_lol (the_list,level=0):
    for each_item in the_list :
        if isinstance (each_item,list):
            print_lol (each_item,level+1)
        else :
            for num in range (level):
                print ("\t"),
            print (each_item)



            
