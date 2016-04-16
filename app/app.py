from flask import Flask, render_template, request, redirect, url_for, json, session
import spotipy
from spotipy import oauth2

import algs

app = Flask(__name__)

app.secret_key = algs.generateRandomString(16)



# GLOBAL VARIABLES

PORT_NUMBER = 8888
SPOTIPY_CLIENT_ID = '883896384d0c4d158bab154c01de29db'
SPOTIPY_CLIENT_SECRET = '37443ee0c0404c44b755f3ed97c48493'
SPOTIPY_REDIRECT_URI1 = 'http://localhost:8888/callback1'
SPOTIPY_REDIRECT_URI2 = 'http://localhost:8888/callback2'
SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private'
CACHE = '.spotipyoauthcache'
STATE1 = algs.generateRandomString(16)
STATE2 = algs.generateRandomString(16)

sp_oauth1 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI1,state=STATE1,scope=SCOPE,cache_path=CACHE,show_dialog=True)
sp_oauth2 = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI2,state=STATE2,scope=SCOPE,cache_path=CACHE,show_dialog=True)




# VIEWS

@app.route('/')
@app.route('/index')
def index():       
    auth_url1 = sp_oauth1.get_authorize_url()
    return render_template("index.html", auth_url=auth_url1)



@app.route('/callback1')
def callback1():
    code = request.args.get('code')
    state = request.args.get('state')

    if code and state == STATE1:
        token = sp_oauth1.get_access_token(code)
        access_token = token["access_token"]

        sp1 = spotipy.Spotify(auth=access_token)

        tracks1 = getAllTracks(sp1)
        session["tracks1"] = tracks1

        auth_url2 = sp_oauth2.get_authorize_url()
        return render_template("index.html", auth_url=auth_url2)

    else:
        return redirect(url_for('index'))

@app.route('/callback2')
def callback2():
    code = request.args.get('code')
    state = request.args.get('state')

    if code and state == STATE2:
        token = sp_oauth2.get_access_token(code)
        access_token = token["access_token"]

        sp2 = spotipy.Spotify(auth=access_token)

        tracks2 = getAllTracks(sp2)
        #session["tracks2"] = tracks2

        return render_template("songs.html", tracks1=session["tracks1"], tracks2=tracks2)

    else:
        return redirect(url_for('index'))






# Methods

def getAllTracks(sp):
    tracks = []

    SONGS_PER_TIME = 50
    offset=0

    while True:
        SPTracks = sp.current_user_saved_tracks(limit=SONGS_PER_TIME, offset=offset) 

        #if len(SPTracks["items"]) == 0:
        if offset == 50:
            break

        for song in SPTracks["items"]:
            track = song["track"]
            song_item = { "name": track["name"], "uri": track["uri"], "artist": track["artists"][0]["name"], "album": track["album"]["name"] }
            tracks.append(song_item)

        offset += SONGS_PER_TIME

    return tracks


















if __name__ == '__main__':
    app.run(port=PORT_NUMBER, debug=True)