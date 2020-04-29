<<<<<<< Updated upstream
from flask import Flask, jsonify
import os
# from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
=======
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, jsonify, render_template, request, current_app as app
from sklearn.preprocessing import LabelEncoder, scale
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
import json

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID,
                                                     client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

>>>>>>> Stashed changes
# from flask_migrate import Migrate
import psycopg2
# from psycopg2.extras import execute_values
db = SQLAlchemy()
# migrate = Migrate()


SPOTIFY_DB_NAME = "phmcuozt"
SPOTIFY_DB_PW = "Gq5822Z4v3ypBvLtnCsF4XjabVM3LKr9"
SPOTIFY_DB_HOST = "drona.db.elephantsql.com"
SPOTIFY_DB_USER = "phmcuozt"

conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
cur = conn.cursor()

# pip install Flask-Migrate
# pip install Flask-SQLAlchemy

# insertion_query = "INSERT INTO test_table (name, data) VALUES %s"
# execute_values(cursor, insertion_query, rows_to_insert)
# ​
# ​


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
    LIMIT 10
    '''
    cur.execute(query_1)
    results = cur.fetchall()
    return jsonify(results)

# @app.route("/data")


# def store_twitter_user_data(screen_name):
#     api = api_client()
#     twitter_user = api.get_user(screen_name)
#     #statuses = api.user_timeline(screen_name, tweet_mode="extended", count=150, exclude_replies=True, include_rts=False)
#     statuses = api.user_timeline(screen_name, tweet_mode="extended", count=150)
#     #return jsonify({"user": user._json, "tweets": [s._json for s in statuses]})

<<<<<<< Updated upstream
#     db_user = User.query.get(twitter_user.id) or User(id=twitter_user.id)
#     db_user.screen_name = twitter_user.screen_name
#     db_user.name = twitter_user.name
#     db_user.location = twitter_user.location
#     db_user.followers_count = twitter_user.followers_count
#     db.session.add(db_user)
#     db.session.commit()
#     #return "OK"
#     #breakpoint()
=======
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
        artist_name = result['tracks']['items'][0]['artists'][0]['name']
        album_name = result['tracks']['items'][0]['album']['name']
        album_id = result['tracks']['items'][0]['album']['id']
        album_cover_link = result['tracks']['items'][0]['album']['images'][0]['url']
        song_sample = result['tracks']['items'][0]['preview_url']
        audio_features = sp.audio_features(track_id)
        audio_features = audio_features[0]
        keys_to_remove = ["uri", "analysis_url", "id", "type", "track_href"]
        for key in keys_to_remove:
          del audio_features[key]
        audio_features = jsonify(audio_features)
        return render_template("button.html", result=result, track_id=track_id, track_name=track_name, artist_name=artist_name, album_name=album_name, album_id=album_id, album_cover_link=album_cover_link, song_sample=song_sample, audio_features=audio_features)  

    @app.route('/run_model/<searched_id>', methods=['GET','POST'])
    def song_recomendation(searched_id):

        # client_credentials_manager = SpotifyClientCredentials(client_id='64c7e99146a749da88cbad6d9b55183c', client_secret='48bb5ebd778f4223a2b0cdd3e9a3a66d')
        # sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

                   
        # conn = psycopg2.connect("dbname='phmcuozt' user='phmcuozt' host='drona.db.elephantsql.com' password='Hl4xzpVOZxiQ9af4kH5bavoEHIx7z3hn'")
        conn = psycopg2.connect(dbname=SPOTIFY_DB_NAME, user=SPOTIFY_DB_USER,
                        password=SPOTIFY_DB_PW, host=SPOTIFY_DB_HOST)
        songs = pd.read_sql_query('SELECT * FROM spotify_table', conn)
        conn.close()


        numerical_features = ['acousticness','danceability',
                              'energy','instrumentalness','key', 'liveness',
                              'loudness','mode','speechiness', 'tempo',
                              'time_signature','valence','popularity']

        scaled_data = scale(songs[numerical_features])

        songs[numerical_features] = scaled_data


        features = ['acousticness','danceability',
                    'energy','instrumentalness','key', 'liveness',
                    'loudness','mode','speechiness', 'tempo',
                    'time_signature','valence','popularity']
        songs_features = songs[features].astype(float)

        #  Product of the vectors.

        knn = Sequential()
        knn.add(Dense(input_shape=(songs_features.shape[1],),
            units=songs.shape[0],
            activation='linear',
            use_bias=False)) 

        def normalize(vectors):

            norm_vectors = np.linalg.norm(vectors, axis=1, keepdims=True)
            return (vectors / norm_vectors)
        
        norm_songs_features = normalize(songs_features)


        # change the weights to the original matrix of features (of songs).
        knn.set_weights([np.array(norm_songs_features.T)])                    

        # random_choice = np.random.randint(1,songs.shape[0]+1)

        # songs[songs['track_id']==song_id].index[0]

        sample_song = songs.loc[songs[songs['track_id'] == searched_id ].index[0]]

        prediction = knn.predict(songs_features.loc[songs[songs['track_id']== searched_id ].index[0]].values.reshape(1,songs_features.shape[1]))

        ten_most_similar_songs = songs.loc[prediction.argsort()[0][-10:]]
        
        # 30 sec of song

        seconds_of_song_urls = []

        for i in range(10):
            seconds_of_song_urls.append(sp.tracks(ten_most_similar_songs['track_id'])['tracks'][i]['preview_url'])

        ten_most_similar_songs['sample_sound_url'] = seconds_of_song_urls

        artists_photos_urls = []

        for i in range(10):
            artists_photos_urls.append(sp.artist(sp.tracks(ten_most_similar_songs['track_id'])['tracks'][i]['artists'][0]['id'])['images'][0]['url'])

        ten_most_similar_songs['artists_photos_urls'] = artists_photos_urls

        result = json.dumps(ten_most_similar_songs.to_dict() )

        return result
>>>>>>> Stashed changes

if __name__ == "__main__":
    app.run(debug=True)
