from django.db import models


class Song(models.Model):
    s_id = models.IntegerField(unique=True, db_index=True)
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    duration = models.SmallIntegerField()
    genre = models.SmallIntegerField(null=True)
    url = models.CharField(max_length=255)