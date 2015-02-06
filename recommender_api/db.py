import ConfigParser
from contextlib import closing
import json
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

    def get_last_action(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM app_useraction ORDER BY date DESC""")
            a = c.fetchone()
            if a is not None:
                return int(a[0])
            else:
                return -1

    def save_lasts(self, user_last=None, song_last=None, last_action=None):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT COUNT(id) FROM app_recommenderinfo""")
            count = int(c.fetchone()[0])

        update_query = None
        insert_query = None
        params = None
        if user_last is None:
            if song_last is None and last_action is None:
                params = None
            elif song_last is None and last_action is not None:
                update_query = """UPDATE app_recommenderinfo SET last_known_user_event_id=%s WHERE id=1"""
                params = (last_action,)
            elif song_last is not None and last_action is None:
                update_query = """UPDATE app_recommenderinfo SET last_known_song_id=%s  WHERE id=1"""
                params = (song_last,)
            elif song_last is not None and last_action is not None:
                update_query = """UPDATE app_recommenderinfo SET last_known_song_id=%s, last_known_user_event_id=%s  WHERE id=1"""
                params = (song_last, last_action)
        else:
            if song_last is None and last_action is None:
                update_query = """UPDATE app_recommenderinfo SET last_known_user_id=%s WHERE id=1"""
                params = (user_last,)
            elif song_last is None and last_action is not None:
                update_query = """UPDATE app_recommenderinfo SET last_known_user_id=%s, last_known_user_event_id=%s WHERE id=1"""
                params = (user_last, last_action)
            elif song_last is not None and last_action is None:
                update_query = """UPDATE app_recommenderinfo SET last_known_user_id=%s, last_known_song_id=%s  WHERE id=1"""
                params = (user_last, song_last)
            elif song_last is not None and last_action is not None:
                update_query = """UPDATE app_recommenderinfo SET last_known_user_id=%s, last_known_song_id=%s, last_known_user_event_id=%s  WHERE id=1"""
                insert_query = [
                    """SET foreign_key_checks = 0""",
                    """INSERT INTO app_recommenderinfo (id, last_known_user_id, last_known_song_id, last_known_user_event_id) VALUES (1, %s, %s, %s)""",
                    """SET foreign_key_checks = 1"""
                ]
                params = [(), (user_last, song_last, last_action), ()]

        if count == 1:
            if update_query is not None and params is not None:
                with closing(db.cursor()) as c:
                    c.execute(update_query, params)
        else:
            if count != 0:
                with closing(db.cursor()) as c:
                    c.execute("""TRUNCATE TABLE app_recommenderinfo""")
            if insert_query is not None and params is not None:
                with closing(db.cursor()) as c:
                    for i in xrange(len(insert_query)):
                        c.execute(insert_query[i], params[i])
            else:
                raise Exception("Unexpected behaviour of save_lasts")
        db.commit()

    def get_lasts(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute(
                """SELECT last_known_user_id, last_known_song_id, last_known_user_event_id FROM app_recommenderinfo""")
            last_u, last_i, last_event = c.fetchone()
        return last_u, last_i, last_event

    def get_users_ids(self, since_id=-1):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM auth_user WHERE id > %s ORDER BY id """, (since_id,))
            ids = map(lambda entry: entry[0], c.fetchall())
        return ids

    def get_items_ids(self, since_id=-1):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM app_song WHERE id > %s ORDER BY id""", (since_id,))
            ids = map(lambda entry: entry[0], c.fetchall())
        return ids

    def get_user_actions(self, action, last_action=-1):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id, action_json FROM app_useraction WHERE id > %s AND action_type = %s ORDER BY date""",
                      (last_action, action))
            actions = map(lambda entry: (entry[0], json.loads(entry[1], encoding='utf-8')), c.fetchall())
        return actions


