from datetime import timedelta

from django import http
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
import vanilla

from . import models as travel
from . import forms
from . import utils


def split_code(code):
    return code.split('-', 1) if '-' in code else (code, None)


class TravelMixin:

    def get_template_names(self):
        template_names = (
            [self.template_name]
            if isinstance(self.template_name, str)
            else self.template_name
        )

        custom = [f'travel/custom/{base}' for base in template_names]
        return custom + [f'travel/{base}' for base in template_names]


class CalendarView(TravelMixin, vanilla.TemplateView):
    template_name = 'profile/calendar.html'

    def get_context_data(self, **kwargs):
        profile = get_object_or_404(
            travel.TravelProfile.objects.public().select_related('user'),
            user__username=self.kwargs['username']
        )
        user = profile.user
        when = self.request.GET.get('when')
        now = timezone.now()
        dt = now.replace(day=15)
        if when:
            year, month = [int(i) for i in when.split('-')]
            dt = dt.replace(year=year, month=month)

        dates = utils.calendar_dict(dt)
        for (name, abbr, arrival, emoji) in user.travellog_set.filter(
            arrival__month=dt.month
        ).values_list('entity__name', 'entity__type__abbr', 'arrival', 'entity__flag__emoji'):
            key = (arrival.month, arrival.day)
            if key in dates:
                dates[key].append([name, abbr, arrival, emoji])

        dates = list(dates.items())
        return super().get_context_data(
            profile=profile,
            dates=[dates[i:i + 7] for i in range(0, len(dates), 7)],
            now=now,
            when=dt,
            prev_month=dt.replace(day=1) - timedelta(days=1),
            next_month=dt + timedelta(days=31)
        )


class FlagGameView(TravelMixin, vanilla.TemplateView):
    template_name = 'flag-game.html'


class AllProfilesView(TravelMixin, vanilla.ListView):
    template_name = 'profile/all.html'
    model = travel.TravelProfile
    context_object_name = 'profiles'


class ProfileView(TravelMixin, vanilla.DetailView):
    template_name = 'profile/profile.html'
    context_object_name = 'profile'
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'

    def get_queryset(self):
        return travel.TravelProfile.objects.select_related('user')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            api_user_log_url=reverse('travel:user_log_api', args=[self.kwargs['username']])
        )


class LocaleView(TravelMixin, vanilla.ListView):
    template_name = 'entities/listing/{}.html'
    context_object_name = 'entities'

    @cached_property
    def entity_type(self):
        return get_object_or_404(travel.TravelEntityType, abbr=self.kwargs['ref'])

    def get_template_names(self):
        self.template_name = self.template_name.format(self.entity_type.abbr)
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        return super().get_context_data(type=self.entity_type, **kwargs)

    def get_queryset(self):
        return travel.TravelEntity.objects.type_related(self.entity_type)


class LanguagesView(TravelMixin, vanilla.ListView):
    template_name = 'languages.html'
    model = travel.TravelLanguage
    context_object_name = 'languages'


class LanguageView(TravelMixin, vanilla.DetailView):
    template_name = 'languages.html'
    model = travel.TravelLanguage
    context_object_name = 'language'


class BucketListsView(TravelMixin, vanilla.ListView):
    template_name = 'buckets/listing.html'
    context_object_name = 'bucket_lists'

    def get_queryset(self):
        return travel.TravelBucketList.objects.for_user(self.request.user)


class BucketListView(TravelMixin, vanilla.DetailView):
    template_name = 'buckets/detail.html'
    model = travel.TravelBucketList
    context_object_name = 'bucket_list'

    @cached_property
    def user(self):
        if 'username' in self.kwargs:
            return get_object_or_404(User, username=self.kwargs['username'])

        return self.request.user

    def get_context_data(self, **kwargs):
        done, entities = self.object.user_results(self.user)
        return super().get_context_data(
            entities=entities,
            stats={'total': len(entities), 'done': done},
            **kwargs
        )


