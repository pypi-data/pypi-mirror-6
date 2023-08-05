movies=["The Holy Girl",1975,"Terry Jones & Terry Gilliam",91,
        ["Graham Chapman",["Michael Palin", "John Cleese","Terry Gilliam","Eric Idle"
                           ,"Terry Jones"]]]
#print(movies)
'''for each_item in movies:
    if isinstance(each_item,list)==False:
        print (each_item)
    else:
        for i in each_item:
            if isinstance(i,list)==False:
                print(i)
            else:
                for j in i:
                    print(j)'''
def print_lol(the_list,indent=False,num=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,num+1)
        else:
            if indent:
                for i in range(num):
                    print("\t",end='')
            print(each_item)
''' print_lol(movies)'''
'''movies.insert(1,1975)
movies.insert(3,1979)
movies.insert(5,1983)

print (movies)
fav_movies=["The Holy Girl","The Life of Brian"]
for each_flick in fav_movies:
    print (each_flick)'''

