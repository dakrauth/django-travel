import pytest
from django.contrib.auth.models import User
from travel.models import (
    TravelEntityType,
    TravelEntity,
    TravelBucketList
)


@pytest.fixture
def user():
    return User.objects.create_user(username='user')


@pytest.fixture
def user2():
    return User.objects.create_user(username='user2')


@pytest.fixture
def continent_type():
    return TravelEntityType.objects.create(abbr='cn', title='Continent')


@pytest.fixture
def country_type():
    return TravelEntityType.objects.create(abbr='co', title='Country')


@pytest.fixture
def continent(continent_type):
    name = 'Continent'
    return TravelEntity.objects.create(
        type=continent_type,
        code='CN',
        name=name,
        full_name=name,
    )


@pytest.fixture
def country(continent, country_type):
    name = 'Country'
    return TravelEntity.objects.create(
        type=country_type,
        code='CO',
        name=name,
        continent=continent,
        full_name=name,
    )


@pytest.fixture
def bucketlist(country):
    bl = TravelBucketList.objects.create(
        owner=None,
        title='Test Bucket List',
        is_public=True,
    )
    bl.entities.add(country)
    return bl
