import os
from collections import Counter

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property

import pytz
from choice_enum import ChoiceEnumeration
import travel.utils as travel_utils
from . import managers

GOOGLE_MAPS = 'http://maps.google.com/maps?q={}'
GOOGLE_MAPS_LATLON = 'http://maps.google.com/maps?q={},+{}&iwloc=A&z=10'
WIKIPEDIA_URL = 'http://en.wikipedia.org/wiki/Special:Search?search={}&go=Go'
WORLD_HERITAGE_URL = 'http://whc.unesco.org/en/list/{}'
BASE_FLAG_DIR = 'travel/img/flags'
STAR = mark_safe('&#9733;')


def svg_upload(instance, filename):
    return '{}/{}-{}'.format(BASE_FLAG_DIR, instance.id, filename)


class TravelFlag(models.Model):
    source = models.CharField(max_length=255)
    svg = models.FileField(upload_to=svg_upload, blank=True)
    is_locked = models.BooleanField(default=False)
    emoji = models.CharField(max_length=8, blank=True)

    class Meta:
        db_table = 'travel_flag'
        verbose_name_plural = 'flags'

    @cached_property
    def image_url(self):
        if self.svg and os.path.exists(self.svg.path):
            return self.svg.url

        return self.source

    @cached_property
    def thumb_url(self):
        return self.image_url


class TravelBucketList(models.Model):
    owner = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    is_public = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    entities = models.ManyToManyField('TravelEntity')
    last_update = models.DateTimeField(auto_now=True)

    objects = managers.TravelBucketListManager()

    class Meta:
        db_table = 'travel_bucket_list'
        verbose_name_plural = 'bucket lists'


    def get_absolute_url(self):
        return reverse('travel-bucket', args=[self.id])

    def __str__(self):
        return self.title

    def user_results(self, user):
        all_entities = self.entities.select_related('flag', 'type', 'state', 'country')
        if not user.is_authenticated:
            return 0, [(e, 0) for e in all_entities]

        logged_entities = Counter(TravelLog.objects.filter(
            user=user,
            entity__in=all_entities
        ).values_list('entity__id', flat=True))

        entities = [
            (entity, logged_entities.get(entity.id, 0))
            for entity in all_entities
        ]
        done = sum(1 if b else 0 for a, b in entities)
        return done, entities


class TravelProfile(models.Model):

    class Access(ChoiceEnumeration):
        PUBLIC = ChoiceEnumeration.Option('PUB', 'Public')
        PRIVATE = ChoiceEnumeration.Option('PRI', 'Private')
        PROTECTED = ChoiceEnumeration.Option('PRO', 'Protected', default=True)

    user = models.OneToOneField(User, related_name='travel_profile', on_delete=models.CASCADE)
    access = models.CharField(max_length=3, choices=Access.CHOICES, default=Access.DEFAULT)

    objects = managers.TravelProfileManager()

    class Meta:
        db_table = 'travel_profile'
        verbose_name_plural = 'profile'

    def public_url(self):
        return reverse('travel-profile', args=[self.user.username])

    def __str__(self):
        return str(self.user)

    def history_json(self):
        return TravelLog.history_json(self.user)

    is_public = property(lambda self: self.access == self.Access.PUBLIC)
    is_private = property(lambda self: self.access == self.Access.PRIVATE)
    is_protected = property(lambda self: self.access == self.Access.PROTECTED)


def profile_factory(sender, instance, created=False, **kws):
    if created:
        TravelProfile.objects.get_or_create(user=instance)


models.signals.post_save.connect(profile_factory, sender=User)


class TravelEntityType(models.Model):
    abbr = models.CharField(max_length=4, db_index=True)
    title = models.CharField(max_length=25)

    class Meta:
        db_table = 'travel_entitytype'
        verbose_name_plural = 'entity types'

    def __str__(self):
        return self.title


