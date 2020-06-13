from algs import generateRandomString

from spotipy import oauth2
class State(object):
    def __init__(self, production=True):
        self._OAuthKeys = generateRandomString(16), generateRandomString(16)
        self._production = production
        self._match = False

        # playlist of songs that have been found for both user's librarys
        self._intersection_playlist = {}

        # list of the tracks and playlists for each user where the key is the integer user id
        self._tracks_dict = {}
        # list of the sources from which to take songs for each user where the key is the integer user id
        self._song_sources_dict = {}

        self._selected = {}
        self._OAuthObjects = self._createOAuthObjects()

    def isDirty(self):
        if self.getIntersectionPlaylist() or \
           self.getTracksDict() or \
           self.getSongSourcesDict() or \
           self.inMatchMode():
                return True
        return False

    def clean(self):
        self.__init__(self._production)
    
    def inProductionMode(self):
        return self._production
    def inMatchMode(self):
        return self._match
    def enableMatchMode(self):
        self._match = True

    def getIntersectionPlaylist(self):
        return self._intersection_playlist
    def getTracksDict(self):
        return self._tracks_dict
    def getSongSourcesDict(self):
        return self._song_sources_dict

    # 0 / default = return both objects as a tuple
    # 1 = return object for user 1
    # 2 = return object for user 2
    def getOAuthObjects(self, index = 0):
        if index and index < 3:
            return self._OAuthObjects[index - 1]
        return self._OAuthObjects
      # 0 / default = return both objects as a tuple
    
    # 0 / default = return both keys as a tuple
    # 1 = return key for user 1
    # 2 = return object for user 2
    def getOAuthKeys(self, index = 0):
        if index and index < 3:
            return self._OAuthKeys[index - 1]
        return self._OAuthKeys

    def _createOAuthObjects(self):
        SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'
        CACHE = '.spotipyoauthcache'
        SPOTIPY_CLIENT_ID = '883896384d0c4d158bab154c01de29db'
        SPOTIPY_CLIENT_SECRET = '37443ee0c0404c44b755f3ed97c48493'

        if self.inProductionMode():
            SPOTIPY_REDIRECT_URI1 = 'https://compatify.herokuapp.com/callback1'
            SPOTIPY_REDIRECT_URI2 = 'https://compatify.herokuapp.com/callback2'
        else:
            SPOTIPY_REDIRECT_URI1 = 'http://localhost:8888/callback1'
            SPOTIPY_REDIRECT_URI2 = 'http://localhost:8888/callback2'

        sp_oauth1 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI1,state=self.getOAuthKeys(1),scope=SCOPE,cache_path=CACHE,show_dialog=True)
        sp_oauth2 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI2,state=self.getOAuthKeys(2),scope=SCOPE,cache_path=CACHE,show_dialog=True)
        return sp_oauth1, sp_oauth2