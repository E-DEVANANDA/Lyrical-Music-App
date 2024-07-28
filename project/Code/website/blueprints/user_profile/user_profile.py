from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user
from .. import db
from sqlalchemy import insert, text

from website.blueprints.models import Song,Creator,Playlist,User,playlist_song, Album, song_rating
# from . import auth

user_profile = Blueprint('user_profile', __name__,template_folder='templates',
    static_folder='static')

@user_profile.route('/user_profile',methods=['GET','POST'])
@login_required
def home():
    songs = Song.query.all()
    song_order=[]
    for song in songs:
        song_rate=rating_score(song.id)
        song_order.append((song_rate, song))
    song_order.sort(key=lambda x: x[0], reverse=True)
    ordered_songs = [song for _, song in song_order]
    playlists=Playlist.query.all()
    genres=db.session.query(Album.genre).distinct().all()
    unique_genres = [genre[0] for genre in genres]
    return render_template('profile.html',songs=songs, playlists=playlists,genres=unique_genres, ordered_songs=ordered_songs)

@user_profile.route('/playlist',methods=['GET','POST'])
@login_required
def playlist():
    user = User.query.filter_by(id=current_user.id).first()
    playlists=user.playlists
    return render_template('playlist.html', playlists=playlists)

@user_profile.route('/add_playlist', methods=['GET', 'POST'])
@login_required
def add_playlist():
    songs = Song.query.all()

    if request.method == 'POST':
        name = request.form.get('title')
        selected_song_ids = request.form.getlist('selected_songs')

        if len(name) < 1:
            flash('Name should have at least 1 character', category='error')
        elif not selected_song_ids:
            flash('At least 1 song should be selected', category='error')
        else:
            # Create a new playlist
            playlist = Playlist(name=name, user_id=current_user.id)
            db.session.add(playlist)
            db.session.commit()
            print(selected_song_ids)
            # Add selected songs to the playlist
            for song_id in selected_song_ids:
                song = Song.query.get(song_id)
                if song:
                    playlist.songs.append(song)
            
            db.session.commit()
            flash('Playlist created successfully!', category='success')
            return redirect(url_for('user_profile.playlist'))

    return render_template('add_playlist.html', songs=songs)

@user_profile.route('/playlist_details/<int:playlist_id>')
@login_required
def playlist_details(playlist_id):
    playlist=Playlist.query.get(playlist_id)
    songs = playlist.songs
    return render_template('playlist_details.html',songs=songs,playlist=playlist)


@user_profile.route('/upgrade_to_creator', methods=['GET'])
@login_required
def upgrade_to_creator():
    user = current_user  # Get the current user

    if user.role == 'user':
        # Change the user's role to 'creator'
        user.role = 'creator'
        new_creator = Creator(user_id=current_user.id)
        db.session.add(new_creator)
        db.session.commit()
        flash('You are now a creator!', category='success')
    else:
        flash('You are already a creator.', category='info')

    # After the role is updated, set the current user as the creator
    login_user(user)
    return redirect(url_for('creator_profile.home'))

@user_profile.route('/song/<int:song_id>', methods=['GET', 'POST'])
@login_required
def song_details(song_id):
    song = Song.query.get(song_id)
    if request.method == 'POST' and 'rating' in request.form:
        user_rating = request.form['rating']
        select_sql = text(f"SELECT * FROM song_rating WHERE user_id = {current_user.id} AND song_id = {song_id};")
        result = db.session.execute(select_sql)
        existing_rating = result.fetchone()
        if existing_rating:
            # Update the existing rating
            update_sql = text(f"UPDATE song_rating SET rating = {user_rating} WHERE user_id = {current_user.id} AND song_id = {song_id};")
            db.session.execute(update_sql)
            db.session.commit()
        else:
            # Insert a new rating
            insert_sql = text(f"INSERT INTO song_rating (user_id, song_id, rating) VALUES ({current_user.id}, {song_id}, {user_rating});")
            db.session.execute(insert_sql)
            db.session.commit()
        db.session.commit()
    rate_score = rating_score(song_id)
    if song:
        return render_template('song_details.html', song=song, rate_score=rate_score)
    else:
        return "Song not found", 404

def rating_score(song_id):
    query = text(f"SELECT rating FROM song_rating WHERE song_id = :song_id")
    result = db.session.execute(query, {'song_id': song_id})
    ratings = result.fetchall()

    if not ratings:
        return 0  # or "No ratings for this song yet."

    total = sum(rating[0] for rating in ratings)
    avg = total / len(ratings)
    return avg


@user_profile.route('/songs', methods=['GET'])
@login_required
def songs():
    songs = Song.query.all()
    return render_template('songs.html', songs=songs)

@user_profile.route('/genres', methods=['GET'])
@login_required
def genres():
    genres=db.session.query(Album.genre).distinct().all()
    unique_genres = [genre[0] for genre in genres]
    return render_template('genres.html', genres=unique_genres)

@user_profile.route('/artists/<artist>', methods=['GET'])
@login_required
def artists(artist):
    songs = Song.query.filter_by(artist=artist).all()
    return render_template('songs.html', songs=songs)

@user_profile.route('/album/<album_id>', methods=['GET'])
@login_required
def albums(album_id):
    songs = Song.query.filter_by(album_id=album_id).all()
    return render_template('songs.html', songs=songs)

@user_profile.route('/genre_details/<genre>', methods=['GET'])
@login_required
def genre_details(genre):
    albums=Album.query.filter_by(genre=genre).all()
    songs = db.session.query(Song).join(Album).filter(Album.genre == genre).all()
    return render_template('songs.html', songs=songs)

@user_profile.route('/search',methods=['GET','POST'])
@login_required
def search():
    if request.method=='POST':
        search=request.form.get('search')
        search_songs = Song.query.filter(Song.title.ilike(f'%{search}%')).all()
        search_lyrics = Song.query.filter(Song.data.ilike(f'%{search}%')).all()
        search_artists = Album.query.filter(Album.artist.ilike(f'%{search}%')).all()
        search_genres= Album.query.filter(Album.genre.ilike(f'%{search}%')).all()
        if not search_songs and not search_artists and not search_genres and not search_lyrics:
            return render_template('404.html')

        return render_template('search.html',search_songs=search_songs,search_artists=search_artists,search_genres=search_genres, search_lyrics=search_lyrics)

@user_profile.route('/deleteplaylist/<playlist_id>',methods=['GET','POST'])
@login_required
def deleteplaylist(playlist_id):
    # Retrieve the playlist and its associated songs
    playlist = Playlist.query.get(playlist_id)

    if playlist:
        playlist.songs.clear()
        db.session.delete(playlist)
        db.session.commit()
        flash('Playlist removed successfully', 'success')
    else:
        flash('Playlist not found', 'danger')

    return redirect(url_for('user_profile.playlist')) # Redirect to the page where playlists are listed

@user_profile.route('/delete_plalylist_song/<int:song_id>/<int:playlist_id>',methods=['GET','POST'])
def delete_playlist_song(song_id,playlist_id):
    playlist=Playlist.query.get(playlist_id)
    song= Song.query.filter_by(id=song_id).first()
    playlist.songs.remove(song)
    db.session.commit()
    songs=playlist.songs
    return render_template('playlist_details.html',songs=songs,playlist=playlist)
