import sqlite3
import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

with connection.cursor() as cursor:
    try:
        cursor.execute("DROP TABLE IF EXISTS interviews_interview CASCADE;")
        print("Table interviews_interview dropped.")
    except Exception as e:
        print(f"Error dropping table: {e}")
