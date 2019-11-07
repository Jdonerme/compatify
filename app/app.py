# -*- coding: utf-8 -*
from flask import (
    Flask, render_template, request, redirect, url_for, session, Response,
    stream_with_context, render_template_string)
from flask.logging import default_handler
import spotipy, sys, os, algs
from contextlib import contextmanager
from spotipy import oauth2
from Song import Song, create_song_obj_from_track_dict
from Playlist import Playlist, create_playlist_obj_from_dict
from forms import SelectForm
from requests import ConnectionError , Timeout
from werkzeug.exceptions import HTTPException
import time
import logging

app = Flask(__name__)
app.secret_key = algs.generateRandomString(16)

# GLOBAL VARIABLES
log = logging.getLogger('my-logger')

PORT_NUMBER = int(os.environ.get('PORT', 8888))
SPOTIPY_CLIENT_ID = '883896384d0c4d158bab154c01de29db'
SPOTIPY_CLIENT_SECRET = '37443ee0c0404c44b755f3ed97c48493'

PRODUCTION = True

if PRODUCTION:
    SPOTIPY_REDIRECT_URI1 = 'https://compatify.herokuapp.com/callback1'
    SPOTIPY_REDIRECT_URI2 = 'https://compatify.herokuapp.com/callback2'

    # Set flask logs to "warning level only in production builds"
    flaskLog = logging.getLogger('werkzeug')
    flaskLog.setLevel(logging.WARNING)
    app.logger.setLevel(logging.WARNING)
else:
    SPOTIPY_REDIRECT_URI1 = 'http://localhost:8888/callback1'
    SPOTIPY_REDIRECT_URI2 = 'http://localhost:8888/callback2'

SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'
CACHE = '.spotipyoauthcache'

STATE1 = algs.generateRandomString(16)
STATE2 = algs.generateRandomString(16)

sp_oauth1 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI1,state=STATE1,scope=SCOPE,cache_path=CACHE,show_dialog=True)
sp_oauth2 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI2,state=STATE2,scope=SCOPE,cache_path=CACHE,show_dialog=True)


INTERSECTION_PLAYLIST = {}

# list of the tracks and playlists for each user where the key is the integer user id
TRACKS_DICT = {}
SONG_SOURCES_DICT = {}
SELECTED = {}

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

# VIEWS

@app.route('/')
@app.route('/index')
def index():       
    auth_url1 = sp_oauth1.get_authorize_url()
    return render_template("first.html", auth_url=auth_url1)


@app.route('/callback1')
def callback1():
    code = request.args.get('code')
    state = request.args.get('state')

    if code and state == STATE1:
        token = sp_oauth1.get_access_token(code)
        session["TOKEN1"] = token
        auth_url2 = sp_oauth2.get_authorize_url()
        return render_template("second.html", auth_url=auth_url2)

    else:
        return redirect(url_for('index'))

@app.route('/callback2')
def callback2():
    code = request.args.get('code')
    state = request.args.get('state')

    if code and state == STATE2:
        token = sp_oauth2.get_access_token(code)
        session["TOKEN2"] = token

        access_token2 = token["access_token"]

        return redirect(url_for('options'))

    else:
        return redirect(url_for('index'))

@app.route('/options')
def options():
    sp1, sp2 = getSpotifyClient(1), getSpotifyClient(2)
    log.info ("--------------------------------------")
    log.info ('Compatify attempt:')
    message = u"users %s and %s" % (sp1.me()["display_name"], sp2.me()["display_name"])

    # print (message.decode("latin1"))
    # message = message.decode("latin1").encode('utf-8')
    log.info (message)
    return render_template("options.html")

@app.route('/songsSelected')
def songsSelected():
    user = '1'
    sp = getSpotifyClient(user)
    message = getLoadingMessage('loadSaved', sp.me()["display_name"], user)

    return render_template("loading.html", message=message, user=user,
                                url="/getSongs/saved")

