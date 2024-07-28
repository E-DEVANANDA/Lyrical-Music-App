from os import path
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
DB_NAME="music_app.db"

def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']='QWERTYUIOP'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .auth import auth
    from .creator_profile import creator_profile
    from .user_profile import user_profile
    from .admin_profile import admin_profile

    app.register_blueprint(auth.auth, url_prefix='/')
    app.register_blueprint(creator_profile.creator_profile, url_prefix='/')
    app.register_blueprint(user_profile.user_profile, url_prefix='/')
    app.register_blueprint(admin_profile.admin_profile, url_prefix='/')

    from .models import User,Song
    create_database(app)

    login_manager = LoginManager()  
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')