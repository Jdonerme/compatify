import string
sigTimeDifference = 10000 # ms
VERSION_KEY_WORDS = ["remaster", "mono", "stereo", "version"]


def lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.

    '''
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property

def simple_string(s):
    return s.lower().translate({string.punctuation: None})

def get_identifier(name, artist):
    song_name = name.lower()
    for word in VERSION_KEY_WORDS:
        if word in song_name and ' - ' in song_name:
            index = song_name.index(' - ')
            song_name = song_name[:index]
    identifier = song_name.translate({string.punctuation: None}) + " - " + \
                 artist.lower().translate({string.punctuation: None})
    return identifier

""" A object to hold necessary song fields.

    uri: unique string spotify assigns to song  
    name: title of song
    featured_artists: any collaboratin artists on the song
    duration: length of song in ms

    """
class Song(object):
    def __init__(self, sp, uri, name, artist, features, album, duration):
        self.sp = sp
        self.uri = uri
        self.name = name
        self.artist = artist
        self.featured_artists = features
        self.album = album
        self.duration = duration

        ''' A string that is unique to each song but will be the same for
        different versions of the same song.

        '''
        self.identifier = get_identifier(name, artist)

        ''' A set containing all the artists that are credited on the song.

        '''
        self.artist_set = set(list(map(simple_string, [artist] + features)))

        # save some attributes in a dictionary for access with [] notation
        self.attributes = { "name": self.name, "uri": self.uri, "artist": 
              self.artist, "album": self.album, "duration": self.duration,
              "featured_artists": self.featured_artists,
              "identifier": self.identifier
            }

    @lazy_property
    def audio_features(self):
        # Get Audio features info
        return self.sp.audio_features([self.uri])


    def has_similar_features_with(self, other):
        if self.identifier == other.identifier:
            return True

        return False

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

            elif simple_string(self.name) == simple_string(other.name) and \
                self.artist_set == other.artist_set and \
                (abs(self.duration - other.duration) < sigTimeDifference):
                return True

            return False
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
        uri = self.uri.encode('utf-8').strip()
        return "Title: %s \n" \
               "artist: %s \n" \
               "album: %s\n" \
               "uri: %s \n"  % (name, artist, album, uri)