@app.route('/loadingPlaylists')
def loadingPlaylists():
    user = request.args.get("user")
    sp = getSpotifyClient(user)

    message = getLoadingMessage('loadPlaylists', sp.me()["display_name"], user)

    return render_template("loading.html", message=message,
                                user=user, url="/playlists")

@app.route('/playlists')
def playlists():
    user = request.args.get("user")
    sp = getSpotifyClient(user)

    message = getLoadingMessage('loadPlaylists', sp.me()["display_name"], user)

    def get_playlists():

        complete_playlist_list = []
        template = 'loading.html'
        context = {'user': user, 'message': message, 'url': '/select'}
        yield render_template(template, **context)
        while True:

            playlists, completed = getAllUserObjects(sp, "playlists",
                                        starting_offset=len(complete_playlist_list),
                                        timeout=3)
            complete_playlist_list += playlists

            if completed:
                break
            else:
                yield '<p style="display:none;"></p>'

        SONG_SOURCES_DICT[int(user)] = complete_playlist_list

    return Response(stream_with_context(get_playlists()))

@app.route('/select', methods = ['GET', 'POST'])
def select():
    MAX_SONGS_TO_DISPLAY = 15
    user = request.args.get("user")
    url = "/getSongs/playlists"

    sp = getSpotifyClient(user)
    name = sp.me()["display_name"]
    message = getLoadingMessage('loadFromSources', sp.me()["display_name"], user)


    playlists = SONG_SOURCES_DICT[int(user)]
    source_choices = list(map(lambda x : (x.id, x.name), playlists))
    source_choices = [("saved", "Your Saved Songs")] + source_choices

    form = SelectForm()
    form.response.choices =  source_choices
    if(form.is_submitted()):

        selection = form.data["response"]
        selected_objects = []

        # save the selected playlists for the user, but don't count the saved
        # songs as playlist if it's chosen to be included.
        if selection[0] == "saved":
            selected_objects.append(selection[0])
            selection = selection[1:]

        selected_objects += [p for p in playlists if p.id in selection]
        SONG_SOURCES_DICT[int(user)] = selected_objects

        return render_template("loading.html", message=message, user=user,
                                url=url)

    # We don't the playlist selection drop down to be too big if there are a lot of
    # playlists.
    display_size = min(MAX_SONGS_TO_DISPLAY, len(source_choices) + 1)
    return render_template("select.html",
                            message=message, user=user, form = form, name=name,
                            display_size=display_size)

@app.route('/getSongs/<source>')
def getSongs(source):
    user = request.args.get("user")
    sp = getSpotifyClient(user)

    # Set how the app should direct after loading all songs
    template = 'loading.html'

    if not source == "playlists":
        message = getLoadingMessage('loadSaved', sp.me()["display_name"], user)

    else:
        message = getLoadingMessage('loadFromSources', sp.me()["display_name"], user)

    context = {'user': user, 'message': message,
               'url': '/getSongsRedirect/' + source}

    # If playlist user was not selected, the only song source is the saved tracks
    if not source == "playlists":
        song_sources = ['saved']
    else:
        song_sources = SONG_SOURCES_DICT[int(user)]

    def get_songs(user, song_sources):
        sp = getSpotifyClient(user)
        complete_song_list = []

        yield render_template(template, **context)

        #if the user wants to include saved songs
        if song_sources[0] == "saved":
            # getting the saved tracks uses a different function than getting playlists
            song_sources = song_sources[1:]
            
            while True:
            
                songs, completed = getAllUserObjects(sp, "tracks",
                                        starting_offset=len(complete_song_list),
                                        timeout=10)
                complete_song_list += songs

                yield '<p style="display:none;"></p>'
                if completed:
                    break

        # Load songs from Playlists chosen
        for playlist in song_sources:
            complete_song_list += playlist.tracks

        TRACKS_DICT[int(user)] = complete_song_list
        

    return Response(stream_with_context(get_songs(user, song_sources)))

