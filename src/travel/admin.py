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


@admin.register(travel.TravelClassification)
class TravelClassificationAdmin(admin.ModelAdmin):
    list_display = ['type', 'title']
    list_filter = ['type']


@admin.register(travel.TravelAlias)
class TravelAliasAdmin(admin.ModelAdmin):
    list_display = ['category', 'entity', 'alias']
    list_filter = ['category']


@admin.register(travel.TravelLanguage)
class TravelLanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'iso639_1', 'iso639_2', 'iso639_3',]


@admin.register(travel.TravelCurrency)
class TravelCurrencyAdmin(admin.ModelAdmin):
    list_display = ['iso', 'name', 'sign', 'fraction', 'fraction_name', 'alt_sign',]


@admin.register(travel.TravelRegion)
class TravelRegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'un_code', 'parent',]


@admin.register(travel.TravelEntityInfo)
class TravelEntityInfoAdmin(admin.ModelAdmin):
    list_display = [
        'entity',
        'iso3',
        'denom',
        'denoms',
        'tld',
        'region',
    ]


