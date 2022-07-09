# PasteMate

Pastebin web app allowing users to post plain text with optional syntax highlighting for many programming languages and other features.

## Technologies
- Python 3.10
- Django 4.0
- PostgreSQL 12.0
- Bootstrap 5 + MDBootstrap
- Node.js 18.2.0

## Features
- Syntax highlighting for over 500 languages
- Online editor with highlighting, autocomplete, search/replace and much more
- Limiting access to pastes (public/private/unlisted on the website)
- "Burn After Read" – auto removal of paste after someone reads it
- Password protection of pastes
- Time-limited pastes (e.g. remove after 10 minutes)
- User Paste List
- Organization of pastes in folders
- Searching of user's pastes
- Pastes Archive
- Displaying pastes only for specific language
- Private messaging between users
- Profile & Avatar for users
- User adjustable preferences on default syntax, expiration time and exposure of pastes
- Counting views of pastes and user profiles
- Cloning of existing pastes
- Downloading of pastes
- Embedding pastes with an auto-generated image of provided text
- Backing up of all pastes

## Screenshots
For more screenshots, see [SCREENSHOTS.md](SCREENSHOTS.md)
![screenshot_view_paste](https://user-images.githubusercontent.com/53559764/177049349-1dbc4309-d25e-4d46-902e-c129ff860a3f.png)

## Getting Started

Clone the code:
```
git clone https://github.com/kstypik/PasteMate.git
```

Install the dependencies (PasteMate uses [poetry](https://python-poetry.org) as a package manager):
```
poetry install
```

Set required environment variables for development (for production there is more, see production settings module).
You can create .env file for them:
```
DATABASE_URL=psql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DBNAME>
DJANGO_SECRET_KEY=some random key
DJANGO_DEBUG=True
```

Apply migrations:
```
poetry run python manage.py makemigrations && poetry run python manage.py migrate
```

Optionally, you can fill the database with examplary data:
```
poetry run python manage.py reset_test_user && poetry run pyhton manage.py generate_demo_pastes
```

Happy coding!

## Testing

To run tests, type:
```
pytest
```
