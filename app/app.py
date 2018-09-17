from flask import Flask, render_template, request, redirect, url_for, session
import spotipy
from spotipy import oauth2
import os
import algs
from Song import Song

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


INTERSECTION_DICT = {}
TRACKS_DICT = {}


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
        return render_template("loading.html",
                                message="Loading User 1 Songs", user=0)

    else:
        return redirect(url_for('index'))

@app.route('/getSongs')
def getSongs():
    user = request.args.get("user")
    token1 = session["TOKEN1"]
    access_token1 = token1["access_token"]
    token2 = session["TOKEN2"]

    if user == '0':

        sp1 = spotipy.Spotify(auth=access_token1)

        tracks1 = getAllTracks(sp1)
        TRACKS_DICT[1] = tracks1

        return render_template("loading.html", 
                                message="Loading User 2 Songs", user=2)

    access_token2 = token2["access_token"]
    sp2 = spotipy.Spotify(auth=access_token2)

    tracks2 = getAllTracks(sp2)

    TRACKS_DICT[2] = tracks2
    tracks1 = TRACKS_DICT[1]

    intersection_songs = algs.intersection(tracks1, tracks2)

    intersection_playlist = algs.getInformation(intersection_songs, 'uri')

    score = algs.compatabilityIndex(tracks1, tracks2, intersection_songs)

    top5artists = algs.topNArtists(intersection_songs, 5)

    
    intersection_size = len(intersection_playlist)

    INTERSECTION_DICT[access_token1 + "_" + access_token2] = intersection_playlist

    return render_template("last.html", score=int(score), count=intersection_size, artists=top5artists, success_page=url_for('success'))

@app.route('/success')
def success():
    token1 = session["TOKEN1"]
    token2 = session["TOKEN2"]
    access_token1 = token1["access_token"]
    access_token2 = token2["access_token"]
    session.clear()

    intersection_songs = INTERSECTION_DICT[access_token1 + "_" + access_token2]
    del INTERSECTION_DICT[access_token1 + "_" + access_token2]


    sp1 = spotipy.Spotify(auth=access_token1)
    sp2 = spotipy.Spotify(auth=access_token2)

    user_id1 = sp1.me()["id"]
    user_id2 = sp2.me()["id"]

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
            break
        for song in SPTracks["items"]:
            track = song["track"]

            song_item = \
                Song(sp, track["uri"], track["name"], track["artists"][0]["name"],
                     map(lambda x: x["name"], track["artists"][1:]), 
                     track["album"]["name"], track["duration_ms"])
            tracks.append(song_item)

        offset += SONGS_PER_TIME

    return tracks

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT_NUMBER, debug=True)
