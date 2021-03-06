from contextlib import closing
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, connection, transaction
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


class SongManager(models.Manager):
    def bulk_create_new(self, recs):
        """
        bulk create recs, skipping key conflicts that would raise an IntegrityError
        # return value: int count of recs written
        """

        try:
            if not recs:
                return 0
            with closing(connection.cursor()) as cursor:
                # lock and empty tmp table
                sql = """
                BEGIN;
                START TRANSACTION;
                TRUNCATE TABLE app_songtmp;
                COMMIT;
                """
                cursor.execute(sql)

            # write to tmp table
            SongTmp.objects.bulk_create(recs)

            with closing(connection.cursor()) as cursor:
                sql = """BEGIN;
                START TRANSACTION;

                INSERT INTO app_song (owner_id,song_id,artist,title,duration,genre,url,art_url,fingerprinted)
                SELECT owner_id,song_id,artist,title,duration,genre,url,art_url,fingerprinted FROM app_songtmp WHERE NOT EXISTS (
                    SELECT 1 FROM app_song WHERE app_songtmp.owner_id = app_song.owner_id AND
                                                 app_songtmp.song_id = app_song.song_id
                );
                COMMIT;
                """
                cursor.execute(sql)
            transaction.commit_unless_managed()
            # statusmessage is of form 'INSERT 0 1'
            # return int(cursor.cursor.cursor.statusmessage.split(' ').pop())
        except (IndexError, ValueError):
            raise Exception("Unexpected statusmessage from INSERT")


class SongBase(models.Model):
    owner_id = models.IntegerField()
    song_id = models.IntegerField()
    artist = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    duration = models.SmallIntegerField()
    genre = models.SmallIntegerField(null=True)
    url = models.CharField(max_length=255, null=True)
    art_url = models.CharField(max_length=255, null=False, default=settings.SONGS_DEFAULT_ART_URL)
    fingerprinted = models.BooleanField(default=False)

    def __unicode__(self):
        thr = 80
        artist = self.artist
        title = self.title
        if len(artist) > thr:
            artist = u'{0}...'.format(artist[:thr])
        if len(title) > thr:
            title = u'{0}...'.format(title[:thr])
        return "[%d] %s - %s" % (self.id, artist, title)

    class Meta:
        unique_together = ('owner_id', 'song_id')
        index_together = ('owner_id', 'song_id')
        abstract = True


class SongTmp(SongBase):
    pass


class Song(SongBase):
    objects = SongManager()


class UserAction(models.Model):
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    date = models.DateTimeField(auto_now=True)
    action_type = models.CharField(max_length=25)
    action_json = models.CharField(max_length=255)

    def __unicode__(self):
        return u'[%d] %s' % (self.id, self.action_json)


class Rating(models.Model):
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    rating = models.FloatField(default=0.0)
    is_implicit = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'song')


class ListenCharacteristic(models.Model):
    uuid = models.CharField(max_length=40)
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    hops_count = models.IntegerField()
    listen_duration = models.IntegerField()

    class Meta:
        unique_together = ('uuid', 'user', 'song')


class RecommenderInfo(models.Model):
    last_known_user = models.ForeignKey(User)
    last_known_song = models.ForeignKey(Song)
    last_known_user_event = models.ForeignKey(UserAction)


#############################################################


class Fingerprints(models.Model):
    hash = models.CharField(max_length=10, primary_key=True)
    song = models.ForeignKey(Song)
    offset = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'fingerprints'
        verbose_name = 'Fingerprints'
        verbose_name_plural = 'Fingerprints'


class Recs(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(User)
    song = models.ForeignKey(Song)
    score = models.FloatField()

    class Meta:
        managed = False
        db_table = 'recs'
        verbose_name = 'Recs'
        verbose_name_plural = 'Recs'


class SvdBi(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    item = models.ForeignKey(Song)
    value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'svd_bI'
        verbose_name = 'SvdBi'
        verbose_name_plural = 'SvdBi'


class SvdBu(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(User)
    value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'svd_bU'
        verbose_name = 'SvdBu'
        verbose_name_plural = 'SvdBu'


class SvdFeatures(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    feature = models.IntegerField()

    def __unicode__(self):
        return u'%d' % self.feature

    class Meta:
        managed = False
        db_table = 'svd_features'
        verbose_name = 'SvdFeatures'
        verbose_name_plural = 'SvdFeatures'


class SvdMu(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    value = models.FloatField()

    def __unicode__(self):
        return u'%d' % self.value

    class Meta:
        managed = False
        db_table = 'svd_mu'
        verbose_name = 'SvdMu'
        verbose_name_plural = 'SvdMu'


class SvdPi(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    item = models.ForeignKey(Song)
    feature = models.ForeignKey(SvdFeatures)
    value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'svd_pI'
        verbose_name = 'SvdPi'
        verbose_name_plural = 'SvdPi'


class SvdPu(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(User)
    feature = models.ForeignKey(SvdFeatures)
    value = models.FloatField()

    class Meta:
        managed = False
        db_table = 'svd_pU'
        verbose_name = 'SvdPu'
        verbose_name_plural = 'SvdPu'


class UsersFeatures(models.Model):
    user_id = models.IntegerField(primary_key=True)
    user = models.CharField(max_length=44)
    features = models.TextField(blank=True)
    baseline = models.FloatField()

    class Meta:
        managed = False
        db_table = 'users_features'


class ItemsFeatures(models.Model):
    song_id = models.IntegerField(primary_key=True)
    song = models.CharField(max_length=77)
    features = models.TextField(blank=True)
    baseline = models.FloatField()

    class Meta:
        managed = False
        db_table = 'items_features'