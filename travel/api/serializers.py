from rest_framework import serializers
from ..models import TravelLog, TravelEntity


class TravelLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = TravelLog
        fields = '__all__'


class TravelEntitySerializer(serializers.ModelSerializer):
    type_abbr = serializers.ReadOnlyField(source='type.abbr')
    flag_svg = serializers.ImageField(source='flag.svg', allow_null=True)
    country_name = serializers.ReadOnlyField(source='country.name')
    country_code = serializers.ReadOnlyField(source='country.code')
    country_flag_emoji = serializers.ReadOnlyField(source='country.flag.emoji')
    country_flag_svg = serializers.ImageField(source='country.flag.svg', allow_null=True)

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
            'type_abbr'
        )


class TravelUserLogSerializer(serializers.Serializer):
    logs = serializers.SerializerMethodField('get_logs')
    entities = serializers.SerializerMethodField('get_entities')

    def get_logs(self, obj):
        return TravelLogSerializer(
            TravelLog.objects.all(),
            many=True
        ).data

    def get_entities(self, obj):
        return TravelEntitySerializer(
            TravelEntity.objects.filter(travellog__rating__gte=0).distinct(),
            many=True
        ).data


def logs_for_user(username):
    return {
        'logs': TravelLogSerializer(
            TravelLog.objects.filter(user__username=username),
            many=True
        ).data,
        'entities': TravelEntitySerializer(
            TravelEntity.objects.filter(
                travellog__user__username=username
            ).distinct().select_related('country', 'flag', 'country__flag', 'type'),
            many=True
        ).data
    }
