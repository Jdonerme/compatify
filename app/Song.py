import string, re
sigTimeDifference = 10000 # ms

# words that are found in songs titles to differentiate versions of the same song
DIFFERENT_VERSION_KEY_WORDS = ["version", "live", "studio", "rerecorded", "edit"]

''' words that denote different versions of a song that are similar enough that
    they should not be included twice in the interesection playlist.

    They still should be removed from the title of the identifier so that all
    versions of the song match.

    '''
SAME_VERSION_KEY_WORDS = ["remaster", "mono", "stereo", "rerecorded"]

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

""" return a lower case string with punctuation removed.

    """
def simple_string(s):
    return s.lower().translate({string.punctuation: None})

""" remove keywords with excess information form the song name.

    """
def get_simplified_song_name(name, keywords):
    song_name = name
    for word in keywords:
            if word in song_name and ' - ' in song_name:
                index = song_name.index(' - ')
                song_name = song_name[:index]
    return song_name

def take_artists_from_song_name(name, artist_set):
    song_name = name
    feat_index = song_name.index(" (feat. ")

    start_artist_index = feat_index + 8
    end_artist_index = song_name.rfind(')')

    featured_artists = song_name[start_artist_index:end_artist_index]

    featured_artists_list = re.split(" & | and |, ", featured_artists)
    artist_set |= set(featured_artists_list)

    # remove the features from the title since they're not always there
    song_name = song_name[:feat_index]
    return song_name, artist_set


""" A object to hold necessary song fields.

    uri: unique string spotify assigns to song  
    name: title of song
    artist: primary artist on the song
    featured_artists: any collaboration artists on the song
    duration: length of song in ms

    match_name: title of the song with insignificant distinguishing features
                removed (ex. remastered)
    identifier: a string that should be the same for all potential different
                versions of the same song

    artist_set: A set containing all the artists that are credited on the song

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

        self.artist_set = set(list(map(simple_string, [artist] + features)))
        self.set_identifier_and_match_name()

        # save some attributes in a dictionary for access with [] notation
        self.attributes = { "name": self.name, "uri": self.uri, "artist": 
              self.artist, "album": self.album, "duration": self.duration,
              "featured_artists": self.featured_artists,
              "identifier": self.identifier
        }
        

    ''' Set the strings that are used for song matching.

        '''
    def set_identifier_and_match_name(self):
        song_name = self.name.lower()

        if " (feat. " in song_name:
            song_name, artist_set = take_artists_from_song_name(song_name,
                                                              self.artist_set)
            # if the features were not already recorded as artists for the track
            if len(self.featured_artists) == 0:
                self.artist_set |= set(artist_set)

        # remove details about the song that are considered to not significantly
        # make the song a different version
        song_name = get_simplified_song_name(song_name, SAME_VERSION_KEY_WORDS)
        self.match_name = simple_string(song_name)

        # remove any version specific details from the song title 
        song_name = get_simplified_song_name(song_name, DIFFERENT_VERSION_KEY_WORDS)
        
        identifier = simple_string(song_name) + " - " + \
                     simple_string(self.artist)
        self.identifier = identifier


    @lazy_property
    def audio_features(self):
        # Get Audio features info
        return self.sp.audio_features([self.uri])


    ''' 
        How to consider two songs as the same. If the uri is the same, the track
        is the same for sure.

        If the name and artists are the same and the duration is within a number
        of seconds, the song is considered the same too.

        '''
    def __eq__(self, other):
        if isinstance(other, Song):
            if self.uri == other.uri:
                return True 

            elif self.match_name == other.match_name and \
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