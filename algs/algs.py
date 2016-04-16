
def Swag(a, b):
    c = []
  
    return c
# Given a list of dictionaries representing songs, returns a list of their song IDs. 
def getSongs(a):
    c = []
    for i in range(len(a)):
        c.append(a[i]['id'])
    return c
# Given a list of dictionaries representings songs, returns a list of their artists. 
def getArtists(a):
    c = []
    for i in range(len(a)):
        c.append(a[i]['artist'])
    return c
# a and b are lists of dictionaries. c is a dictionary containing information of
#The songs in common. Ignores duplicates        
def SongsinCommon(a, b):
    c = []
    my_dict = {'': False}
    counted_already = {}
    for i in range(len(a)):
        my_dict[a[i]['id']] = True  
    for j in range(len(b)):
        if (my_dict.get(b[j]['id'])):
            if (not counted_already.get(b[j]['id'])):
                counted_already[b[j]['id']] = True
                c.append(b[j])
    #print "There were %s songs in common. They were: \n" %len(c), c
    return c

# a and b are lists. c is a list of the elements in either. Returns a list of
#all songs in either list.
def SongsinEither(a, b):
    c = []
    my_dict = {'': False}
    for i in range(len(a)):
        c.append(a[i]['id'])
        my_dict[a[i]['id']] = True
    for j in range(len(b)):
        if (not my_dict.get(b[j]['id'])): #make sure duplicate songs are not                             
            c.append(b[j])                #included twice
    #print c
    return c
# a and b are lists of dictionaries that contain song information. returns c, 
# a list of dictionaries representing information of songs in a that aren't in  b.
def SongsOnlyinfirst(a, b):
    c = []
    my_dict = {'': False}
    for i in range(len(b)):
        my_dict[b[i]['id']] = True
    for j in range(len(b)):
        if (not my_dict.get(a[j]['id'])):                                
            c.append(a[j])
    #print c
    return c
#a and b are lists of dictionaries that contain song information. Returns c, a
#dictionary mapping how many instances of different artists were in common.
def inCommonCounts(a, b, key):
    c = SongsinCommon(a, b)
    artistcount = {}
    for i in range(len(c)):
        if (not artistcount.get(c[i][key])):
            artistcount[c[i][key]] = 1
        else:
            artistcount[c[i][key]] += 1
    #print artistcount    
    return artistcount

#Given a dictionary, a, mapping instances of an key to number of occurances, 
#returns a sorted list of the keys corresponding to the top n occurances. 
# returns as a tuple (key, occurances)
def TopNOccurances(a, n):
    c = []
    x = sorted(a, key=a.get, reverse=True)
    
    if n > len(x):
        for i in range(len(x)):
            c.append((x[i], a[x[i]]))
    else:
        for i in range(n):
            c.append((x[i], a[x[i]]))
    print c
    return c
            
#Main function
if __name__ == '__main__':
    dict1 = {'id': 1, 'artist': 'Swift', 'album': '1985'}
    dict2 = {'id': 2, 'artist': 'Kanye', 'album': 'TLOP'}
    dict5 = {'id': 5, 'artist': 'Joon', 'album': 'Songs in the key of Junhui'}
    dict6 = {'id': 6, 'artist': 'Swift', 'album': 'speak now'}
    dict10 = {'id': 10, 'artist': 'Swift', 'album' : 'red'}
    dict3 = {'id': 3, 'artist': 'Kanye', 'album' : 'TLOP'}
    dict7 = {'id': 7, 'artist': 'Swift', 'album' : 'red'}    
    SongsOnlyinfirst([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    #SongsinEither([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    #SongsinCommon([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    x = inCommonCounts([dict1, dict2, dict3, dict7, dict5, dict6, dict10], [dict1, dict2, dict3, dict5, dict6, dict10], 'album')
    TopNOccurances(x, 40)
    x = inCommonCounts([dict1, dict2, dict3, dict7, dict5, dict6, dict10], [dict1, dict2, dict3, dict5, dict6, dict10], 'artist')
    TopNOccurances(x, 40)    
    
    
    