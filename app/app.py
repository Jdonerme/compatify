from flask import Flask, render_template, request, json
import spotipy
import json
import random, math
from spotipy import oauth2

app = Flask(__name__)



# Methods

def generateRandomState(length): 
    text = '';
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

    for i in range(length):
        text += possible[int(math.floor(random.random() * len(possible)))]

    return text





# GLOBAL VARIABLES

PORT_NUMBER = 8888
SPOTIPY_CLIENT_ID = '883896384d0c4d158bab154c01de29db'
SPOTIPY_CLIENT_SECRET = '37443ee0c0404c44b755f3ed97c48493'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'user-library-read playlist-modify-public'
CACHE = '.spotipyoauthcache'
STATE = generateRandomState(16)

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,state=STATE,scope=SCOPE,cache_path=CACHE,show_dialog=True)






# VIEWS

@app.route('/')
@app.route('/index')
def index():       
    auth_url = sp_oauth.get_authorize_url()
    return render_template("index.html", auth_url=auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    token = sp_oauth.get_access_token(code)
    sp = spotipy.Spotify(auth=token)
    tracks1 = sp.current_user_saved_tracks(limit=20, offset=0) 

    string = "<p>state: " + state + "</p><p>code: " + code + "</p><p>token: " + json.dumps(token) + "</p>"
    return string













#return render_template("index.html")














if __name__ == '__main__':
    app.run(port=PORT_NUMBER, debug=True)