class BucketListComparisonView(TravelMixin, vanilla.DetailView):
    template_name = 'buckets/compare.html'
    model = travel.TravelBucketList
    context_object_name = 'bucket_list'

    def get_context_data(self, **kwargs):
        usernames = self.kwargs['usernames'].split('/')
        entities = self.object.entities.select_related()
        results = [{
            'username': username,
            'entities': set(travel.TravelLog.objects.filter(
                user__username=username,
                entity__in=entities
            ).values_list('entity__id', flat=True))
        } for username in usernames]

        return super().get_context_data(entities=entities, results=results, **kwargs)


class LogEntryView(TravelMixin, vanilla.UpdateView):
    template_name = 'log-entry.html'
    model = travel.TravelLog
    context_object_name = 'entry'

    def get_queryset(self):
        return self.model.objects.filter(user__username=self.kwargs['username'])

    def form_valid(self, form):
        form.save(user=self.request.user)
        return http.HttpResponseRedirect(self.object.entity.get_absolute_url())

    def get_form(self, data=None, files=None, **kwargs):
        if self.request.user != self.object.user:
            raise http.Http404

        return forms.TravelLogForm(
            self.object.entity,
            data=data,
            files=files,
            instance=self.object
        )


class SearchView(TravelMixin, vanilla.TemplateView):
    template_name = 'search/search.html'

    def get_context_data(self, **kwargs):
        search_form = forms.SearchForm(self.request.GET)
        data = {'search_form': search_form}
        if search_form.is_valid():
            q = search_form.cleaned_data['search']
            by_type = search_form.cleaned_data['type']
            data.update(
                search=q,
                by_type=by_type,
                results=travel.TravelEntity.objects.search(q, by_type)
            )

        return super().get_context_data(**{**data, **kwargs})


class AdvancedSearchView(TravelMixin, LoginRequiredMixin, vanilla.TemplateView):
    template_name = 'search/advanced.html'

    def get_context_data(self, **kwargs):
        results = None
        search = self.request.GET.get('search', '').strip()
        if search:
            lines = [line.strip() for line in search.splitlines()]
            results = travel.TravelEntity.objects.advanced_search(lines)

        return super().get_context_data(results=results, search=search, **kwargs)


class EntityRelationshipsView(TravelMixin, vanilla.TemplateView):
    template_name = 'entities/listing/{}.html'

    @cached_property
    def relative_type(self):
        return get_object_or_404(travel.TravelEntityType, abbr=self.kwargs['rel'])

    @cached_property
    def entity_type(self):
        return get_object_or_404(travel.TravelEntityType, abbr=self.kwargs['ref'])

    def get_template_names(self):
        self.template_name = self.template_name.format(self.relative_type.abbr)
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        code, aux = split_code(self.kwargs['code'])
        entity = get_object_or_404(travel.TravelEntity.objects.find(
            self.entity_type.abbr,
            code,
            aux
        ))

        rel = self.relative_type
        return super().get_context_data(
            type=rel,
            entities=entity.related_by_type(rel),
            parent=entity,
            **kwargs
        )


class EntityView(TravelMixin, vanilla.DetailView):
    form_class = forms.TravelLogForm

    def get_form(self, data=None, files=None, **kwargs):
        cls = self.get_form_class()
        return cls(data=data, files=files, **kwargs)

    def get_object(self):
        ref = self.kwargs['ref']
        code, aux = split_code(self.kwargs['code'])
        return get_object_or_404(travel.TravelEntity.objects.find(ref, code, aux))

    def get_template_names(self):
        ref = self.kwargs['ref']
        self.template_name = [f'entities/detail/{ref}.html', 'entities/detail/base.html']
        return super().get_template_names()

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return http.HttpResponseNotAllowed(['get'])

        self.object = self.get_object()
        form = self.get_form(entity=self.object, data=self.request.POST)
        if form.is_valid():
            form.save(self.request.user)
            return http.HttpResponseRedirect(self.request.path)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(entity=self.object)
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        entity = self.object
        user = self.request.user
        history = user.travellog_set.filter(entity=entity) if user.is_authenticated else []

        return super().get_context_data(
            entity=entity,
            history=history,
            **kwargs
        )
