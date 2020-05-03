import os
import psycopg2
import pandas as pd
import numpy as np
import spotipy
import joblib
import matplotlib
import matplotlib.pyplot as plt
import chart_studio
import chart_studio.plotly as py
import plotly.graph_objs as go
from spotipy.oauth2 import SpotifyClientCredentials
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from plotly.subplots import make_subplots
from sklearn.neighbors import NearestNeighbors
# from spotify_flask_app.model import KNN_Model

# load in enviorment variables from .env file
load_dotenv()

# Client and Secret IDs are required credentials for accessing the spotify api
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID,
                                                     client_secret=CLIENT_SECRET)

# instantiate the api object
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# credentials for accessing plotly
chart_studio.tools.set_credentials_file(username=os.getenv("CHART_USERNAME"), api_key=os.getenv("CHART_APIKEY"))


db = SQLAlchemy()

# ElephantSQL database credentials
SPOTIFY_DB_NAME = os.getenv("SPOTIFY_DB_NAME")
SPOTIFY_DB_PW = os.getenv("SPOTIFY_DB_PW")
SPOTIFY_DB_HOST = os.getenv("SPOTIFY_DB_HOST")
SPOTIFY_DB_USER = os.getenv("SPOTIFY_DB_USER")


def create_app():
    '''
    Creates the flask application
    '''
    app = Flask(__name__)
    CORS(app)
    db = SQLAlchemy(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgres://{SPOTIFY_DB_NAME}:{SPOTIFY_DB_PW}@{SPOTIFY_DB_HOST}:5432/{SPOTIFY_DB_USER}'

    @app.route("/")
    def index():
        return "Home Page"

    @app.route("/data")
    def april_spotify_data():
        '''
        This route returns data from the database stored in ElephantSQL.
        '''
        # Establish a connection to the database
        conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
        
        # Establish a cursor object and write the query we want to return
        cur = conn.cursor()
        query_1 = '''
        SELECT *
        FROM spotify_table
        LIMIT 100
        '''

        # Execute the query, and return the results, jsonified
        cur.execute(query_1)
        results = cur.fetchall()
        conn.close()
        return jsonify(results)

    @app.route("/<user>/<playlist_id>")
    def playlist_audio_features(user=None, playlist_id=None):
        '''
        Route that returns a series of songs in a given user's playlist with
        those songs' audio features. Takes in a user's spotify username
        and a public playlist id from one of their playlists.
        '''
        # to spotipy to grab a playlist based on user's input
        playlist = sp.user_playlist(user=user, playlist_id=playlist_id)

        # get songs from that playlist
        songs = playlist["tracks"]["items"] 
        
        # compile a list of track_ids in order to get audio features
        ids = [] 
        for i in range(len(songs)): 
            ids.append(songs[i]["track"]["id"])
        
        features = sp.audio_features(ids)
        print(type(features))
        print(len(features))
        return jsonify(features)

    @app.route("/dummy_data")
    def dummy_data():
        '''
        Route that includes dummy data. Mainly used for front end to demo.
        Returns jsonified list of 6 songs with its artist, album, and cover art
        '''
        dummy_data = [
            {
                'song': 'My Boo',
                'song_id': '68vgtRHr7iZHpzGpon6Jlo',
                'artist': "Usher",
                'album': 'Confessions (Expanded Edition)',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273365b3fb800c19f7ff72602da'
            },
            {
                'song': 'Sorry',
                'song_id': '09CtPGIpYB4BrO8qb1RGsF',
                'artist': "Justin Bieber",
                'album': 'Purpose (Deluxe)',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273f46b9d202509a8f7384b90de'
            },
            {
                'song': 'See Through',
                'song_id': '1pJzl0YsxaWj6BbPs1mUuQ',
                'artist': "The Band CAMINO",
                'album': 'tryhard',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273f232b955ad8637ecd04bfdf7'
            },
            {
                'song': 'Heaven',
                'song_id': '0vrmHPfoBadXVr2n0m1aqZ',
                'artist': "Avicii",
                'album': 'TIM',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273660ee24281a547103f466ff5'
            },
            {
                'song': 'Here And Now',
                'song_id': '0NSwXfEWMG7HIRvXioGu03',
                'artist': "Kenny Chesney",
                'album': 'Here And Now',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273c559a84d5a37627db8c76a8a'
            },
            {
                'song': 'Halo',
                'song_id': '4JehYebiI9JE8sR8MisGVb',
                'artist': "Beyonce",
                'album': 'I AM...SASHA FIERCE',
                'cover_art': 'https://i.scdn.co/image/ab67616d0000b273e13de7b8662b085b0885ffef'
            }
        ]
        return jsonify(dummy_data)

    @app.route("/search_something/<artist_name>/<track_name>", methods=['GET','POST'])
    def get_stuff(artist_name, track_name):
        '''
        Takes artist name and track name as input for Spotify
        API query.Returns info relevant to user and model
        from Spotify's API.The track_id result is used for
        a separate query to pull the audio features for that same
        track from Spotify's API. The results are converted to a
        dataframe and passed into the model which returns
        6 track ids (6 song recommendations) from the premade
        SQL database. Those track ids are then used to make
        a final call to Spotify's API and pull the relevant
        info pertaining to the users recommended songs.
        '''

        # using spotify's API to search
        result = sp.search(q=f'artist:{artist_name} track:{track_name}')

        # indexing the results to get relevant information
        track_id = result['tracks']['items'][0]['id']
        track_name = result['tracks']['items'][0]['name']
        track_popularity = result['tracks']['items'][0]['popularity']
        artist_name = result['tracks']['items'][0]['artists'][0]['name']
        album_name = result['tracks']['items'][0]['album']['name']
        album_id = result['tracks']['items'][0]['album']['id']
        album_cover_link = result['tracks']['items'][0]['album']['images'][0]['url']
        song_sample = result['tracks']['items'][0]['preview_url']

        # Use the track id to get a set of audio features (nested list)
        audio_features = sp.audio_features(track_id)
        audio_features = audio_features[0] #> turns into dictionary

        # Removing audio features we don't need
        keys_to_remove = ["uri", "analysis_url", "type", "track_href", "duration_ms", 'time_signature']
        for key in keys_to_remove:
            del audio_features[key]
        
        # convert audio features to a pandas dataframe
        audio_features_df = pd.DataFrame(audio_features, index=[0])

        # audio_features_json = jsonify(audio_features)

        #
        # TRAIN A MODEL TO RETURN 6 RECOMMENDED SONGS
        #
        conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
        # model_results = "HI"

        inp = audio_features_df
        inp.key = inp.key * 2 + inp['mode']
        track_id = inp['id'][0]
        inp = inp.drop(['mode', 'id'], axis=1)
        
        path_to_model = './knn.pkl'
        
        results = np.flip(joblib.load(path_to_model).kneighbors(inp, return_distance=False)[0]).tolist()
        query = f'''
        SELECT * FROM spotify_table
        WHERE index IN {tuple(results)} AND track_id <> '{track_id}'
        LIMIT 6;
        '''
        output = pd.read_sql_query(query, conn)

        model_result_query = sp.tracks(output['track_id'])

        dict_input = {k:np.nan for k in ['artist', 'track_name', 'track_id', 'album_cover', 'album_name']}
        dict_input['artist'] = artist_name
        dict_input['track_name'] = track_name
        dict_input['track_id'] = track_id
        dict_input['album_cover'] = album_cover_link
        dict_input['album_name'] = album_name

        conn.close()

        # dictionary including artist, track_name, track_id, album_name, and
        #. album artwork for each track returned in model_result_query
        results_dict_list = {}
        results_dict_list['user_input'] = dict_input
        for i in range(6):
            results_dict = {k:np.nan for k in ['artist', 'track_name', 'track_id','album_name', 'album_cover']}
            results_dict['artist'] = model_result_query['tracks'][i]['artists'][0]['name']
            results_dict['track_name'] = model_result_query['tracks'][i]['name']
            results_dict['track_id'] = model_result_query['tracks'][i]['id']
            results_dict['album_cover'] = model_result_query['tracks'][i]['album']['images'][0]['url']
            results_dict['album_name'] = model_result_query['tracks'][i]['album']['name']
            results_dict_list[str(i)] = results_dict
        



        # print(output) 
        # print(results_dict_list)
    
        audio_features_df['popularity'] = track_popularity
        results_to_plot = output[['popularity','danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo', ]]
        results_to_plot = audio_features_df[['popularity','danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness','liveness','valence','tempo', ]].append(results_to_plot)
        results_to_plot = results_to_plot.reset_index(drop=True)

        # figs = go.Figure()

        # figs = make_subplots(rows=4, cols=3, shared_yaxes=True)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['danceability'], name='Danceability'),
        #             row=1, col=1)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['energy'], name='Energy'),
        #             row=1, col=2)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['liveness'], name='Liveness'),
        #             row=1, col=3)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['speechiness'], name='Speechiness'),
        #             row=2, col=1)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['acousticness'], name='Acousticness'),
        #             row=2, col=2)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['instrumentalness'], name='Instrumentalness'),
        #             row=2, col=3)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['loudness'], name='Loudness'),
        #             row=3, col=1)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['popularity'], name='Popularity'),
        #             row=3, col=2)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['tempo'], name='Tempo'),
        #             row=3, col=3)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['key'], name='Key'),
        #             row=4, col=1)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['mode'], name='Mode'),
        #             row=4, col=2)

        # figs.add_trace(go.Scatter(x=results_to_plot.index, y=results_to_plot['valence'], name='Valence'),
        #             row=4, col=3)


        # figs.update_layout(height=800, width=800,
        #                 title_text="Difference of features between recomendations.")

        # figs.update_xaxes(title_text="Songs")

        # py.plot(figs, filename='subplots', sharing='public')

        # plt.savefig(img, format='png')



        return jsonify(results_dict_list)


    return app
