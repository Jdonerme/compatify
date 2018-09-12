sigTimeDifference = 10000 # ms

""" A object to hold necessary song fields.

    uri: unique string spotify assigns to song  
    name: title of song
    featured_artists: any collaboratin artists on the song
    duration: length of song in ms

    """
class Song(object):
    def __init__(self, uri, name, artist, features, album, duration):
        self.uri = uri
        self.name = name
        self.artist = artist
        self.featured_artists = features
        self.album = album
        self.duration = duration

        self.attributes = { "name": self.name, "uri": self.uri, "artist": 
              self.artist, "album": self.album, "duration": self.duration,
              "featured_artists": self.featured_artists
            }

    ''' A string that is unique to each song but will be the same for different 
        versions of the same song.

    '''
    def get_identifier(self):
        return self.name + "-" + self.artist

    ''' 
        How to consider two songs as the same. If the uri is the same the track
        is the same for sure.

        If there are collaborating artists in one version but not the other,
        it is considered a different version of the song.

        If the name and artist are the same and the duration is within a number
        of seconds, the song is considered the same too.

        '''
    def __eq__(self, other):
        if isinstance(other, Song):
            if self.uri == other.uri:
                return True 
            elif self.featured_artists != other.featured_artists:
                return False
            return (self.name == other.name and self.artist == other.artist and 
                     (abs(self.duration - other.duration) < sigTimeDifference))
        else:
            return False
    # not equal to go with equality definition
    def __ne__(self, other):
        return (not self.__eq__(other))

    # allows accessing fields of the song with [] notation
    def __getitem__(self, key):
        return self.attributes[key]

    # formats the output when printing the song as a string
    def __str__(self):
        name = self.name.encode('utf-8').strip()
        artist = self.artist.encode('utf-8').strip()
        album = self.album.encode('utf-8').strip()
        return "Title: %s \n" \
               "artist: %s \n" \
               "album: %s" % (name, artist, album)