@app.route('/getSongsRedirect/<source>')
def getSongsRedirect(source):
    user = request.args.get("user")
    second_user = '2'
    if user == '1':

        sp = getSpotifyClient(second_user)
        ''' loading message is different for playlist and saved songs since this
        funtion is used before the smain loading of objects when doing saved
        songs but after the long step when using playlists. '''

        if not source == "playlists":
            message = getLoadingMessage('loadSaved', sp.me()["display_name"], second_user)
            url = '/getSongs/saved'
        else:
            message = getLoadingMessage('loadPlaylists', sp.me()["display_name"], second_user)
            url = '/loadingPlaylists'
    else:
        message = "Comparing Songs..."
        url = url_for('comparison')

    return render_template("loading.html", message=message, user=second_user,
                                url=url)

@app.route('/comparison')
def comparison():
    tracks1 = TRACKS_DICT[1]
    tracks2 = TRACKS_DICT[2]
    sp1, sp2 = getSpotifyClient(1), getSpotifyClient(2)
    message = u"Compatify success for users %s and %s" % (sp1.me()["display_name"], sp2.me()["display_name"])
    # message = message.encode('utf-8')
    # print (message.decode("latin1"))
    log.info(message)

    if tracks1 == [] or tracks2 == []:
        intersection_songs, top5artists = [], []
        intersection_playlist_uris, intersection_playlist_names = [], []
        score, intersection_size = 0, 0
    else:

        intersection_songs = algs.intersection(tracks1, tracks2)
        intersection_size = len(intersection_songs)

        score = algs.compatabilityIndex(tracks1, tracks2, intersection_songs)

        top5artists = algs.topNArtists(intersection_songs, 5)

        intersection_playlist_names = algs.getInformation(intersection_songs, 'name')

        # filter out local tracks before making the shared playlist since they
        # cannot be included by spotify api.
        intersection_songs = list(filter(lambda song: not song.local, intersection_songs))

        intersection_playlist_uris = algs.getInformation(intersection_songs, 'uri')

    INTERSECTION_PLAYLIST["uris"] = intersection_playlist_uris
    INTERSECTION_PLAYLIST["names"] = intersection_playlist_names

    return render_template("last.html", score=int(score),
                            count=intersection_size, artists=top5artists,
                            success_page=url_for('success'))


@app.route('/success')
def success():
    token1 = session["TOKEN1"]
    token2 = session["TOKEN2"]
    access_token1 = token1["access_token"]
    access_token2 = token2["access_token"]
    intersection_songs = INTERSECTION_PLAYLIST["uris"]
    intersection_names = INTERSECTION_PLAYLIST["names"]

    session.clear()

    sp1 = spotipy.Spotify(auth=access_token1)
    sp2 = spotipy.Spotify(auth=access_token2)

    user1, user2 = sp1.me(), sp2.me()

    user_id1, user_id2 = user1["id"], user2["id"]
    user_name1, user_name2 = user1["display_name"], user2["display_name"]

    if user_name1 == None:
        user_name1 = user_id1
    if user_name2 == None:
        user_name2 = user_id2

    playlist_name = 'Compatify ' + user_name1 + ' ' + user_name2

    new_playlist1 = sp1.user_playlist_create(user_id1, playlist_name, public=False)
    new_playlist2 = sp2.user_playlist_create(user_id2, playlist_name, public=False)

    size = len(intersection_songs)

    index = 0
    while True:
        current_num = size - index
        if current_num > 100:
            sp1.user_playlist_add_tracks(user_id1, new_playlist1["id"], intersection_songs[index:index+100], position=None)
            sp2.user_playlist_add_tracks(user_id2, new_playlist2["id"], intersection_songs[index:index+100], position=None)
            index += 100
        elif current_num > 0:
            sp1.user_playlist_add_tracks(user_id1, new_playlist1["id"], intersection_songs[index:index+current_num], position=None)
            sp2.user_playlist_add_tracks(user_id2, new_playlist2["id"], intersection_songs[index:index+current_num], position=None)
            break
        else:
            break
    # if not all songs have uris and can be included (i.e. if there were local tracks)
    if len(intersection_names) != len(intersection_songs):
        warning = "Warning: matching local tracks were found that were unable to be included in the playlist."
    else:
        warning = ''
    message = u"Playlist Made for users %s and %s" % (user_name1, user_name2)
    # print (message.decode("latin1"))
    log.info(message)
    return render_template("success.html", warning=warning)

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
        message = str(type(e)) + ":\t" + e.message.decode('utf-8').strip()

    elif isinstance(e, ConnectionError):
        message="There was en error connecting to the Spotify API. \
               Please check your network connection and try again. If the \
               problem persists, try selecting sources with fewer songs."
    elif isinstance(e, KeyError):
        message = "The application is missing session data due to an unexpected \
                   redirect. Please start again from the beginning.\n"
        message += '\n'
        message += str(e.message)

    elif isinstance(e, Timeout):
        message = "HTTP timeout error. Please check your network connection and \
                  try again."
    else:
        message = str(type(e)) + ":\t" + e.message.decode('utf-8').strip()
    log.error("Error occured:")
    log.error(message)
    # print (message)
    return render_template("error.html", message=message)


