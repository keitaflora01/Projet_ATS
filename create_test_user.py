import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ats.users.models import User
from django.db import IntegrityError

email = "fotsoeddysteve@gmail.com"
password = "password123"

try:
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(email=email, password=password, role="candidate", full_name="Eddy Fotso")
        print(f"User {email} created.")
    else:
        print(f"User {email} already exists.")
except Exception as e:
    print(f"Error creating user: {e}")
