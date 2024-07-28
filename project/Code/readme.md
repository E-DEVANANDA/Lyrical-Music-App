# Lyrion
The LYRION is a web application built with Flask, allowing users to explore and interact with song lyrics, artists, and albums. It provides features such as user authentication, playlist creation, and the ability to rate and contribute to the music database.


## Features

- Search for songs, artists, and albums.
- Search for songs that have special lyrics
- Enjoy top-rated and recent releases.
- Create and manage playlists.
- Rate song lyrics based on user enjoyment.
- User authentication with role-based access (User, Creator, Admin).
- Users can contribute as creators, uploading albums and songs.
- Admin functionalities to manage content and enforce policies.

## Installation


1. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate     # On Windows
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables (if applicable).

4. Run the application:

    ```bash
    python main.py
    ```

5. Access the app at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## Usage

- Create user account by filling the required columns
- Visit the user home page to explore the song lyrics, artists, and albums.
- Log in to access personalized features such as playlists and ratings.
- Try  becoming creator and add albums and songs
- Creators can upload albums and songs through their dashboard.
- After creating one user only you can access the admin page
- Admins have comprehensive control over the content and user contributions.
- Admin account can be access by username: admin and password: adminpassword

## Project Structure

- `main.py`: Main entry point for the Flask application.
- `website/`: Contains the main application logic and structure.
    - `blueprints/`: Blueprints for different sections (admin, user, authentication, creator).
    - `templates/`: HTML templates.
    - `models.py`: Database models.

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Login
- Werkzeug
- SQLAlchemy
