from flask import Flask, render_template, request, redirect, url_for, session
import json
import spotipy
from spotipy import oauth2
import os
import algs

app = Flask(__name__)

app.secret_key = algs.generateRandomString(16)

# GLOBAL VARIABLES

PORT_NUMBER = int(os.environ.get('PORT', 8888))
SPOTIPY_CLIENT_ID = '883896384d0c4d158bab154c01de29db'
SPOTIPY_CLIENT_SECRET = '37443ee0c0404c44b755f3ed97c48493'

PRODUCTION = True

if PRODUCTION:
    SPOTIPY_REDIRECT_URI1 = 'https://compatify.herokuapp.com/callback1'
    SPOTIPY_REDIRECT_URI2 = 'https://compatify.herokuapp.com/callback2'
else:
    SPOTIPY_REDIRECT_URI1 = 'http://localhost:8888/callback1'
    SPOTIPY_REDIRECT_URI2 = 'http://localhost:8888/callback2'


SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'
CACHE = '.spotipyoauthcache'

STATE1 = algs.generateRandomString(16)
STATE2 = algs.generateRandomString(16)

sp_oauth1 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI1,state=STATE1,scope=SCOPE,cache_path=CACHE,show_dialog=True)
sp_oauth2 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI2,state=STATE2,scope=SCOPE,cache_path=CACHE,show_dialog=True)


# NEED TO REMOVE
TRACK_SAVE = None
TOKEN1 = None
TOKEN2 = None
INTERSECTION = None

SP1 = None
SP2 = None


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
        return render_template("loading2.html")

    else:
        return redirect(url_for('index'))

@app.route('/getsongs2')
def getsongs2():

    token1 = session["TOKEN1"]
    token2 = session["TOKEN2"]
    access_token1 = token1["access_token"]
    access_token2 = token2["access_token"]

    sp1 = spotipy.Spotify(auth=access_token1)
    sp2 = spotipy.Spotify(auth=access_token2)

    tracks1 = getAllTracks(sp1)
    tracks2 = getAllTracks(sp2)

    score = algs.CompatabilityIndex(tracks1, tracks2)

    top5artists = algs.TopNArtists(tracks1, tracks2, 5)

    intersection_songs = algs.IntersectionPlaylist(tracks1, tracks2)
    intersection_size = len(intersection_songs)

    session["INTERSECTION"] = json.dumps(intersection_songs)

    return render_template("last.html", score=int(score), count=intersection_size, artists=top5artists, success_page=url_for('success'))

@app.route('/success')
def success():
    token1 = session["TOKEN1"]
    token2 = session["TOKEN2"]
    access_token1 = token1["access_token"]
    access_token2 = token2["access_token"]

    sp1 = spotipy.Spotify(auth=access_token1)
    sp2 = spotipy.Spotify(auth=access_token2)

    user_id1 = sp1.me()["id"]
    user_id2 = sp2.me()["id"]

    intersection_songs = json.loads(session["INTERSECTION"])
    session.clear()

    playlist_name = 'Compatify-' + user_id1 + '-' + user_id2

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
    return render_template("success.html")


# Methods

def getAllTracks(sp):
    tracks = []

    SONGS_PER_TIME = 50
    offset=0

    while True:
        SPTracks = sp.current_user_saved_tracks(limit=SONGS_PER_TIME, offset=offset) 

        if len(SPTracks["items"]) == 0:
        #if offset >= 50:
            break

        for song in SPTracks["items"]:
            track = song["track"]
            song_item = { "name": track["name"], "uri": track["uri"], "artist": track["artists"][0]["name"], "album": track["album"]["name"] }
            tracks.append(song_item)

        offset += SONGS_PER_TIME

    return tracks
'''
def createIntersection(sp):
    sp.user



'''






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_NUMBER, debug=True)