# PasteMate

Pastebin web app allowing users to post plain text with optional syntax highlighting for many programming languages and other features.

[SEE DEMO](https://pastemate.toadres.pl)

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

Set required environment variables for development (for production there is more, see production settings module).
You can create .env file for them:
```
DATABASE_URL=psql://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DBNAME>
DJANGO_SECRET_KEY=some random key
DJANGO_DEBUG=True
```

As of now, pinax_messages package needs some workarounds for compatibility with newer Django versions.

Open <PATH_TO_YOUR_PYTHON_VIRTUAL_ENVIRONMENT>/pinax/messages/signals.py

Change
```python
message_sent = Signal(providing_args=["message", "thread", "reply"])
```
to
```python
message_sent = Signal()
```
Open <PATH_TO_YOUR_PYTHON_VIRTUAL_ENVIRONMENT>/pinax/messages/urls.py
Change
```python
from django.conf.urls import url

from . import views

app_name = "pinax_messages"

urlpatterns = [
    url(r"^inbox/$", views.InboxView.as_view(),
        name="inbox"),
    url(r"^create/$", views.MessageCreateView.as_view(),
        name="message_create"),
    url(r"^create/(?P<user_id>\d+)/$", views.MessageCreateView.as_view(),
        name="message_user_create"),
    url(r"^thread/(?P<pk>\d+)/$", views.ThreadView.as_view(),
        name="thread_detail"),
    url(r"^thread/(?P<pk>\d+)/delete/$", views.ThreadDeleteView.as_view(),
        name="thread_delete"),
]
```
to
```python
from django.urls import path

from . import views

app_name = "pinax_messages"

urlpatterns = [
    path("inbox/", views.InboxView.as_view(),
        name="inbox"),
    path("create/", views.MessageCreateView.as_view(),
        name="message_create"),
    path("create/<int:user_id>/", views.MessageCreateView.as_view(),
        name="message_user_create"),
    path("thread/<int:pk>/", views.ThreadView.as_view(),
        name="thread_detail"),
    path("thread/<int:pk>/delete/", views.ThreadDeleteView.as_view(),
        name="thread_delete"),
]
```

Apply migrations:
```
poetry run python manage.py makemigrations && poetry run python manage.py migrate
```

Optionally, you can fill the database with examplary data:
```
poetry run python manage.py reset_test_user && poetry run python manage.py generate_demo_pastes
```

Now you can start the development server:
```
poetry run python manage.py runserver
```

**Note:** To support paste expiration feature, you have to add expire_pastes Django management command to your cron tasks or another scheduler.

Happy coding!

## Testing

To run tests, type:
```
pytest
```
