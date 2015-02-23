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


class TableNotCreated(Exception):
    def __init__(self, *args, **kwargs):
        super(TableNotCreated, self).__init__(*args, **kwargs)


class Db:
    RECS_TABLE_NAME = 'recs'

    def __init__(self, config_filename):
        config = ConfigParser.ConfigParser()
        config.read(config_filename)
        self.conn_info = {
            'host': config.get('db', 'HOST'),
            'port': int(config.get('db', 'PORT')),
            'user': config.get('db', 'USER'),
            'passwd': config.get('db', 'PASSWORD'),
            'db': config.get('db', 'NAME')
        }

        self.db = None

    def connect(self):
        if self.db is None:
            self.db = MySQLdb.connect(**self.conn_info)
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
                params = (user_last, song_last, last_action)
                insert_query = [
                    """SET foreign_key_checks = 0""",
                    """INSERT INTO app_recommenderinfo (id, last_known_user_id, last_known_song_id, last_known_user_event_id) VALUES (1, %s, %s, %s)""",
                    """SET foreign_key_checks = 1"""
                ]
                insert_params = [(), params, ()]

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
                        c.execute(insert_query[i], insert_params[i])
            else:
                raise Exception("Unexpected behaviour of save_lasts")
        db.commit()

    def get_lasts(self):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute(
                """SELECT last_known_user_id, last_known_song_id, last_known_user_event_id FROM app_recommenderinfo""")
            if c.rowcount == 0:
                return None, None, None
            last_u, last_i, last_event = c.fetchone()
        return last_u, last_i, last_event

    def get_users_ids(self, since_id=-1):
        if since_id is None:
            since_id = -1
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM auth_user WHERE id > %s ORDER BY id """, (since_id,))
            ids = map(lambda entry: entry[0], c.fetchall())
        return ids

    def get_items_ids(self, since_id=-1):
        if since_id is None:
            since_id = -1
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT id FROM app_song WHERE id > %s ORDER BY id""", (since_id,))
            ids = map(lambda entry: entry[0], c.fetchall())
        return ids

    def get_user_actions(self, action, last_action=-1, mapper=None):
        db = self.connect()
        if mapper is None:
            mapper = lambda x: x

        with closing(db.cursor()) as c:
            c.execute("""SELECT id, action_json FROM app_useraction WHERE id > %s AND action_type = %s ORDER BY date""",
                      (last_action, action))
            actions = map(lambda entry: (entry[0], mapper(json.loads(entry[1], encoding='utf-8'))), c.fetchall())
        return actions

    def get_all_ratings(self, mapper=None):
        db = self.connect()

        with closing(db.cursor()) as c:
            c.execute("""SELECT user_id, song_id, rating FROM app_rating ORDER BY user_id, song_id""")
            if mapper is None:
                return c.fetchall()
            else:
                return map(lambda entry: mapper(entry[0], entry[1], entry[2]), c.fetchall())

    def check_table_exists(self, table_name):
        db = self.connect()
        q = """SELECT COUNT(*)
               FROM information_schema.tables
               WHERE table_schema = %s
               AND table_name = %s"""

        with closing(db.cursor()) as c:
            c.execute(q, (self.conn_info['db'], table_name))
            res = int(c.fetchone()[0])
        return res > 0

    def create_recommendations_table(self, table_name):
        db = self.connect()
        q = """CREATE TABLE %s (
               id int(11) NOT NULL AUTO_INCREMENT,
               user_id int(11) NOT NULL,
               song_id int(11) NOT NULL,
               score double NOT NULL,
               PRIMARY KEY (id),
               UNIQUE KEY user_id_song_id_unique (user_id, song_id),
               KEY song_id_key (song_id),
               KEY user_id_key (user_id),
               KEY score_key (score),
               CONSTRAINT song_id_fk FOREIGN KEY (song_id) REFERENCES app_song (id),
               CONSTRAINT user_id_fk FOREIGN KEY (user_id) REFERENCES auth_user (id)
               ) ENGINE=InnoDB DEFAULT CHARSET=utf8
            """ % (table_name,)
        res = None
        with closing(db.cursor()) as c:
            try:
                c.execute(q)
                db.commit()
                res = True
            except Exception as e:
                pprint(e)
                db.rollback()
                res = False

        self.disconnect()
        return res

    def destroy_recommendations(self, user_id):
        if not self.check_table_exists(self.RECS_TABLE_NAME):
            return True

        q = """DELETE FROM %s WHERE user_id = %%s""" % self.RECS_TABLE_NAME
        db = self.connect()

        with closing(db.cursor()) as c:
            try:
                c.execute(q, (user_id,))
                db.commit()
                res = True
            except Exception as e:
                pprint(e)
                db.rollback()
                res = False

        self.disconnect()
        return res

    def save_recommendations(self, user_id, recs):
        if not self.check_table_exists(self.RECS_TABLE_NAME):
            res = self.create_recommendations_table(self.RECS_TABLE_NAME)
            if not res:
                raise TableNotCreated()

        values = []
        for r in recs:
            value = '(%d, %d, %f)'
            values.append(value % (user_id, r.item_id, r.score))

        values_str = ','.join(values)
        q = """INSERT INTO %s (user_id, song_id, score) VALUES %s""" % (self.RECS_TABLE_NAME, values_str)

        db = self.connect()

        with closing(db.cursor()) as c:
            try:
                c.execute(q)
                db.commit()
                res = c.rowcount
            except Exception as e:
                pprint(e)
                db.rollback()
                res = -1

        self.disconnect()
        return res


