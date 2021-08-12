# -*- coding: utf-8 -*
from flask import (
    Flask, render_template, request, redirect, url_for, session, Response,
    stream_with_context, render_template_string)
from flask.logging import default_handler
import spotipy, sys, os, algs, requests
from contextlib import contextmanager
from Song import Song, create_song_obj_from_track_dict
from Playlist import Playlist, create_playlist_obj_from_dict
from State import State
from forms import SelectForm
from requests import ConnectionError , Timeout
from werkzeug.exceptions import HTTPException
import datetime, time
import logging

app = Flask(__name__)
app.secret_key = algs.generateRandomString(16)
app.url_map.strict_slashes = False

# GLOBAL VARIABLES
log = logging.getLogger('my-logger')

PORT_NUMBER = int(os.environ.get('PORT', 8888))
# general
MATCH_PLAYLIST_ID = '10eJ5YNR0xdDUUgZkx48MP'

# c-go-to
# MATCH_PLAYLIST_ID='2CDvmrW3OY4AC3KSKwrz7m'

''' Store all states that have been created.
Data is stored as a tuple, with the first element being the state and the second
the date the state was created. '''
STATES = {}
PRODUCTION = True if 'PRODUCTION' in os.environ and os.environ['PRODUCTION'].lower() == 'true' else False

if PRODUCTION:
    # Set flask logs to "warning level only in production builds"
    flaskLog = logging.getLogger('werkzeug')
    flaskLog.setLevel(logging.WARNING)
    app.logger.setLevel(logging.WARNING)

# list of the tracks and playlists for each user where the key is the integer user id

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
@app.route('/<view>')
@app.route('/index/<view>')
def index(view=''):
    clearOldStates()
    if "session_id" in session:
        session_id = session["session_id"]
        STATE = STATES[session_id][0]
    else:
        session_id = algs.generateRandomString(16)
        session["session_id"] = session_id
        STATE = State(production = PRODUCTION)
        STATES[session_id] = (STATE, datetime.date.today())

    if (view != "favicon.ico" and STATE.isDirty()):
        STATE.clean()
    sp_oauth1 = STATE.getOAuthObjects(1)
    auth_url1 = sp_oauth1.get_authorize_url()
    message = "How compatible are your music tastes?"
    if view and view.lower() == 'match':
        message = "How compatible are our music tastes?"
        STATE.enableMatchMode()
    elif (view != "favicon.ico"):
        STATE.disableMatchMode()
    return render_template("first.html", auth_url=auth_url1,
                            message=message, match=STATE.inMatchMode())

@app.route('/callback1')
def callback1():
    code = request.args.get('code')
    state = request.args.get('state')

    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    if code and state == STATE.getOAuthKeys(1):
        token = STATE.getOAuthObjects(1).get_access_token(code)
        session["TOKEN1"] = token
        if STATE.inMatchMode():
            # TODO get an auth token for my account for playlist making
            session["TOKEN2"] = token
            return redirect(url_for('options'))

        auth_url2 = STATE.getOAuthObjects(2).get_authorize_url()
        return render_template("second.html", auth_url=auth_url2)

    else:
        return redirect(url_for('index'))

@app.route('/callback2')
def callback2():
    code = request.args.get('code')
    state = request.args.get('state')
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    if code and state == STATE.getOAuthKeys(2):
        token = STATE.getOAuthObjects(2).get_access_token(code)
        session["TOKEN2"] = token

        access_token2 = token["access_token"]

        return redirect(url_for('options'))

    else:
        return redirect(url_for('index'))

@app.route('/options')
def options():
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    log.info ("--------------------------------------")
    sp1 = getSpotifyClient(1)
    STATE.saveUserInfo(1, sp1.me())
    if not STATE.inMatchMode():
        sp2 = getSpotifyClient(2)
        STATE.saveUserInfo(2, sp2.me())
        message = u"Compatify attempt for users %s and %s" % (STATE.getUserInfoObjects(1)["display_name"], STATE.getUserInfoObjects(2)["display_name"])
    else:
        message = u"Compatify match from user %s!" % STATE.getUserInfoObjects(1)["display_name"]
        STATE.saveUserInfo(2, STATE.getUserInfoObjects(1))

    log.info (message)
    return render_template("options.html")

@app.route('/songsSelected')
def songsSelected():
    user = '1'
    sp = getSpotifyClient(user)
    message = getLoadingMessage('loadSaved', user)

    return render_template("loading.html", message=message, user=user,
                                url="/getSongs/saved")

