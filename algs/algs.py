import random, math

''' Logic for compatify. 5c spring hackathon. 4 /16/2016. coded by Joe Donermeyer
on the team of Joon Hee Lee, Catherine Ma, and Celia Zhang '''


''' Given a list of dictionaries representing songs, returns a list of the key values
 of the songs. '''
def GetInformation(a, key='uri'):
    c = []
    for i in range(len(a)):
        c.append(a[i][key])
    return c
''' a and b are lists of dictionaries. c is a dictionary containing information of
The songs in common. Ignores duplicates     '''   
def Intersection(a, b, key='uri'):
    c = []
    my_dict = {'': False}
    counted_already = {}
    for i in range(len(a)):
        my_dict[a[i][key]] = True  
    for j in range(len(b)):
        if (my_dict.get(b[j][key])):
            if (not counted_already.get(b[j][key])):
                counted_already[b[j][key]] = True
                c.append(b[j])
    #print "There were %s songs in common. They were: \n" %len(c), c
    return c

''' a and b are lists. c is a list of the elements in either. Returns a list of
all songs in either list. '''
def Union(a, b, key = 'uri'):
    c = []
    my_dict = {'': False}
    for i in range(len(a)):
        c.append(a[i])
        my_dict[a[i][key]] = True
    for j in range(len(b)):
        if (not my_dict.get(b[j][key])): #make sure duplicate songs are not                             
            c.append(b[j])                #included twice
   #print c
    return c
''' a and b are lists of dictionaries that contain song information. returns c, 
 a list of dictionaries representing information of songs in a that aren't in  b. '''
def OnlyInFirst(a, b, key = 'uri'):
    c = []
    my_dict = {'': False}
    for i in range(len(b)):
        my_dict[b[i][key]] = True
    for j in range(len(b)):
        if (not my_dict.get(a[j][key])):                                
            c.append(a[j])
    #print c
    return c
''''a and b are lists of dictionaries that contain song information. Returns c, a
dictionary mapping how many instances of different a paramater were in common.
 key is the paramater we're interested in. only considers things that are in
 common amongst songs in the intersection. Thus if 5 songs are in common between a
 and b and the key is albums, it will produce a count of how often different albums
 appear in that set of 5 songs.'''
def InCommonCounts(a, b, key):
    c = Intersection(a, b)
    artistcount = {}
    for i in range(len(c)):
        if (not artistcount.get(c[i][key])):
            artistcount[c[i][key]] = 1
        else:
            artistcount[c[i][key]] += 1
    #print artistcount    
    return artistcount

'''Given a dictionary, a, mapping instances of an key to number of occurances, 
returns a sorted list of the keys corresponding to the top n occurances. 
 returns as a tuple (key, occurances) '''
def TopNOccurrences(a, n):
    c = []
    x = sorted(a, key=a.get, reverse=True)
    
    if n > len(x):
        for i in range(len(x)):
            c.append((x[i], a[x[i]]))
    else:
        for i in range(n):
            c.append((x[i], a[x[i]]))
    #print c
    return c
'''finds the compatability index. What percentage of songs in the smaller
   sized playlist are in common. Rounds to two decimals '''
def CompatabilityIndex(a, b):
    c = Intersection(a, b, 'uri')
    percentage = 100.0 * len(c) / min(len(a), len(b))
    percentage = round(percentage, 2);
    return percentage


'''generate a random string of size length'''
def generateRandomString(length): 
    text = '';
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for i in range(length):
        text += possible[int(math.floor(random.random() * len(possible)))]

    return text

'''return list of song ids for the intersection playlist of a, b'''
def IntersectionPlaylist(a, b):
    c = Intersection(a, b)
    playlist = GetInformation(c)
    print playlist
    return playlist
'''return list of song ids in a but not in b'''
def ExclusivePlaylist(a, b):
    c = OnlyInFirst(a, b)
    playlist = GetInformation(c)
    print playlist
    return playlist
'''returns a list of the top n artists of songs that were shared. 
   Each list element is a tuple of the artist name and how many 
   occurances there where'''
def TopNArtists(a, b, n):
    c = InCommonCounts(a, b, 'artist')
    topn = TopNOccurrences(c, n)
    print topn
    return topn
    
#Main function
if __name__ == '__main__':
    dict1 = {'uri': 1, 'artist': 'Swift', 'album': '1985'}
    dict2 = {'uri': 2, 'artist': 'Kanye', 'album': 'TLOP'}
    dict5 = {'uri': 5, 'artist': 'Joon', 'album': 'Songs in the key of Junhui'}
    dict6 = {'uri': 6, 'artist': 'Swift', 'album': 'speak now'}
    dict10 = {'uri': 10, 'artist': 'Swift', 'album' : 'red'}
    dict3 = {'uri': 3, 'artist': 'Kanye', 'album' : 'TLOP'}
    dict7 = {'uri': 7, 'artist': 'Swift', 'album' : 'red'}    
    #print OnlyInFirst([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    #print Union([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    #print Intersection([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    #x = InCommonCounts([dict1, dict2, dict3, dict7, dict5, dict6, dict10], [dict1, dict2, dict3, dict5, dict6, dict10], 'album')
    #print TopNOccurrences(x, 40)
    #x = InCommonCounts([dict1, dict2, dict3, dict7, dict5, dict6, dict10], [dict1, dict2, dict3, dict5, dict6, dict10], 'artist')
    #print TopNOccurrences(x, 40)    
    
    #y = Union([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
    #print GetInformation(y)
    
    #Intersection([dict1, dict2, dict5, dict6, dict10], [dict1, dict2, dict3, dict10, dict7])
    