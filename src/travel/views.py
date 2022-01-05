from datetime import timedelta
from collections import OrderedDict
from calendar import Calendar, SUNDAY

from django import http
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test

from . import models as travel
from . import forms

superuser_required = user_passes_test(
    lambda u: u.is_authenticated and u.is_active and u.is_superuser
)


def render_travel(
    request,
    base_templates,
    context=None,
    content_type=None,
    status=None
):
    if isinstance(base_templates, str):
        base_templates = [base_templates]

    custom = ['travel/custom/' + base for base in base_templates]
    templates = custom + ['travel/' + base for base in base_templates]
    return render(request, templates, context, content_type, status)


def flag_game(request):
    return render_travel(request, ['flag-game.html'])


def all_profiles(request):
    return render_travel(request, 'profile/all.html', {
        'profiles': travel.TravelProfile.objects.public()
    })


def profile(request, username):
    return render_travel(request, 'profile/profile.html', {
        'profile': get_object_or_404(travel.TravelProfile, user__username=username),
        'api_user_log_url': reverse('user_log_api', args=[username])
    })


def languages(request):
    return render_travel(request, 'languages.html', {
        'languages': travel.TravelLanguage.objects.all()
    })


def language(request, pk):
    return render_travel(request, 'languages.html', {
        'language': get_object_or_404(travel.TravelLanguage, pk=pk)
    })


def bucket_lists(request):
    return render_travel(request, 'buckets/listing.html', {
        'bucket_lists': travel.TravelBucketList.objects.for_user(request.user)
    })


def bucket_list_comparison(request, pk, usernames):
    bucket_list = get_object_or_404(travel.TravelBucketList, pk=pk)
    entities = bucket_list.entities.select_related()
    results = [{
        'username': username,
        'entities': set(travel.TravelLog.objects.filter(
            user__username=username,
            entity__in=entities
        ).values_list('entity__id', flat=True))
    } for username in usernames.split('/')]

    return render_travel(request, 'buckets/compare.html', {
        'bucket_list': bucket_list,
        'entities': entities,
        'results': results
    })


def _bucket_list_for_user(request, bucket_list, user):
    done, entities = bucket_list.user_results(user)
    return render_travel(request, 'buckets/detail.html', {
        'bucket_list': bucket_list,
        'entities': entities,
        'stats': {'total': len(entities), 'done': done}
    })


def bucket_list(request, pk):
    bucket_list = get_object_or_404(travel.TravelBucketList, pk=pk)
    return _bucket_list_for_user(request, bucket_list, request.user)


def bucket_list_for_user(request, pk, username):
    user = get_object_or_404(User, username=username)
    bucket_list = get_object_or_404(travel.TravelBucketList, pk=pk)
    return _bucket_list_for_user(request, bucket_list, user)


def search(request):
    search_form = forms.SearchForm(request.GET)
    data = {'search_form': search_form}
    if search_form.is_valid():
        q = search_form.cleaned_data['search']
        by_type = search_form.cleaned_data['type']
        data.update(search=q, by_type=by_type, results=travel.TravelEntity.objects.search(q, by_type))

    return render_travel(request, 'search/search.html', data)


@login_required
def search_advanced(request):
    # 'travel-search-advanced'
    data = {'results': None, 'search': ''}
    search = request.GET.get('search', '').strip()
    if search:
        lines = [line.strip() for line in search.splitlines()]
        data.update(
            search='\n'.join(lines),
            results=travel.TravelEntity.objects.advanced_search(lines)
        )

    return render_travel(request, 'search/advanced.html', data)


def by_locale(request, ref):
    etype = get_object_or_404(travel.TravelEntityType, abbr=ref)
    entities = travel.TravelEntity.objects.type_related(etype)
    template = 'entities/listing/{}.html'.format(ref)
    return render_travel(request, template, {'type': etype, 'entities': entities})


def _default_entity_handler(request, entity):
    form, history = None, []
    if request.user.is_authenticated:
        history = request.user.travellog_set.filter(entity=entity)
        if request.method == 'POST':
            form = forms.TravelLogForm(entity, request.POST)
            if form.is_valid():
                form.save(request.user)
                return http.HttpResponseRedirect(request.path)
        else:
            form = forms.TravelLogForm(entity)

    templates = [
        'entities/detail/{}.html'.format(entity.type.abbr),
        'entities/detail/base.html'
    ]

    return render_travel(request, templates, {
        'entity': entity,
        'form': form,
        'history': history
    })


def _handle_entity(request, ref, code, aux, handler):
    entity = travel.TravelEntity.objects.find(ref, code, aux)
    n = entity.count()
    if n == 0:
        raise http.Http404
    elif n > 1:
        return render_travel(request, 'search/search.html', {'results': entity})
    else:
        return handler(request, entity[0])


