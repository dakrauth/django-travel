from itertools import chain
from rest_framework import serializers

from django.contrib.auth.models import User
from travel.models import TravelLog, TravelEntity
from travel.extras import games


class TravelLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = TravelLog
        fields = '__all__'


class TravelEntitySerializer(serializers.ModelSerializer):
    type_abbr = serializers.ReadOnlyField(source='type.abbr')
    flag_svg = serializers.ImageField(source='flag.svg', allow_null=True)
    country_name = serializers.ReadOnlyField(source='country.name', allow_null=True)
    country_code = serializers.ReadOnlyField(source='country.code', allow_null=True)
    country_flag_emoji = serializers.ReadOnlyField(source='country.flag.emoji', allow_null=True)
    country_flag_svg = serializers.ImageField(source='country.flag.svg', allow_null=True)
    url = serializers.URLField(source='get_absolute_url')

    class Meta:
        model = TravelEntity
        fields = (
            'id',
            'code',
            'name',
            'locality',
            'flag_svg',
            'country_name',
            'country_code',
            'country_flag_svg',
            'country_flag_emoji',
            'type_abbr',
            'url'
        )


class TravelUserLogSerializer(serializers.ModelSerializer):
    logs = serializers.SerializerMethodField()
    entities = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'logs', 'entities']

    def get_logs(self, obj):
        return TravelLogSerializer(
            TravelLog.objects.filter(user=obj),
            many=True
        ).data

    def get_entities(self, obj):
        return TravelEntitySerializer(
            TravelEntity.objects.filter(
                travellog__user=obj
            ).distinct().select_related('country', 'flag', 'country__flag', 'type'),
            many=True
        ).data


class FlagEntitySerializer(serializers.ModelSerializer):
    image = serializers.URLField(source='flag.svg.url')

    class Meta:
        model = TravelEntity
        fields = ['name', 'code', 'image']


def flag_data():
    return {
        'countries': FlagEntitySerializer(
            TravelEntity.objects.countries().filter(
                code__in={*chain(*games.FLAG_GROUPS)}
            ).select_related('flag'),
            many=True
        ).data,
        'groups': games.FLAG_GROUPS
    }
