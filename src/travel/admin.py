from django.contrib import admin
from travel import models as travel


class CountryListFilter(admin.SimpleListFilter):
    title = 'country'
    parameter_name = 'country'
    template = 'travel/country-filter-template.html'

    def lookups(self, request, model_admin):
        return travel.TravelEntity.objects.filter(type__abbr='co').values_list('code', 'name')

    def queryset(self, request, queryset):
        return queryset.filter(country__code=self.value())


@admin.register(travel.TravelEntity)
class TravelEntityAdmin(admin.ModelAdmin):
    list_filter = ('type', CountryListFilter)
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
