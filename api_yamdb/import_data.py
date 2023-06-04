import sqlite3
import pandas as pd

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
users = pd.read_csv('static/data/users.csv')
users.to_sql('users', conn, if_exists='append', index = False, chunksize = 10000)

titles = pd.read_csv('static/data/titles.csv')
titles.to_sql('titles', conn, if_exists='append', index = False, chunksize = 10000)

review = pd.read_csv('static/data/review.csv')
review.to_sql('review', conn, if_exists='append', index = False, chunksize = 10000)

genre = pd.read_csv('static/data/genre.csv')
genre.to_sql('genre', conn, if_exists='append', index = False, chunksize = 10000)

genre_title = pd.read_csv('static/data/genre_title.csv')
genre_title.to_sql('genre_title', conn, if_exists='append', index = False, chunksize = 10000)

comments = pd.read_csv('static/data/comments.csv')
comments.to_sql('comments', conn, if_exists='append', index = False, chunksize = 10000)

category = pd.read_csv('static/data/category.csv')
category.to_sql('category', conn, if_exists='append', index = False, chunksize = 10000)