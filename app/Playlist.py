from Song import Song, create_song_obj_from_track_dict
from algs import intersection, non_duplicate_playlist_length

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

""" Create a Playlist Object in a useful format using the raw information
    returned by the Spotify API.

    sp: spotify client object that was used to fetch the playlsit
    playlist (dict): raw [;ay;ost] object returned from spotipy.

    """

def create_playlist_obj_from_dict(sp, playlist):
    user = sp.me()["id"]
    return Playlist(sp, playlist["uri"], playlist["name"], user, playlist["id"])


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
class Playlist(object):
    required_song_fields = "items(is_local,track(uri,name,artists(name),album(name),duration_ms)),next"
    def __init__(self, sp, uri, name, user, playlist_id):
        self.sp = sp
        self.uri = uri
        self.name = name
        self.user = user
        self.username = sp.me()["display_name"]
        self.id = playlist_id

    @lazy_property
    def tracks(self):
        song_objects = []
        results = self.sp.playlist_tracks(self.id,
                        fields=Playlist.required_song_fields)

        for item in results["items"]:
            track = item['track']
            local = item['is_local']
            song_objects.append (create_song_obj_from_track_dict(self.sp, track, local))

        while results['next']:
            results = self.sp.next(results)
            for item in results["items"]:
                track = item['track']
                local = item['is_local']
                song_objects.append (create_song_obj_from_track_dict(self.sp, track, local))
            song_objects.append (create_song_obj_from_track_dict(self.sp, track))

        return song_objects

    @lazy_property
    def length(self):
        return (self.tracks)

    ''' 
        How to consider two playlists as the same.

        If the id is the same, the playlist is the same for sure. If they are of
        different lengths, they are different playlists.

        if the input playlists and the intersection have the same length,
        the two inputs have the same songs and should be considered the same.


        '''
    def __eq__(self, other):
        if isinstance(other, Playlist):
            if self.id == other.id:
                return True 

            elif len(self.tracks) != len(other.tracks):
                return False
                #
            return non_duplicate_playlist_length(self.tracks) == \
                   non_duplicate_playlist_length(intersection(self, other))

        return False
    # not equal to go with equality definition
    def __ne__(self, other):
        return (not self.__eq__(other))

    # formats the output when printing the song as a string
    def __str__(self):
        name = self.name.encode('utf-8').strip()
        username = self.username.encode('utf-8').strip()
        uri = self.uri.encode('utf-8').strip()
        return (
            "-" * 50 + "\n"
            "Playlist Name: %s \n" #% name
            "Owner: %s \n" #% username
            "uri: %s \n" % (name, username, uri) +
            "-" * 50 + "\n"
            )