import random, math



''' Logic for compatify. 5c spring hackathon. 4 /16/2016. coded by Joe Donermeyer
on the team of Joon Hee Lee, Catherine Ma, and Celia Zhang.

    Updated on 9/11/2018 to not count different versions of the same song as 
    independent. '''


''' Given a list of song objects, returns a list of the key values
 of the songs. '''
def getInformation(playlist, key='uri'):
    return list(map(lambda x: x[key], playlist))

""" given a list of songs, finds the number of unique songs.
    
    Note that compatability, different versions of the same song are only
    counted once."""

def non_duplicate_playlist_length(playlist):
    identifiers = set(getInformation(playlist, "identifier"))
    return len(identifiers)

''' Given playlist_a and playlist_b lists of song objects, find the intersection.

    Initially finds songs with that share the identifier and then checks
    to confirm that they are the same version of the song.

    returns a list of the intersection songs.

    '''   
def intersection(playlist_a, playlist_b):
    intersection_songs = []
    playlist_a_songs = {}
    counted_already = {}

    if playlist_a == [] or playlist_b == []:
        return []

    # for each song in playlist a
    for song_a in playlist_a:

        identifier = song_a.identifier

        # if no version of the song has been seen before
        if identifier not in playlist_a_songs:
            # save the song for cross-checking
            playlist_a_songs[identifier] = [song_a]

        # if no version of the song that has been seen before matches this one
        elif song_a not in playlist_a_songs[identifier]:

            #save the song for cross checking
            playlist_a_songs[identifier].append(song_a)

    song_a = None
    # for each song in playlist b
    for song_b in playlist_b:
        identifier = song_b.identifier

        # for all version of the song in playlist a
        song_a_list = playlist_a_songs.get(identifier)
        if not song_a_list:
            continue

        # the song is included if it hasn't been added yet
        if identifier not in counted_already:
            intersection_songs.append(song_b)
            counted_already[identifier] = [song_b]

        # the song is added if it as a unique version that hasn't been added yet
        elif song_b not in counted_already[identifier]:
                intersection_songs.append(song_b)
                counted_already[identifier].append(song_b)

        # for each version of the song in playlist a
        for i, song_a in enumerate(song_a_list):

            # add the song if it's a unique version
            if song_a not in counted_already[identifier]:
                intersection_songs.append(song_a)
                counted_already[identifier].append(song_a)

    return intersection_songs

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
def onlyInFirst(a, b, key = 'uri'):
    c = []
    my_dict = {'': False}
    for i in range(len(b)):
        my_dict[b[i][key]] = True
    for j in range(len(b)):
        if (not my_dict.get(a[j][key])):                                
            c.append(a[j])
    #print c 
    return c

''' intersection_songs contains a list of song objects shared. 

    Returns inCommonCount, a dictionary mapping how many instances of different
    a paramater were in common. key is the paramater we're interested in. 

    Thus if 5 songs are in the interesction and the key is albums, it will 
    produce a count of how often different albums appear in that set of 5 songs.

    '''
def inCommonCounts(intersection_songs, key):
    inCommonCount = {}
    for song in intersection_songs:
        if (not inCommonCount.get(song[key])):
            inCommonCount[song[key]] = 1
        else:
            inCommonCount[song[key]] += 1
   
    return inCommonCount

'''Given a playlist of songs, maps instances of an key to number of occurences, 

returns a sorted list of the keys corresponding to the top n occureneces. 
 
 returns as a tuple (key, occureneces) '''
def topNOccurrences(playlist, n):
    top_occureneces = []
    x = sorted(playlist, key=playlist.get, reverse=True)
    
    if n > len(x):
        for i in range(len(x)):
            top_occureneces.append((x[i], playlist[x[i]]))
    else:
        for i in range(n):
            top_occureneces.append((x[i], playlist[x[i]]))

    return top_occureneces
'''finds the compatability index. What percentage of songs in the smaller
   sized playlist are in common. Rounds to two decimals '''
def compatabilityIndex(playlist_a, playlist_b, intersection_songs=None):
    if intersection_songs is None:
        intersection_songs = Intersection(a, b, 'uri')

    a_length = non_duplicate_playlist_length(playlist_a)
    b_length = non_duplicate_playlist_length(playlist_b)
    interesction_length = non_duplicate_playlist_length(intersection_songs)

    percentage = 100.0 * interesction_length / min(a_length, b_length)
    percentage = round(percentage, 2);
    return percentage


'''generate a random string of size length'''
def generateRandomString(length): 
    text = '';
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for i in range(length):
        text += possible[int(math.floor(random.random() * len(possible)))]

    return text

'''return list of song ids in a but not in b'''
def ExclusivePlaylist(a, b):
    c = onlyInFirst(a, b)
    playlist = getInformation(c)
    # print playlist
    return playlist
    
'''returns a list of the top n artists of songs that were shared. 
   Each list element is a tuple of the artist name and how many 
   occureneces there where'''
def topNArtists(intersection_songs, n):
    common_counts = inCommonCounts(intersection_songs, 'artist')
    topn = topNOccurrences(common_counts, n)
    # print topn
    return topn
    
# #Main function
# if __name__ == '__main__':
#     dict1 = {'uri': 1, 'artist': 'Swift', 'album': '1985', 'name': 'a', 'duration': 4000}
#     dict2 = {'uri': 2, 'artist': 'Kanye', 'album': 'TLOP', 'name': 'v', 'duration': 4000}
#     dict5 = {'uri': 5, 'artist': 'Joon', 'album': 'Songs in the key of Junhui', 'name': 'v', 'duration': 4000}
#     dict6 = {'uri': 6, 'artist': 'Swift', 'album': 'speak now', 'name': 'v', 'duration': 4000}
#     dict10 = {'uri': 10, 'artist': 'Swift', 'album' : 'red', 'name': 'a', 'duration': 4000}
#     dict3 = {'uri': 3, 'artist': 'Kanye', 'album' : 'TLOP', 'name': 'v', 'duration': 4000}
#     dict7 = {'uri': 7, 'artist': 'Swift', 'album' : 'red', 'name': 'a', 'duration': 4000}    
#     # print OnlyInFirst([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
#     # print Union([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
#     print intersection([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict7])
#     # x = InCommonCounts([dict1, dict2, dict3, dict7, dict5, dict6, dict10], [dict1, dict2, dict3, dict5, dict6, dict10], 'album')
#     # print TopNOccurrences(x, 40)
#     # x = InCommonCounts([dict1, dict2, dict3, dict7, dict5, dict6, dict10], [dict1, dict2, dict3, dict5, dict6, dict10], 'artist')
#     # print TopNOccurrences(x, 40)    
    
#     # y = Union([dict1, dict2, dict5, dict6, dict10], [dict2, dict3, dict10, dict7])
#     # print GetInformation(y)
    
#     # Intersection([dict1, dict2, dict5, dict6, dict10], [dict1, dict2, dict3, dict10, dict7])
    
