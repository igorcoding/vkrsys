from django.db import models, connection, transaction


class SongManager(models.Manager):

    def bulk_create_new(self, recs):
        """
        bulk create recs, skipping key conflicts that would raise an IntegrityError
        # return value: int count of recs written
        """

        try:
            if not recs:
                return 0
            cursor = connection.cursor()

            # lock and empty tmp table
            sql = """
            BEGIN;
            START TRANSACTION;
            TRUNCATE TABLE app_songtmp;
            COMMIT;
            """
            cursor.execute(sql)
            cursor.close()

            # write to tmp table
            SongTmp.objects.bulk_create(recs)

            cursor = connection.cursor()
            sql = """BEGIN;
            START TRANSACTION;

            INSERT INTO app_song (s_id,artist,title,duration,genre,url)
            SELECT s_id,artist,title,duration,genre,url FROM app_songtmp WHERE NOT EXISTS (
                SELECT 1 FROM app_song WHERE app_songtmp.s_id = app_song.s_id
            );
            COMMIT;
            """
            cursor.execute(sql)
            cursor.close()
            transaction.commit_unless_managed()
            # statusmessage is of form 'INSERT 0 1'
            # return int(cursor.cursor.cursor.statusmessage.split(' ').pop())
        except (IndexError, ValueError):
            raise Exception("Unexpected statusmessage from INSERT")


class SongBase(models.Model):
    s_id = models.IntegerField(unique=True, db_index=True)
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    duration = models.SmallIntegerField()
    genre = models.SmallIntegerField(null=True)
    url = models.CharField(max_length=255)

    class Meta:
        abstract = True


class SongTmp(SongBase):
    pass


class Song(SongBase):
    objects = SongManager()
