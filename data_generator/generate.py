from __future__ import absolute_import
import os

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vkrsys.settings')

import django
django.setup()

import MySQLdb
from django.contrib.auth.models import User
from app.models import Song, Rating
from random_words import RandomNicknames
import random
from pprint import pprint


GENRES = {
    1: 'Rock',
    2: 'Pop',
    3: 'Rap & Hip-Hop',
    4: 'Easy Listening',
    5: 'Dance & House',
    6: 'Instrumental',
    7: 'Metal',
    21: 'Alternative',
    8: 'Dubstep',
    9: 'Jazz & Blues',
    10: 'Drum & Bass',
    11:	'Trance',
    12:	'Chanson',
    13:	'Ethnic',
    14:	'Acoustic & Vocal',
    15:	'Reggae',
    16:	'Classical',
    17:	'Indie Pop',
    19:	'Speech',
    22:	'Electropop & Disco',
    18:	'Other'
}

GENRES_IDS = GENRES.keys()


class DummyUser:
    TAKEN_USERNAMES = []
    RND_NICK = RandomNicknames()

    def __init__(self, username, genre_tastes):
        self.id = None
        self.username = username
        self.genres = genre_tastes

    @staticmethod
    def _gen_rnd_number(minimum=None, maximum=None):
        if minimum is None:
            minimum = 0
        if maximum is None:
            maximum = 100000
        return random.randint(minimum, maximum)

    @staticmethod
    def _gen_rnd_username():
        self = DummyUser
        username = self.RND_NICK.random_nick(gender='u')
        while username in self.TAKEN_USERNAMES:
            username = self.RND_NICK.random_nick(gender='u') + str(self._gen_rnd_number(0, 1000))
        self.TAKEN_USERNAMES.append(username)
        return username

    @staticmethod
    def _gen_genres():
        PP = {
            3: [0.6, 0.3, 0.1],
            4: [0.5, 0.3, 0.1, 0.1],
            5: [0.6, 0.2, 0.1, 0.06, 0.04]
        }
        genres_arr = []
        genres_count = random.randint(3, 5)
        for _ in xrange(genres_count):
            genres_arr.append(random.choice(GENRES_IDS))
        genres = {}

        for i, g in enumerate(genres_arr):
            genres[g] = PP[genres_count][i]

        return genres

    @staticmethod
    def generate():
        self = DummyUser
        username = self._gen_rnd_username()
        genres = self._gen_genres()
        user = DummyUser(username, genres)
        return user

    def save(self):
        user = User()
        user.username = self.username
        user.save()
        u = User.objects.latest('id')
        self.id = u.id
        return u

    def __str__(self):
        return "[DummyUser] id=%d; username='%s'; " % (self.id, self.username)


def main():
    users = []
    m = 100
    for i in xrange(m):
        print "%d / %d " % (i+1, m)
        u = DummyUser.generate()
        auth_u = u.save()
        users.append(u)
        print u

        songs = Song.objects.filter(genre__in=u.genres.keys())

        for s in songs:
            s_genre_id = s.genre

            z = random.random()  # will we even touch this song
            if z < u.genres[s_genre_id]:
                z2 = random.random()  # like or dislike
                r = Rating()
                r.user = auth_u
                r.song = s
                if z2 < 0.66:
                    r.rating = 1
                else:
                    r.rating = 0
                r.save()





if __name__ == "__main__":
    main()