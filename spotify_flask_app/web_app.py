from flask import Flask, jsonify
import os
# from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
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

#     db_user = User.query.get(twitter_user.id) or User(id=twitter_user.id)
#     db_user.screen_name = twitter_user.screen_name
#     db_user.name = twitter_user.name
#     db_user.location = twitter_user.location
#     db_user.followers_count = twitter_user.followers_count
#     db.session.add(db_user)
#     db.session.commit()
#     #return "OK"
#     #breakpoint()

if __name__ == "__main__":
    app.run(debug=True)
