#!/usr/bin/env python3
#
# Create a new superuser with expected password
import os

from django.contrib.auth import get_user_model

UserModel = get_user_model()

name = os.getenv("DJANGO_ADMIN_USERNAME", "admin")
password = os.getenv("DJANGO_ADMIN_PASSWORD", "admin")

# trying to get username
try:
    su = UserModel.objects.get(username=name)
    su.set_password(password)
except Exception:
    su = UserModel.objects.create_user(name, password=password)

su.is_staff = True
su.is_superuser = True
su.save()
