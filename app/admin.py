from django.contrib import admin

from .models import *


class SongAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner_id', 'song_id', 'artist', 'title', 'duration', 'genre', 'fingerprinted')


class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'song', 'rating', 'is_implicit')


class ListenCharacteristicAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'user', 'song', 'hops_count', 'listen_duration')


class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'song', 'date', 'action_type', 'action_json')


class RecommenderInfoAdmin(admin.ModelAdmin):
    list_display = ('last_known_user', 'last_known_song', 'last_known_user_event')


class FingerprintsAdmin(admin.ModelAdmin):
    list_display = ('hash', 'song', 'offset')


class RecsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'song', 'score')
    ordering = ('user', '-score')


class SvdBiAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'value')


class SvdBuAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'value')


class SvdFeaturesAdmin(admin.ModelAdmin):
    list_display = ('id', 'feature')


class SvdMuAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')


class SvdPiAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'feature', 'value')
    ordering = ('item', 'feature')


class SvdPuAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'feature', 'value')
    ordering = ('user', 'feature')


class UsersFeaturesAdmin(admin.ModelAdmin):
    list_display = ('user', 'features', 'baseline')
    ordering = ('user_id', )


class ItemsFeaturesAdmin(admin.ModelAdmin):
    list_display = ('song', 'features', 'baseline')
    ordering = ('song_id', )



admin.site.register(Song, SongAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(ListenCharacteristic, ListenCharacteristicAdmin)
admin.site.register(UserAction, UserActionAdmin)
admin.site.register(RecommenderInfo, RecommenderInfoAdmin)

admin.site.register(Fingerprints, FingerprintsAdmin)
admin.site.register(Recs, RecsAdmin)
admin.site.register(SvdMu, SvdMuAdmin)
admin.site.register(SvdFeatures, SvdFeaturesAdmin)
admin.site.register(SvdBi, SvdBiAdmin)
admin.site.register(SvdBu, SvdBuAdmin)
admin.site.register(SvdPi, SvdPiAdmin)
admin.site.register(SvdPu, SvdPuAdmin)


admin.site.register(UsersFeatures, UsersFeaturesAdmin)
admin.site.register(ItemsFeatures, ItemsFeaturesAdmin)