# Methods

def getSpotifyClient(user):
    key = "TOKEN" + str(user)
    access_token = session[key]["access_token"]
    sp = spotipy.Spotify(auth=access_token)
    return sp

def getLoadingMessage(key, name, user):
    if not name is None:
        name_string = ' User ' + name + "'s"
    else:
        name_string = ''

    if key == 'loadSaved':
        message = u"Loading%s Saved Songs..." %  name_string
        if str(user) != '1':
            message = 'Now ' + message

    elif key == 'loadPlaylists':
        message = u"Loading%s Playlist Options..." % name_string
        if str(user) != '1':
            message = 'Now ' + message

    elif key == 'loadFromSources':
        message = u"Loading%s Songs From the Chosen Sources..." % name_string
    else:
        message = 'Loading...'

    return message


""" Either get all of a user's saved tracks or saved playlists.

    returns:
        objects [arr]: array of the objecst requset
        completed: whether all of the objects that exit are returned. If
            completed is false, the call was terminated early to avoid a timeout.

    """
def getAllUserObjects(sp, userObject, starting_offset=0, timeout=None):
    start = time.time()

    objects = []
    OBJECTS_PER_TIME = 50
    offset=starting_offset
    completed = False
    # Disable spotify api retrying messges
    with suppress_stdout():
        while True:

            if userObject == "tracks":
                SPObjects = sp.current_user_saved_tracks(limit=OBJECTS_PER_TIME, offset=offset)

            elif userObject == "playlists" :
                #SPObjects = sp.current_user_playlists(limit=OBJECTS_PER_TIME, offset=offset)
                user = sp.me()["id"]
                SPObjects = sp.user_playlists(user, limit=OBJECTS_PER_TIME, offset=offset)
            else:
                raise TypeError ("getAllUserObjects is expecting to get only either"
                                 " saved_tracks or playlists")
                return []

            if not SPObjects or len(SPObjects["items"]) == 0:
                completed = True
                break
            for item in SPObjects["items"]:

                if userObject == "tracks":
                    track = item["track"]
                    created_item = create_song_obj_from_track_dict(sp, track)
                else: # userObject == "playlist"
                    created_item = create_playlist_obj_from_dict(sp, item)
                objects.append(created_item)

            offset += OBJECTS_PER_TIME

            # if the request is taking too long, stop this function
            if timeout and (time.time() - start) > timeout:
                return objects, completed

    return objects, completed

if __name__ == '__main__':
    log.addHandler(default_handler)
    log.setLevel(logging.INFO)
    app.run(host='0.0.0.0', port=PORT_NUMBER, debug=(not PRODUCTION))
