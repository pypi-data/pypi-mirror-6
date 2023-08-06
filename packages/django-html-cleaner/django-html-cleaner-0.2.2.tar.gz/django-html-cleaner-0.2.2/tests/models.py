from django_html_cleaner.models import SanitizedCharField, SanitizedTextField
from django.db import models


class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    title = SanitizedCharField(max_length=200)
    body = SanitizedTextField()
