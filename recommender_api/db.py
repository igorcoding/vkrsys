import ConfigParser
from contextlib import closing
from pprint import pprint
import MySQLdb
from MySQLdb.cursors import DictCursor


def safe_db_call(f):
    def wrapper(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        finally:
            self.disconnect()

    return wrapper


class Db:
    def __init__(self, config_filename):
        config = ConfigParser.ConfigParser()
        config.read(config_filename)
        self._conn_info = {
            'host': config.get('db', 'HOST'),
            'port': int(config.get('db', 'PORT')),
            'user': config.get('db', 'USER'),
            'passwd': config.get('db', 'PASSWORD'),
            'db': config.get('db', 'NAME')
        }

        self.db = None

    def connect(self):
        if self.db is None:
            self.db = MySQLdb.connect(**self._conn_info)
        return self.db

    def disconnect(self, db=None):
        if db is None or db == self.db:
            if self.db is not None:
                self.db.close()
        else:
            if db is not None:
                db.close()
        self.db = None

    def get_users_count(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT COUNT(id) FROM auth_user""")
            count = int(c.fetchone()[0])

        with closing(db.cursor()) as c:
            c.execute("""SELECT MAX(id) FROM auth_user""")
            last_id = int(c.fetchone()[0])

        return count, last_id

    def get_songs_count(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT COUNT(id) FROM app_song""")
            count = int(c.fetchone()[0])

        with closing(db.cursor()) as c:
            c.execute("""SELECT MAX(id) FROM app_song""")
            last_id = int(c.fetchone()[0])

        return count, last_id

    def save_lasts(self, user_last, song_last):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT COUNT(id) FROM app_recommenderinfo""")
            count = int(c.fetchone()[0])

        if count == 1:
            with closing(db.cursor()) as c:
                c.execute("""UPDATE app_recommenderinfo SET last_known_user_id=%s, last_known_song_id=%s WHERE id=1""",
                          (user_last, song_last))
        else:
            if count != 0:
                with closing(db.cursor()) as c:
                    c.execute("""TRUNCATE TABLE app_recommenderinfo""")
            with closing(db.cursor()) as c:
                c.execute("""INSERT INTO app_recommenderinfo (id, last_known_user_id, last_known_song_id)
                             VALUES (1, %s, %s)""", (user_last, song_last))
        db.commit()

    def get_users_ids(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM auth_user ORDER BY id""")  # probably don't need ordering by id
            ids = map(lambda entry: entry[0], c.fetchall())
        return ids

    def get_items_ids(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM app_song ORDER BY id""")  # probably don't need ordering by id
            ids = map(lambda entry: entry[0], c.fetchall())
        return ids
