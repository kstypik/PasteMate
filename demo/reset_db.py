"""
    Script copied from: https://github.com/liip/django-template
    License: MIT
"""
from io import StringIO

from django.core import management
from django.db import connection


def reset_db():
    """
    Reset database to a blank state by removing all the tables and recreating them.
    """
    with connection.cursor() as cursor:
        cursor.execute("select tablename from pg_tables where schemaname = 'public'")
        tables = [row[0] for row in cursor.fetchall()]

        # Can't use query parameters here as they'll add single quotes which are not
        # supported by postgres
        for table in tables:
            cursor.execute('drop table "' + table + '" cascade')

    # Call migrate so that post-migrate hooks such as generating a default Site object
    # are run
    management.call_command("migrate", "--noinput", stdout=StringIO())
