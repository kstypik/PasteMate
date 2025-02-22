# PasteMate

Pastebin web app allowing users to post plain text with optional syntax highlighting for many programming languages and with a bunch of other features.

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
- "Burn After Read" – auto removal of pastes after someone reads them
- Password protection of pastes
- Time-limited pastes (e.g. remove after 10 minutes)
- User Paste List
- Organization of pastes into folders
- Searching of user's pastes
- Pastes Archive
- Displaying pastes only for specific language
- Profile & Avatar for users
- User adjustable preferences on default syntax, expiration time and exposure of pastes
- Counting views of pastes and user profiles
- Cloning of existing pastes
- Downloading of pastes
- Embedding pastes with an auto-generated image of provided text
- Backing up of all pastes

## Screenshots

See [SCREENSHOTS.md](SCREENSHOTS.md) for more
![pastemate_paste_detail_smaller](https://user-images.githubusercontent.com/53559764/178123659-df31ca8d-db45-42b8-80d8-dff6bcbaac9a.png)

## Getting Started

Clone the code:

```
git clone https://github.com/kstypik/PasteMate.git .
```

Install the dependencies (PasteMate uses [poetry](https://python-poetry.org) as a package manager):

```
poetry install
```

Set required environment variable for development (for production there is more, see production settings module).
You can create .env file in the project's base directory with your environment variables (don't forget to replace placeholder data with your own Postgres credentials:

```
DATABASE_URL=psql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DBNAME>
```

Apply migrations:

```
poetry run python manage.py makemigrations && poetry run python manage.py migrate
```

Install the Node dependencies:

```
npm install
```

Build the [CodeMirror](codemirror.net/) editor:

```
npm start
```

Optionally, you can fill the database with examplary data:

```
poetry run python manage.py reset_test_user && poetry run python manage.py generate_demo_pastes
```

Now you can start the development server:

```
poetry run python manage.py runserver
```

**Note:** To support paste expiration feature, you have to add expire_pastes Django management command to your cron tasks or to another scheduler.

Happy coding!

## Testing

To run tests, type:

```
pytest
```