@app.route('/loadingPlaylists')
def loadingPlaylists():
    user = request.args.get("user")
    sp = getSpotifyClient(user)

    message = getLoadingMessage('loadPlaylists', user)

    return render_template("loading.html", message=message,
                                user=user, url="/playlists")

@app.route('/playlists')
def playlists():
    user = request.args.get("user")
    sp = getSpotifyClient(user)
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    message = getLoadingMessage('loadPlaylists', user)

    def get_playlists():

        complete_playlist_list = []
        template = 'loading.html'
        context = {'user': user, 'message': message, 'url': '/select'}
        yield render_template(template, **context)
        while True:

            playlists, completed = getAllUserObjects(sp, "playlists", user,
                                        starting_offset=len(complete_playlist_list),
                                        timeout=15)
            complete_playlist_list += playlists

            if completed:
                break
            else:
                yield '<p style="display:none;"></p>'
        song_sources_dict = STATE.getSongSourcesDict()
        song_sources_dict[int(user)] = complete_playlist_list

    return Response(stream_with_context(get_playlists()))

@app.route('/select', methods = ['GET', 'POST'])
def select():
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    MAX_SONGS_TO_DISPLAY = 15
    user = request.args.get("user")
    url = "/getSongs/playlists"

    message = getLoadingMessage('loadFromSources', user)

    song_sources_dict = STATE.getSongSourcesDict()
    playlists = song_sources_dict[int(user)]

    user_info = STATE.getUserInfoObjects(user)
    name = user_info["display_name"] if user_info["display_name"] else "User " + user_info["id"]

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
        song_sources_dict[int(user)] = selected_objects

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
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    user = request.args.get("user")

    # Set how the app should direct after loading all songs
    template = 'loading.html'
    sp = getSpotifyClient(user)

    # if getting the songs for the match mode user, get songs from the public playlist defiend by MATCH_PLAYLIST_ID
    if STATE.inMatchMode() and user == '2':
        song_sources_dict = STATE.getSongSourcesDict()
        song_sources_dict[int(user)] = [getPublicPlaylist(sp, MATCH_PLAYLIST_ID)]
        song_sources = song_sources_dict[int(user)]
        message = getLoadingMessage('loadSaved', user)
    else:
        # If playlist source was not selected, the only song source is the saved tracks
        if not source == "playlists":
            message = getLoadingMessage('loadSaved', user)
            song_sources = ['saved']
        else:
            message = getLoadingMessage('loadFromSources', user)
            song_sources_dict = STATE.getSongSourcesDict()
            song_sources = song_sources_dict[int(user)]

    context = {'user': user, 'message': message,
               'url': '/getSongsRedirect/' + source}

    def get_songs(user, song_sources):
        sp = getSpotifyClient(user)
        complete_song_list = []

        yield render_template(template, **context)

        #if the user wants to include saved songs
        if song_sources[0] == "saved":
            # getting the saved tracks uses a different function than getting playlists
            song_sources = song_sources[1:]
            
            while True:
            
                songs, completed = getAllUserObjects(sp, "tracks", user,
                                        starting_offset=len(complete_song_list),
                                        timeout=10)
                complete_song_list += songs

                yield '<p style="display:none;"></p>'
                if completed:
                    break

        # Load songs from Playlists chosen
        for playlist in song_sources:
            complete_song_list += playlist.tracks

        tracks_dict = STATE.getTracksDict()
        tracks_dict[int(user)] = complete_song_list
        

    return Response(stream_with_context(get_songs(user, song_sources)))

@app.route('/getSongsRedirect/<source>')
def getSongsRedirect(source):
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    user = request.args.get("user")
    second_user = '2'
    if user == '1':
        if STATE.inMatchMode():
            sp = None
            url = '/getSongs/playlists'
            message = getLoadingMessage('', second_user)
        else:
            sp = getSpotifyClient(second_user)
            ''' loading message is different for playlist and saved songs since this
            function is used before the main loading of objects when doing saved
            songs but after the long step when using playlists. '''

            if not source == "playlists":
                message = getLoadingMessage('loadSaved', second_user)
                url = '/getSongs/saved'
            else:
                message = getLoadingMessage('loadPlaylists', second_user)
                url = '/loadingPlaylists'
    else:
        message = "Comparing Songs..."
        url = url_for('comparison')

    return render_template("loading.html", message=message, user=second_user,
                                url=url)

