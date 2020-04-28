import os
import psycopg2
import pandas as pd
from flask import Flask, jsonify
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID,
                                                     client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# from flask_migrate import Migrate
# from psycopg2.extras import execute_values

db = SQLAlchemy()
# migrate = Migrate()

SPOTIFY_DB_NAME = os.getenv("SPOTIFY_DB_NAME")
SPOTIFY_DB_PW = os.getenv("SPOTIFY_DB_PW")
SPOTIFY_DB_HOST = os.getenv("SPOTIFY_DB_HOST")
SPOTIFY_DB_USER = os.getenv("SPOTIFY_DB_USER")

conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
cur = conn.cursor()

# pip install Flask-Migrate
# pip install Flask-SQLAlchemy

# insertion_query = "INSERT INTO test_table (name, data) VALUES %s"
# execute_values(cursor, insertion_query, rows_to_insert)
# ​
# ​

def create_app():
    app = Flask(__name__)
    db = SQLAlchemy(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://phmcuozt:Gq5822Z4v3ypBvLtnCsF4XjabVM3LKr9@drona.db.elephantsql.com:5432/phmcuozt'

    @app.route("/")
    def index():
        return "Home Page"

    @app.route("/data")
    def april_spotify_data():
        query_1 = '''
        SELECT *
        FROM april_spotify
        LIMIT 1000
        '''
        cur.execute(query_1)
        results = cur.fetchall()
        return jsonify(results)

    @app.route("/<user>/<playlist_id>")
    def playlist_audio_features(user=None, playlist_id=None):
        playlist = sp.user_playlist(user=user, playlist_id=playlist_id)
        songs = playlist["tracks"]["items"] 
        
        ids = [] 
        for i in range(len(songs)): 
            ids.append(songs[i]["track"]["id"])
        
        features = sp.audio_features(ids)
        print(type(features))
        print(len(features))
        return jsonify(features)

    @app.route("/dummy_data")
    def dummy_data():
        dummy_data = [
            {
                'song': 'My Boo',
                'artist': "Usher",
                'album': 'Confessions (Expanded Edition)',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273365b3fb800c19f7ff72602da'
            },
            {
                'song': 'Sorry',
                'artist': "Justin Bieber",
                'album': 'Purpose (Deluxe)',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273f46b9d202509a8f7384b90de'
            },
            {
                'song': 'See Through',
                'artist': "The Band CAMINO",
                'album': 'tryhard',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273f232b955ad8637ecd04bfdf7'
            },
            {
                'song': 'Heaven',
                'artist': "Avicii",
                'album': 'TIM',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273660ee24281a547103f466ff5'
            },
            {
                'song': 'Here And Now',
                'artist': "Kenny Chesney",
                'album': 'Here And Now',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273c559a84d5a37627db8c76a8a'
            },
            {
                'song': 'Halo',
                'artist': "Beyonce",
                'album': 'I AM...SASHA FIERCE',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273e13de7b8662b085b0885ffef'
            }
        ]
        return jsonify(dummy_data)


