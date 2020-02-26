from django.contrib import admin
from travel import models as travel


@admin.register(travel.TravelEntity)
class TravelEntityAdmin(admin.ModelAdmin):
    list_filter = ('type', )
    list_display = (
        'id',
        'code',
        'type',
        'classification',
        'name',
        'capital',
        'state',
        'country',
        'continent',
    )
    raw_id_fields = ['state', 'capital', 'country', 'continent', 'flag']
    search_fields = ['name', 'full_name', 'code']


@admin.register(travel.TravelEntityType)
class TravelEntityTypeAdmin(admin.ModelAdmin):
    list_display = ('abbr', 'title')


@admin.register(travel.TravelFlag)
class TravelFlagAdmin(admin.ModelAdmin):
    list_display = ('id', 'source')
    search_fields = ['source']


@admin.register(travel.TravelProfile)
class TravelProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'access')


@admin.register(travel.TravelBucketList)
class TravelBucketListAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'title', 'is_public', 'description')


@admin.register(travel.TravelLog)
class TravelLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'arrival', 'rating', 'user', 'entity')