def entity(request, ref, code, aux=None):
    return _handle_entity(request, ref, code, aux, _default_entity_handler)


def entity_relationships(request, ref, code, rel, aux=None):
    etype = get_object_or_404(travel.TravelEntityType, abbr=rel)
    entities = travel.TravelEntity.objects.find(ref, code, aux)
    count = entities.count()

    if count == 0:
        raise http.Http404('No entity matches the given query.')
    elif count > 1:
        return render_travel(request, 'search/search.html', {'results': entities})

    entity = entities[0]
    related_entities = entity.related_by_type(etype)

    return render_travel(request, 'entities/listing/{}.html'.format(rel), {
        'type': etype,
        'entities': related_entities,
        'parent': entity
    })


def log_entry(request, username, pk):
    entry = get_object_or_404(travel.TravelLog, user__username=username, pk=pk)
    if request.user == entry.user:
        if request.method == 'POST':
            form = forms.TravelLogForm(entry.entity, request.POST, instance=entry)
            if form.is_valid():
                form.save(user=request.user)
                return http.HttpResponseRedirect(request.path)
        else:
            form = forms.TravelLogForm(entry.entity, instance=entry)
    else:
        form = None

    return render_travel(request, 'log-entry.html', {'entry': entry, 'form': form})


def calendar(request, username):
    profile = get_object_or_404(travel.TravelProfile.objects.public(), user__username=username)
    user = profile.user
    when = request.GET.get('when')
    now = timezone.now()
    dt = now.replace(day=15)
    if when:
        year, month = [int(i) for i in when.split('-')]
        dt = dt.replace(year=year, month=month)

    cal = Calendar()
    cal.setfirstweekday(SUNDAY)
    dates = OrderedDict(
        ((d.month, d.day), [])
        for d in list(cal.itermonthdates(dt.year, dt.month))
    )

    for (name, abbr, arrival, emoji) in user.travellog_set.filter(
        arrival__month=dt.month,
        user=user
    ).values_list('entity__name', 'entity__type__abbr', 'arrival', 'entity__flag__emoji'):
        key = (arrival.month, arrival.day)
        if key in dates:
            dates[key].append([name, abbr, arrival, emoji])

    dates = list(dates.items())
    context = {
        'profile': profile,
        'dates': [dates[i:i + 7] for i in range(0, len(dates), 7)],
        'now': now,
        'when': dt,
        'prev_month': dt.replace(day=1) - timedelta(days=1),
        'next_month': dt + timedelta(days=31)
    }
    return render(request, 'travel/profile/calendar.html', context)

# ------------------------------------------------------------------------------
# Admin utils below
# ------------------------------------------------------------------------------


def _entity_edit(request, entity, template='entities/edit.html'):
    if request.method == 'POST':
        form = forms.EditTravelEntityForm(request.POST, instance=entity)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(entity.get_absolute_url())
    else:
        form = forms.EditTravelEntityForm(instance=entity)

    return render_travel(request, template, {'entity': entity, 'form': form})


@superuser_required
def entity_edit(request, ref, code, aux=None):
    return _handle_entity(request, ref, code, aux, _entity_edit)


@superuser_required
def start_add_entity(request, template='entities/add/start.html'):
    abbr = request.GET.get('type')
    if abbr:
        if abbr == 'co':
            return http.HttpResponseRedirect(reverse('travel-entity-add-co'))

        co = request.GET.get('country')
        if co:
            return http.HttpResponseRedirect(
                reverse('travel-entity-add-by-co', args=(co, abbr))
            )

    return render_travel(request, template, {
        'types': travel.TravelEntityType.objects.exclude(abbr__in=['cn', 'co']),
        'countries': travel.TravelEntity.objects.countries()
    })


@superuser_required
def add_entity_co(request, template='entities/add/add.html'):
    entity_type = get_object_or_404(travel.TravelEntityType, abbr='co')
    if request.method == 'POST':
        form = forms.NewCountryForm(request.POST)
        if form.is_valid():
            entity = form.save(entity_type)
            return http.HttpResponseRedirect(entity.get_absolute_url())
    else:
        form = forms.NewCountryForm()

    return render_travel(request, template, {'form': form, 'entity_type': entity_type})


@superuser_required
def add_entity_by_co(request, code, abbr, template='entities/add/add.html'):
    entity_type = get_object_or_404(travel.TravelEntityType, abbr=abbr)
    country = travel.TravelEntity.objects.get(code=code, type__abbr='co')

    if request.method == 'POST':
        form = forms.NewTravelEntityForm(request.POST)
        if form.is_valid():
            entity = form.save(entity_type, country=country)
            return http.HttpResponseRedirect(entity.get_absolute_url())
    else:
        form = forms.NewTravelEntityForm()

    return render_travel(request, template, {'entity_type': entity_type, 'form': form})
