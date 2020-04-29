import os
import psycopg2
import pandas as pd
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from model import get_results
import numpy as np
# from spotify_flask_app.model import KNN_Model
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



# pip install Flask-Migrate
# pip install Flask-SQLAlchemy

# insertion_query = "INSERT INTO test_table (name, data) VALUES %s"
# execute_values(cursor, insertion_query, rows_to_insert)
# ​
# ​

def create_app():
    app = Flask(__name__)
    CORS(app)
    db = SQLAlchemy(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://phmcuozt:Hl4xzpVOZxiQ9af4kH5bavoEHIx7z3hn@drona.db.elephantsql.com:5432/phmcuozt'

    @app.route("/")
    def index():
        return "Home Page"

    @app.route("/data")
    def april_spotify_data():
        conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
        cur = conn.cursor()
        query_1 = '''
        SELECT *
        FROM spotify_table
        LIMIT 100
        '''
        cur.execute(query_1)
        results = cur.fetchall()
        conn.close()
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

    @app.route("/search_something/<artist_name>/<track_name>")
    def get_stuff(artist_name, track_name):
        result = sp.search(q=f'artist:{artist_name} track:{track_name}')
        track_id = result['tracks']['items'][0]['id']
        track_name = result['tracks']['items'][0]['name']
        track_name_json = jsonify(track_name)
        artist_name = result['tracks']['items'][0]['artists'][0]['name']
        album_name = result['tracks']['items'][0]['album']['name']
        album_id = result['tracks']['items'][0]['album']['id']
        album_cover_link = result['tracks']['items'][0]['album']['images'][0]['url']
        song_sample = result['tracks']['items'][0]['preview_url']
        audio_features = sp.audio_features(track_id)
        audio_features = audio_features[0]
        keys_to_remove = ["uri", "analysis_url", "type", "track_href"]
        for key in keys_to_remove:
          del audio_features[key]
        audio_features_df = pd.DataFrame(audio_features, index=[0])
        audio_features_json = jsonify(audio_features)
        #MODEL RETURNS 6 RECOMMENDS
        conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
        # model_results = "HI"
        model_query = '''
        SELECT *
        FROM spotify_table
        '''
        model_results = get_results(audio_features_df, pd.read_sql_query(model_query, conn).drop(['track_name', 'artist_name'], axis=1))
        conn.close()
        model_track_ids = model_results.id
        model_result_query = sp.tracks(model_track_ids)
        results_dict_list = {}
        for i in range(6):
            results_dict = {k:np.nan for k in ['artist', 'track_name', 'track_id', 'album_cover']}
            results_dict['artist'] = model_result_query['tracks'][i]['artists'][0]['name']
            results_dict['track_name'] = model_result_query['tracks'][i]['name']
            results_dict['track_id'] = model_result_query['tracks'][i]['id']
            results_dict['album_cover'] = model_result_query['tracks'][i]['album']['images'][0]['url']
            results_dict_list[i] = results_dict
        return jsonify(results_dict_list)
       
     

        # return render_template("button.html", result=result, track_id=track_id, track_name=track_name, artist_name=artist_name, album_name=album_name, album_id=album_id, album_cover_link=album_cover_link, song_sample=song_sample, audio_features=audio_features) 
        # return jsonify(track_id, track)

    return app