@app.route('/comparison')
def comparison():
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    tracks_dict = STATE.getTracksDict()
    tracks1 = tracks_dict[1]
    tracks2 = tracks_dict[2]
    sp1, sp2 = getSpotifyClient(1), getSpotifyClient(2)
    message = u"Compatify success for users %s and %s" % (STATE.getUserInfoObjects(1)["display_name"], STATE.getUserInfoObjects(2)["display_name"])

    log.info(message)
    if (STATE.inMatchMode() and STATE.inProductionMode()):
        name = STATE.getUserInfoObjects(1)["display_name"]
        sendMatchNotifications(name)

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
        local_tracks = list(filter(lambda song: song.local, intersection_songs))
        warning = "Could not add local track: "
        [log.warning(warning + song.identifier) for song in local_tracks]
        intersection_songs = list(filter(lambda song: not song.local, intersection_songs))

        intersection_playlist_uris = algs.getInformation(intersection_songs, 'uri')

    intersection_playlist = STATE.getIntersectionPlaylist()
    intersection_playlist["uris"] = intersection_playlist_uris
    intersection_playlist["names"] = intersection_playlist_names

    return render_template("last.html", score=int(score),
                            count=intersection_size, artists=top5artists,
                            success_page=url_for('success'),
                            match=STATE.inMatchMode())


@app.route('/success')
def success():
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    token1 = session["TOKEN1"]
    token2 = session["TOKEN2"]
    access_token1 = token1["access_token"]
    access_token2 = token2["access_token"]
    
    intersection_playlist = STATE.getIntersectionPlaylist()
    intersection_songs = intersection_playlist["uris"]
    intersection_names = intersection_playlist["names"]

    session.clear()
    STATES.pop(session_id)


    sp1 = spotipy.Spotify(auth=access_token1)
    sp2 = spotipy.Spotify(auth=access_token2)

    user1, user2 = STATE.getUserInfoObjects(1), STATE.getUserInfoObjects(2)

    user_id1, user_id2 = user1["id"], user2["id"]
    user_name1, user_name2 = user1["display_name"], user2["display_name"]

    if user_name1 == None:
        user_name1 = user_id1
    if user_name2 == None:
        user_name2 = user_id2

    playlist_name = 'Compatify ' + user_name1
    if (not STATE.inMatchMode()):
        playlist_name += ' ' + user_name2

    new_playlist1 = sp1.user_playlist_create(user_id1, playlist_name, public=STATE.inMatchMode())
    makeSecondPlaylist = user_id1 != user_id2
    if makeSecondPlaylist:
        new_playlist2 = sp2.user_playlist_create(user_id2, playlist_name, public=STATE.inMatchMode())

    size = len(intersection_songs)
    if (STATE.inMatchMode()):
        url = new_playlist1['external_urls']['spotify']
        log.warning("Created Match playlist at: " + url)
        if STATE.inProductionMode():
            sendMatchNotifications(user_name1, url)

    index = 0
    while True:
        current_num = size - index
        if current_num > 100:
            sp1.user_playlist_add_tracks(user_id1, new_playlist1["id"], intersection_songs[index:index+100], position=None)
            if makeSecondPlaylist:
                sp2.user_playlist_add_tracks(user_id2, new_playlist2["id"], intersection_songs[index:index+100], position=None)
            index += 100
        elif current_num > 0:
            sp1.user_playlist_add_tracks(user_id1, new_playlist1["id"], intersection_songs[index:index+current_num], position=None)
            if makeSecondPlaylist:
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
    log.info(message)
    return render_template("success.html", warning=warning, match=STATE.inMatchMode())

@app.errorhandler(Exception)
def handle_error(e):
    match = False
    if "session_id" in session:
        session_id = session["session_id"]
        STATE = STATES[session_id][0]
        match = STATE.inMatchMode()

    code = 500
    message = ''
    if isinstance(e, HTTPException):
        code = e.code

    elif isinstance(e, ConnectionError):
        message="There was en error connecting to the Spotify API. \
               Please check your network connection and try again. If the \
               problem persists, try selecting sources with fewer songs."
    elif isinstance(e, KeyError):
        message = "The application is missing session data due to an unexpected \
                   redirect. Please start again from the beginning.\n"
        message += '\n'
        logging.exception(e)

    elif isinstance(e, Timeout):
        message = "HTTP timeout error. Please check your network connection and \
                  try again."
    else:
        message = "Something went wrong: " + str(type(e)) + "\t-\t" + str(e).strip()
        logging.exception(e)

    if message:
        log.error(message)
    return render_template("error.html", message=message, match=match)


