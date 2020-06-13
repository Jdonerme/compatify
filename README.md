Compatify
========

![Screenshot](/home.jpg "Home Screen")

*Test your music compatibility with your friends and significant others!*

Live Website: https://compatify.herokuapp.com/

Inspiration
-----------

Music is a window to the soul. We wanted to peek into the hearts of our friends
to test their musical compatibilities with us.

Description
-----------

Compatify was a project we completed over 12 hours at the 5C Hackathon 
(Spring 2016) at Pomona College. The app looks at Spotify users' saved music and
determines the similarity in their tastes in music. When two users use Compatify,
it also creates a playlist of songs that both of the users enjoy.

In 2018, an update was added so that different tracks that corresponded to the 
same version of the same song would be recognized as identical. (i.e. the deluxe 
album track and the normal album track are still considred the same song. 
Different versions of the same song are still considered distinct.

Songs are considered the same if they are of the same length, have the same 
artists and have the same title.

How We Built It
---------------

We used Python, Flask, and Spotipy to develop our backend, and HTML/CSS, Bootstrap, Javascript, and D3.js to develop our frontend.

Roles
-----

Frontend & Design: Catherine Ma, Celia Zhang

Backend & Spotify API: Joon Hee Lee

Logic & Algorithms: Joseph Donermeyer

Local Use
-----------
To install requirements, run
pip install -r requirements.txt

Then, from the app folder, run
python3 app.py

For local use, the production variable in app.py needs to be set to False. The service will run
on port 8888