class TravelClassification(models.Model):
    type = models.ForeignKey(TravelEntityType, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = 'classifications'

    def __str__(self):
        return self.title


class Extern(object):

    def __init__(self, name, handler, entity):
        self.name = name
        self.handler = handler
        self.entity = entity

    @cached_property
    def url(self):
        return self.handler(self.entity)

    @staticmethod
    def wikipedia_url(entity):
        return WIKIPEDIA_URL.format(travel_utils.nice_url(entity.full_name))

    @staticmethod
    def world_heritage_url(entity):
        return WORLD_HERITAGE_URL.format(entity.code)

    @classmethod
    def get(cls, entity):
        default = ('Wikipedia', cls.wikipedia_url)
        handlers = {
            'wh': ('UNESCO', cls.world_heritage_url)
        }

        name, hdlr = handlers.get(entity.type.abbr, default)
        return cls(name, hdlr, entity)


class TravelEntity(models.Model):
    type = models.ForeignKey(TravelEntityType, related_name='entity_set', on_delete=models.PROTECT)
    code = models.CharField(max_length=8, db_index=True)
    alt_code = models.CharField(max_length=8, db_index=True, default='', blank=True)
    name = models.CharField(max_length=175)
    full_name = models.CharField(max_length=175)
    lat = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    lon = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    locality = models.CharField(max_length=256, blank=True)

    classification = models.ForeignKey(TravelClassification, on_delete=models.CASCADE,
        blank=True, null=True)
    flag = models.ForeignKey(TravelFlag, null=True, blank=True, on_delete=models.SET_NULL)
    capital = models.ForeignKey('self', related_name='capital_set', on_delete=models.SET_NULL,
        blank=True, null=True)
    state = models.ForeignKey('self', related_name='state_set', on_delete=models.SET_NULL,
        blank=True, null=True)
    country = models.ForeignKey('self', related_name='country_set', on_delete=models.SET_NULL,
        blank=True, null=True)
    continent = models.ForeignKey('self', related_name='continent_set', on_delete=models.SET_NULL,
        blank=True, null=True)

    tz = models.CharField('timezone', max_length=40, blank=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.TextField(default='', blank=True)

    objects = managers.TravelEntityManager()

    class Meta:
        ordering = ('name',)
        db_table = 'travel_entity'
        verbose_name_plural = 'entities'

    class Related:
        ENTITY_TYPES = {'co': 'entity_set__country', 'st': 'entity_set__state'}
        DETAILS = {
            'co': 'Countries',
            'st': 'States, provinces, territories, etc',
            'ct': 'Cities',
            'ap': 'Airports',
            'np': 'National Parks',
            'lm': 'Landmarks',
            'wh': 'World Heriage Sites',
        }
        BY_TYPE_PARAMS = {
            'co': 'country',
            'st': 'state',
            'cn': {
                'co': 'continent',
                'default': 'country__continent'
            }
        }

    def __str__(self):
        return self.name

    def descriptive_name(self):
        if self.type.abbr == 'ct':
            what = self.state or self.country
            return '{}{}'.format(self, ', {}'.format(what) if what else '')
        return str(self)

    @cached_property
    def code_url_bit(self):
        code = self.code or self.id
        if self.type.abbr in ('st', 'wh'):
            code = '{}-{}'.format(self.country.code, code) if self.country else code
        return code

    @cached_property
    def _permalink_args(self):
        return [self.type.abbr, self.code_url_bit]

    def get_absolute_url(self):
        return reverse('travel-entity', args=self._permalink_args)

    def get_edit_url(self):
        return reverse('travel-entity-edit', args=self._permalink_args)

    def wikipedia_search_url(self):
        return Extern.wikipedia_url(self)

    @property
    def extern(self):
        return Extern.get(self)

    @cached_property
    def get_entityinfo(self):
        try:
            #return TravelEntityInfo.objects.get(entity=self)
            return TravelEntityInfo.objects.select_related(
                'currency',
                'region',
                'entity'
            ).prefetch_related(
                'languages',
                'neighbors',
            ).get(entity=self)
        except TravelEntityInfo.DoesNotExist:
            return None

    @cached_property
    def category_detail(self):
        if self.classification:
            return self.classification.title

        return self.type.title

    @cached_property
    def timezone(self):
        return (
            self.tz
            or (self.state and self.state.timezone)
            or (self.country and self.country.timezone)
            or 'UTC'
        )

    @property
    def tzinfo(self):
        return pytz.timezone(self.timezone)

    def get_continent(self):
        if self.continent:
            return self.continent
        return self.country.continent if self.country else None

    @property
    def relationships(self):
        abbr = self.type.abbr
        qs = None
        if abbr == 'cn':
            qs = TravelEntityType.objects.distinct().filter(
                models.Q(entity_set__continent=self) |  # noqa
                models.Q(entity_set__country__continent=self)
            )
        else:
            key = self.Related.ENTITY_TYPES.get(abbr)
            if key:
                qs = TravelEntityType.objects.distinct().filter(**{key: self})

        return () if qs is None else qs.annotate(
            cnt=models.Count('abbr')
        ).values_list('abbr', 'cnt')


    @cached_property
    def related_entities(self):
        return [{
            'abbr': abbr,
            'text': self.Related.DETAILS[abbr],
            'count': cnt,
            'url': reverse(
                'travel-entity-relationships',
                args=[self.type.abbr, self.code_url_bit, abbr]
            )
        } for abbr, cnt in self.relationships]

    @property
    def flag_dir(self):
        abbr = self.type.abbr
        if abbr == 'co' or abbr == 'ct':
            return abbr
        elif abbr == 'st' and self.country:
            return 'st/{}'.format(self.country.code.lower())
        return ''

    def related_by_type(self, type):
        key = self.Related.BY_TYPE_PARAMS[self.type.abbr]
        if isinstance(key, dict):
            key = key.get(type.abbr, key['default'])

        qs = TravelEntity.objects.filter(**{key: self, 'type': type})
        return TravelEntity.objects.type_related(type, qs)

    def update_flag(self, flag_url):
        flag = self.flag if self.flag and not self.flag.is_locked else TravelFlag()
        flag.source = flag_url
        flag.save()
        self.flag = flag
        self.save()
        return flag

    @property
    def lower(self):
        return self.code.lower()

    @cached_property
    def lat_lon_str(self):
        return f'{self.lat},{self.lon}' if self.lat else ''

    @cached_property
    def lat_lon_display(self):
        return f'{self.lat}° Lat, {self.lon}° Lon' if self.lat else ''

    @property
    def google_maps_url(self):
        if self.lat or self.lon:
            return GOOGLE_MAPS_LATLON.format(self.lat, self.lon)
        else:
            return GOOGLE_MAPS.format(travel_utils.nice_url(self.name),)


class ExternalSource(models.Model):
    name = models.CharField(max_length=50, unique=True)
    url = models.URLField(blank=True)


class ExternalReference(models.Model):
    source = models.ForeignKey(ExternalSource, on_delete=models.CASCADE)
    ref = models.CharField(max_length=255)
    entity = models.ForeignKey(TravelEntity, on_delete=models.CASCADE)


class TravelAlias(models.Model):
    category = models.CharField(max_length=50)
    entity = models.ForeignKey(TravelEntity, on_delete=models.CASCADE)
    alias = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'aliases'


class TravelLog(models.Model):

    RATING_CHOICES = (
        (1, mark_safe(STAR * 5)),
        (2, mark_safe(STAR * 4)),
        (3, mark_safe(STAR * 3)),
        (4, mark_safe(STAR * 2)),
        (5, mark_safe(STAR * 1)),
    )

    arrival = models.DateTimeField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=3)
    user = models.ForeignKey(User, related_name='travellog_set', on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    entity = models.ForeignKey(TravelEntity, on_delete=models.CASCADE)

    objects = managers.TravelLogManager()

    class Meta:
        get_latest_by = 'arrival'
        ordering = ('-arrival',)
        verbose_name_plural = 'logs'

    def __str__(self):
        return '{} | {}'.format(self.entity, self.user)

    @property
    def local_arrival(self):
        return self.arrival.astimezone(self.entity.tzinfo)

    def get_absolute_url(self):
        return reverse('travel-log-entry', args=[self.user.username, self.id])

    def save(self, *args, **kws):
        if not self.arrival:
            self.arrival = timezone.now()

        return super(TravelLog, self).save(*args, **kws)

    def update_notes(self, note):
        self.notes = note
        self.save()

    @classmethod
    def user_history(cls, user):
        return (
            TravelEntity.objects.filter(travellog__user=user).distinct().values(
                'id', 'code', 'name', 'locality', 'flag__svg', 'country__name', 'country__code',
                'country__flag__svg', 'country__flag__emoji', 'type__abbr'
            ),
            TravelLog.objects.filter(user=user).order_by('-arrival').values(
                'id', 'arrival', 'entity__id', 'rating'
            )
        )

    @classmethod
    def history_json(cls, user):
        entities, logs = cls.user_history(user)
        return travel_utils.json_dumps({
            'entities': list(entities),
            'logs': list(logs)
        })


class TravelLanguage(models.Model):
    iso639_1 = models.CharField(blank=True, max_length=2)
    iso639_2 = models.CharField(blank=True, max_length=12)
    iso639_3 = models.CharField(blank=True, max_length=3)
    name = models.CharField(max_length=60)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'languages'

    def __str__(self):
        return self.name

    @cached_property
    def related_entities(self):
        return TravelEntity.objects.filter(entityinfo__languages=self)

    def get_absolute_url(self):
        return reverse('travel-language', args=[self.id])


class TravelCurrency(models.Model):
    iso = models.CharField(max_length=4, primary_key=True)
    name = models.CharField(max_length=50)
    fraction = models.CharField(blank=True, max_length=8)
    fraction_name = models.CharField(blank=True, max_length=15)
    sign = models.CharField(blank=True, max_length=4)
    alt_sign = models.CharField(blank=True, max_length=4)

    class Meta:
        db_table = 'travel_currency'
        verbose_name_plural = 'currencies'
        ordering = ['iso']

    def __str__(self):
        return self.name


class EntityImage(object):

    def __init__(self, entity, location):
        fn = entity.code.lower() + '.gif'
        self.fqdn = os.path.join(settings.MEDIA_ROOT, 'travel/img', location, fn)
        self.exists = os.path.exists(self.fqdn)
        self.url = settings.MEDIA_URL + '/'.join(['travel/img', location, fn])


class TravelRegion(models.Model):
    name = models.CharField(max_length=50)
    un_code = models.CharField(max_length=5, db_index=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'regions'


class TravelEntityInfo(models.Model):
    entity = models.OneToOneField(TravelEntity, related_name='entityinfo', on_delete=models.CASCADE)
    iso3 = models.CharField(blank=True, max_length=3)
    currency = models.ForeignKey(TravelCurrency, blank=True, null=True, on_delete=models.SET_NULL)
    denom = models.CharField(blank=True, max_length=40)
    denoms = models.CharField(blank=True, max_length=60)
    language_codes = models.CharField(blank=True, max_length=100)
    phone = models.CharField(blank=True, max_length=20)
    electrical = models.CharField(blank=True, max_length=40)
    postal_code = models.CharField(blank=True, max_length=60)
    tld = models.CharField(blank=True, max_length=8)
    population = models.IntegerField(blank=True, null=True, default=None)
    area = models.IntegerField(blank=True, null=True, default=None)
    languages = models.ManyToManyField(TravelLanguage, blank=True)
    neighbors = models.ManyToManyField(TravelEntity, blank=True)
    region = models.ForeignKey(TravelRegion, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['entity']
        db_table = 'travel_entityinfo'
        verbose_name_plural = 'entity info'

    def __str__(self):
        return '<{}: {}>'.format('TravelEntityInfo', self.entity.name)

    @cached_property
    def get_languages(self):
        lang = ', '.join([lang.name for lang in self.languages.all()])
        return lang or 'Unknown'

    @cached_property
    def electrical_info(self):
        if self.electrical:
            v, h, p = self.electrical.split('/')
            return {'volts': v, 'hertz': h, 'plugs': p.split(',')}
        return {}

    @cached_property
    def images(self):
        images = [self.map, self.locator]
        return [i for i in images if i.exists]

    @cached_property
    def locator(self):
        return EntityImage(self.entity, 'locator')

    @cached_property
    def map(self):
        return EntityImage(self.entity, 'map')

    @cached_property
    def square_miles(self):
        if self.area is not None:
            return int(self.area * 0.386102)