# Methods

def getSpotifyClient(user):
    key = "TOKEN" + str(user)
    access_token = session[key]["access_token"]
    sp = spotipy.Spotify(auth=access_token)
    return sp

def getLoadingMessage(key, user):
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    if STATE.inMatchMode():
        if user == '1':
            name_string = 'Your'
        else:
            return "Loading My Songs..."
    else:
        user_info = STATE.getUserInfoObjects(user)
        if user_info:
            name_string = user_info["display_name"] if user_info["display_name"] else "User " + user_info["id"]
            name_string += "'s"
        else:
            name_string = 'Your'

    if key == 'loadSaved':
        message = u"Loading %s Saved Songs..." %  name_string
        if str(user) != '1':
            message = 'Now ' + message

    elif key == 'loadPlaylists':
        message = u"Loading %s Playlist Options..." % name_string
        if str(user) != '1':
            message = 'Now ' + message

    elif key == 'loadFromSources':
        message = u"Loading %s Songs From the Chosen Sources..." % name_string
    else:
        message = 'Loading...'

    return message

""" Load a public spotify playlist as a Playlist object using its id

    returns:
        playlist: an instance of the Playlist class containing the playlist
    """
def getPublicPlaylist(sp, playlist_id):
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

    rawPlaylist = sp.playlist(playlist_id)
    return create_playlist_obj_from_dict(sp, STATE.getUserInfoObjects(1), rawPlaylist)

""" Either get all of a user's saved tracks or saved playlists.

    returns:
        objects [arr]: array of the objecst requset
        completed: whether all of the objects that exit are returned. If
            completed is false, the call was terminated early to avoid a timeout.

    """
def getAllUserObjects(sp, userObject, user, starting_offset=0, timeout=None):
    session_id = session["session_id"]
    STATE = STATES[session_id][0]

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
                user_id = STATE.getUserInfoObjects(user)["id"]
                SPObjects = sp.user_playlists(user_id, limit=OBJECTS_PER_TIME, offset=offset)
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
                    created_item = create_playlist_obj_from_dict(sp, STATE.getUserInfoObjects(user), item)
                objects.append(created_item)

            offset += OBJECTS_PER_TIME

            # if the request is taking too long, stop this function
            if timeout and (time.time() - start) > timeout:
                return objects, completed

    return objects, completed

""" Delete stale data from the STATES dictionary.
    Any state that that is 2 days old or older will be deleted
    """
def clearOldStates():
    today = datetime.date.today()
    for session_id in STATES:
        creation_date = STATES[session_id][1]
        time_diff_days = (today - creation_date).days

        if time_diff_days >= 2:
            del STATES[session_id]

def sendMatchNotifications(name, url=None):
    if url:
        MSG = "New Compatify match playlist created by user %s at %s !" % (name, url)
    else:
        MSG = "Compatify match completed by user %s" % name
    sendMatchEmail(MSG)
    sendMatchText(MSG)

def sendMatchText(MSG):
    if "MATCH_PHONE_NUM" in os.environ and "TILL_URL" in os.environ:
        TILL_URL = os.environ.get("TILL_URL")
        PHONE_NUM = os.environ.get("MATCH_PHONE_NUM")

        requests.post(TILL_URL, json={
            "phone": [PHONE_NUM],
            "text" : MSG
        })

def sendMatchEmail(MSG):
    if "MAILGUN_API_KEY" in os.environ and "MAILGUN_DOMAIN" in os.environ and "MATCH_EMAIL" in os.environ:
        MAIL_GUN_KEY = os.environ.get("MAILGUN_API_KEY")
        MAIL_GUN_DOMAIN = os.environ.get("MAILGUN_DOMAIN")
        MATCH_EMAIL = os.environ.get("MATCH_EMAIL")

        MAIL_GUN_URL = "https://api.mailgun.net/v3/%s/messages" % MAIL_GUN_DOMAIN

        return requests.post(
            MAIL_GUN_URL,
            auth=("api", MAIL_GUN_KEY),
            data={"from": ("Compatify <mailgun@%s>" % MAIL_GUN_DOMAIN),
                "to": [MATCH_EMAIL],
                "subject": "New Compatify Match!",
                "text": MSG})

if __name__ == '__main__':
    log.addHandler(default_handler)
    log.setLevel(logging.INFO)
    app.run(host='0.0.0.0', port=PORT_NUMBER, debug=not PRODUCTION, threaded=True)
