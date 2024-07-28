from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user
from sqlalchemy import text
from .. import db
from ..models import User, Song, Album, song_rating

admin_profile = Blueprint('admin_profile', __name__,template_folder='templates',
    static_folder='static')

@admin_profile.route('/admin_home',methods=['GET','POST'])
@login_required
def admin_home():
    songs = Song.query.all()
    users = User.query.all()
    albums = Album.query.all()
    creators = User.query.filter_by(role='creator').all()
    genres = db.session.query(Album.genre).distinct().all()
    unique_genres = [genre[0] for genre in genres]
    
    rated_song, avg = top_song(songs)
    rated_album = top_album(albums)
    rated_artist=top_artist()
    
    count = [len(songs), len(users), len(creators), len(albums), len(unique_genres)]
    
    return render_template('admin_home.html', count=count, rated_song=rated_song, rated_album=rated_album,rated_artist=rated_artist)

def top_song(songs):
    max_avg = 0
    top_song = None

    for song in songs:
        query = text("SELECT rating FROM song_rating WHERE song_id = :song_id")
        result = db.session.execute(query, {'song_id': song.id})
        ratings = result.fetchall()

        if not ratings:
            continue

        total = sum(rating[0] for rating in ratings)
        avg = total / len(ratings)

        if avg > max_avg:
            max_avg = avg
            top_song = song

    return top_song, max_avg

def top_album(albums):
    max_avg = 0
    top_album = None

    for album in albums:
        album_tot = 0
        songs = Song.query.filter_by(album_id=album.id).all()

        for song in songs:
            query = text("SELECT rating FROM song_rating WHERE song_id = :song_id")
            result = db.session.execute(query, {'song_id': song.id})
            ratings = result.fetchall()

            if not ratings:
                continue

            total = sum(rating[0] for rating in ratings)
            avg = total / len(ratings)
            album_tot += avg
        if songs:
            avg_rating = album_tot / len(songs)

            if avg_rating > max_avg:
                max_avg = avg_rating
                top_album = album

    return top_album

def top_artist():
    albums=Album.query.all()
    albums_by_artist = {}

    # Populate the dictionary
    for album in albums:
        artist = album.artist
        if artist not in albums_by_artist:
            albums_by_artist[artist] = get_songs(album.id)
        else:
            albums_by_artist[artist].extend(get_songs(album.id))
    print(albums_by_artist)
    max_avg = 0
    top_artist = None

    for artist, songs in albums_by_artist.items():
        song_name,artist_avg = top_song(songs)

        if artist_avg > max_avg:
            max_avg = artist_avg
            top_artist = artist
            top_song_name = song_name

    return top_artist
@admin_profile.route('/tracks',methods=['GET','POST'])
@login_required
def tracks():
    albums=Album.query.all()
    albums_by_genre = {}

    # Populate the dictionary
    for album in albums:
        genre = album.genre
        if genre not in albums_by_genre:
            albums_by_genre[genre] = get_songs(album.id)
        else:
            albums_by_genre[genre].extend(get_songs(album.id))
    print(albums_by_genre)
    return render_template('tracks.html',albums_by_genre=albums_by_genre)

def get_songs(album_id):
    L=[]
    songs=Song.query.filter_by(album_id=album_id)
    for song in songs:
        L.append(song)
    return L

@admin_profile.route('/allsongs',methods=['GET','POST'])
@login_required
def allsongs():
    songs=Song.query.all()
    return render_template('admin_songs.html',songs=songs)

@admin_profile.route('/deletesong/<song_id>',methods=['GET','POST'])
@login_required
def deletesong(song_id):
    song=Song.query.filter_by(id=song_id).first()
    if song:
        db.session.delete(song)
        db.session.commit()
        flash('Song deleted successfully', 'success')
    else:
        flash('Song not found', 'danger')
    
    return redirect(url_for('admin_profile.allsongs'))


@admin_profile.route('/lyrics/<song_id>',methods=['GET','POST'])
@login_required
def lyrics(song_id):
    song=Song.query.filter_by(id=song_id).first()
    print(song)
    if song:
        return render_template('admin_lyrics.html',song=song)
    else:
        flash('Song not found', 'danger')

@admin_profile.route('/artistsongs/<artist>',methods=['GET','POST'])
@login_required
def artistsongs(artist):
    songs = Song.query.filter_by(artist=artist).all()
    return render_template('admin_songs.html', songs=songs)

@admin_profile.route('/admin_search',methods=['GET','POST'])
@login_required
def search():
    if request.method == 'POST':
        search = request.form.get('search')
        search_songs = Song.query.filter(Song.title.ilike(f'%{search}%')).all()
        search_artists = Album.query.filter(Album.artist.ilike(f'%{search}%')).all()
        search_genres = Album.query.filter(Album.genre.ilike(f'%{search}%')).all()
        
        unique_ratings_and_songs = db.session.query(song_rating.c.rating, Song).join(Song).distinct().all()
        ratings_dict = {}
        
        for rating, songs in unique_ratings_and_songs:
            if rating in ratings_dict:
                ratings_dict[rating].append(songs)
            else:
                ratings_dict[rating] = [songs]
        rating_list=[]
        search_key = None
        for key in ratings_dict:
            if str(key) == search:
                search_key = key
                break 

        if search_key is not None:
            # If there's a match, set rating_list to the corresponding value
            rating_list = ratings_dict[search_key]

        if not search_songs and not search_artists and not search_genres and not ratings_dict:
            return render_template('no_result.html')
        
        return render_template('admin_search.html', search_songs=search_songs, search_artists=search_artists, search_genres=search_genres, rating_list=rating_list)
    
