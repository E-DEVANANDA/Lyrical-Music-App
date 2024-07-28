from sqlalchemy import func
from . import db
from flask_login import UserMixin

# Define the association table for the many-to-many relationship
# class SongRating(db.Model):
#     __tablename__ = 'song_rating'
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#     song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)
#     rating = db.Column(db.Integer)

song_rating = db.Table(
    'song_rating',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True),
    db.Column('rating', db.Integer)
)

    # user = db.relationship('User', back_populates='song_ratings')
    # song = db.relationship('Song', back_populates='users_rated')

# Admin Model
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150))

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    role = db.Column(db.String(20), default='user')
    playlists = db.relationship('Playlist', backref='user')  # User-Playlist relationship
    song_ratings = db.relationship('Song', secondary=song_rating, back_populates='users_rated')


# Creator Model
class Creator(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    songs = db.relationship('Song', backref='creator')
    albums = db.relationship('Album', backref='creator')

# Playlist Model
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.relationship('Song', secondary='playlist_song', back_populates='playlists')

# Song Model
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
    data = db.Column(db.Text)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    artist = db.Column(db.String(25))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=True)

    playlists = db.relationship('Playlist', secondary='playlist_song', back_populates='songs')
    users_rated = db.relationship('User', secondary='song_rating', back_populates='song_ratings')

# Album Model
class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
    genre = db.Column(db.String(50))
    artist = db.Column(db.String(25))

# Define the association table for the many-to-many relationship
playlist_song = db.Table('playlist_song',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

