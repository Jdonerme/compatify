from flask import Flask, render_template, request, json
import spotipy
import random, math
from spotipy import oauth2

app = Flask(__name__)



# Methods
def htmlForLoginButton():
    auth_url = sp_oauth.get_authorize_url()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

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
SCOPE = 'user-library-read'
CACHE = '.spotipyoauthcache'
STATE = generateRandomState(16)

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,state=STATE,scope=SCOPE,cache_path=CACHE )






# VIEWS

@app.route('/')
@app.route('/index')
def index():       
    """
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print "Found cached token!"
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print "Found Spotify auth code in Request URL! Trying to get valid access token..."
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print "Access token available! Trying to get user information..."
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return results

    else:
        """
    #return htmlForLoginButton()
    auth_url = sp_oauth.get_authorize_url()
    return render_template("index.html", auth_url=auth_url)

@app.route('/callback')
def callback():
    string = "<p>state: " + request.args.get('state') + "</p><p>code: " + request.args.get('code') + "</p>"
    return string













#return render_template("index.html")














if __name__ == '__main__':
    app.run(port=PORT_NUMBER, debug=True)