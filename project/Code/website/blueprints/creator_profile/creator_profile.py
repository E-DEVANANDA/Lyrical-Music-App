from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import text
from ..models import Creator, Song, Album, User
from .. import db


creator_profile = Blueprint('creator_profile', __name__,template_folder='templates',
    static_folder='static')

@creator_profile.route('/creator_home',methods=['GET','POST'])
@login_required
def home():
    if request.method == 'POST': 
        return redirect(url_for('creator_profile.add_album'))

    creator = Creator.query.filter_by(id=current_user.id).first()
    creator_songs = Song.query.filter_by(creator_id=current_user.id).all()
    album = Album.query.filter_by(creator_id=current_user.id).count()

    # Initialize an empty list to collect ratings
    ratings = []

    for song in creator_songs:
        query = text(f"SELECT rating FROM song_rating WHERE song_id = :song_id")
        result = db.session.execute(query, {'song_id': song.id})
        song_ratings = result.fetchall()
        ratings.extend(song_ratings)

    if len(ratings) == 0:
        avg = 0
    else:
        total = sum(rating[0] for rating in ratings)
        avg = total / len(ratings)

    return render_template("home.html", creator=creator, avg=avg, album=album)


@creator_profile.route('/add_song/<int:album_id>/<int:count>', methods=['GET', 'POST'])
@login_required
def add_song(count, album_id):
    if request.method == 'POST':
        for i in range(count):
            title = request.form.get(f'title_{i}').lower()  # Assuming each form input for songs is named incrementally
            album = Album.query.filter_by(id=album_id).first()
            artist=album.artist
            data = request.form.get(f'lyrics_{i}').lower()
            if len(title) < 1 or len(artist) < 1 or len(data) < 1:
                flash('All fields need to have at least 1 character', category='error')
            else:
                new_song = Song(data=data, title=title, artist=artist, creator_id=current_user.id, album_id=album_id)
                db.session.add(new_song)
        
        db.session.commit()
        flash('Songs added!', category='success')
        return redirect(url_for('creator_profile.home'))  # Assuming 'home' is the route for the creator's home page
        
    return render_template('add_song.html', count=count)

@creator_profile.route('/add_album',methods=['GET','POST'])
@login_required
def add_album():
    album=Album.query.all()
    if request.method == 'POST': 
        name = request.form.get('title').lower()#Gets the note from the HTML 
        artist = request.form.get('singer').lower()
        genre = request.form.get('genre').lower()
        count= int(request.form.get('number_of_songs'))
        if count<1:
            flash('Count need to have at least 1 charecter', category='error')
        elif len(name) < 1:
            flash('Title need to have at least 1 charecter', category='error') 
        elif len(artist) < 1:
            flash('Artist need to have at least 1 charecter', category='error') 
        elif len(genre) < 1:
            flash('Genre need to have at least 1 charecter', category='error') 
        else:
            new_album = Album(genre=genre,name=name,artist=artist, creator_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_album) #adding the note to the database 
            db.session.commit()
            
            return redirect(url_for('creator_profile.add_song',album_id=new_album.id,count=count))
    
    return render_template('add_album.html',album=album)

@creator_profile.route('/album_details/<int:album_id>',methods=['GET','POST'])
@login_required
def album_details(album_id):
    album=Album.query.filter_by(id=album_id).first()
    songs=Song.query.filter_by(album_id=album_id).all()
    return render_template('album_details.html', songs=songs, album=album)

@creator_profile.route('/song_edit/<int:album_id>/<int:song_id>',methods=['GET','POST'])
@login_required
def song_edit(song_id,album_id):
    song=Song.query.filter_by(id=song_id).first()
    if request.method=='POST':
        title = request.form.get('title')
        artist = request.form.get('artist')
        lyrics = request.form.get('lyrics')
        
        # Update the song attributes if needed
        song.title = title
        song.artist = artist
        song.data = lyrics
        
        # Commit the changes to the database
        db.session.commit()
        
        # Redirect to a different page after editing
        return redirect(url_for('creator_profile.album_details',album_id=album_id))

    return render_template('song_edit.html',song=song)

@creator_profile.route('/deletealbum/<album_id>')
@login_required
def deletealbum(album_id):
    album=Album.query.filter_by(id=album_id).first()
    songs=Song.query.filter_by(album_id=album_id).all()
    if album:
        for song in songs:
            db.session.delete(song)
            db.session.commit()
        db.session.delete(album)
        db.session.commit()
    else:
        flash('Song not found', 'danger')
    
    return redirect(url_for('creator_profile.home'))

@creator_profile.route('/dltsong/<song_id>',methods=['GET','POST'])
@login_required
def dltsong(song_id):
    song=Song.query.filter_by(id=song_id).first()
    if song:
        db.session.delete(song)
        db.session.commit()
        flash('Song deleted successfully', 'success')
    else:
        flash('Song not found', 'danger')
    
    return redirect(url_for('creator_profile.home'))