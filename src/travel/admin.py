from django.contrib import admin
from travel import models as travel


@admin.register(travel.Electrical)
class ElectricalAdmin(admin.ModelAdmin):
    list_display = ("voltage", "frequency", "plugs")
    raw_id_fields = ["entity"]


class AliasInline(admin.TabularInline):
    model = travel.TravelAlias


class ExternalReferenceInline(admin.TabularInline):
    model = travel.ExternalReference


@admin.register(travel.TravelEntity)
class TravelEntityAdmin(admin.ModelAdmin):
    list_filter = ("type",)
    list_display = (
        "name",
        "id",
        "code",
        "type",
        "classification",
        "capital",
        "state",
        "country",
    )
    raw_id_fields = ["state", "capital", "country", "flag", "continent"]
    search_fields = ["name", "full_name", "code"]
    inlines = [AliasInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "type", "classification", "capital", "state", "country"
        )


@admin.register(travel.TravelAliasCategory)
class TravelAliasCategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "description"]


@admin.register(travel.TravelEntityType)
class TravelEntityTypeAdmin(admin.ModelAdmin):
    list_display = ("abbr", "title")


@admin.register(travel.TravelFlag)
class TravelFlagAdmin(admin.ModelAdmin):
    list_display = ("id", "source")
    search_fields = ["source"]


@admin.register(travel.TravelProfile)
class TravelProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "access")


@admin.register(travel.TravelBucketList)
class TravelBucketListAdmin(admin.ModelAdmin):
    list_display = ("id", "owner", "title", "is_public", "description")
    raw_id_fields = ["entities"]


@admin.register(travel.TravelLog)
class TravelLogAdmin(admin.ModelAdmin):
    list_display = ("id", "arrival", "rating", "user", "entity")
    raw_id_fields = ["entity", "user"]


@admin.register(travel.TravelClassification)
class TravelClassificationAdmin(admin.ModelAdmin):
    list_display = ["type", "title"]
    list_filter = ["type"]


@admin.register(travel.TravelLanguage)
class TravelLanguageAdmin(admin.ModelAdmin):
    list_display = ["name", "iso639_1", "iso639_2", "iso639_3"]


@admin.register(travel.TravelCurrency)
class TravelCurrencyAdmin(admin.ModelAdmin):
    list_display = [
        "iso",
        "name",
        "sign",
        "updated",
        "value",
    ]


@admin.register(travel.TravelEntityInfo)
class TravelEntityInfoAdmin(admin.ModelAdmin):
    list_display = ["iso3", "denom", "tld"]
    filter_horizontal = ["languages", "neighbors"]
    raw_id_fields = [
        "entity",
    ]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "neighbors":
            kwargs["queryset"] = travel.TravelEntity.objects.filter(type__abbr="co")
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(travel.ExternalSource)
class ExternalSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "url"]
