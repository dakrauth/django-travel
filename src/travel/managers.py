import operator
from functools import reduce
from django.db.models import Manager, Q, Count

__all__ = (
    'TravelProfileManager',
    'TravelBucketListManager',
    'TravelEntityManager',
    'TravelLogManager',
)


class TravelProfileManager(Manager):

    def public(self):
        return self.filter(
            access=self.model.Access.PUBLIC
        ).select_related('user').prefetch_related('user__travellog_set')

    def for_user(self, user):
        return self.get_or_create(user=user)[0]


class TravelBucketListManager(Manager):

    def for_user(self, user):
        q = Q(is_public=True)
        if user.is_authenticated:
            q |= Q(owner=user)

        return self.filter(q).order_by('title').prefetch_related('entities')

    def new_list(self, owner, title, entries, is_public=True, description=''):
        tdl = self.create(
            owner=owner,
            title=title,
            is_public=is_public,
            description=description
        )

        for e in entries:
            e.todos.create(todo=tdl)

        return tdl


class TravelEntityManager(Manager):
    search_select_related = [
        'type',
        'flag',
        'classification',
        'country',
        'country__flag',
        'country__type',
    ]
    base_select_related = [
        'type',
        'flag',
        'country',
        'country__flag',
        'country__type',
        'classification'
    ]
    state_select_related = [
        'state',
        'state__flag',
        'state__type',
        'state__country',
        'state__country__type'
    ]
    capital_select_related = ['capital', 'capital__type']
    common_select_related = base_select_related + state_select_related

    select_related_by_type = {
        'co': base_select_related + capital_select_related + ['continent'],
        'st': base_select_related + capital_select_related + ['country__capital'],
        'ct': common_select_related,
        'ap': common_select_related,
        'wh': common_select_related,
        'np': common_select_related,
        'lm': common_select_related,
    }

    @staticmethod
    def _search_q(term):
        return (
            Q(name__icontains=term) |
            Q(full_name__icontains=term) |
            Q(locality__icontains=term) |
            Q(code__iexact=term)
        )

    def search(self, term, type=None):
        term = (term or '').strip()
        if not term:
            return self.none()

        qs = self.filter(self._search_q(term))
        if type:
            qs = qs.filter(type__abbr=type)

        return qs.select_related(*self.search_select_related)

    def advanced_search(self, bits, type=None):
        bits = [b.strip() for b in bits]
        qq = reduce(operator.ior, [self._search_q(term) for term in bits])
        qs = self.filter(qq)
        if type:
            qs = qs.filter(type__abbr=type)

        return qs.select_related(*self.search_select_related)

    def countries(self):
        return self.filter(type__abbr='co').select_related(*self.base_select_related)

    def country(self, code):
        return self.select_related(*self.base_select_related).get(code=code, type__abbr='co')

    def country_dict(self):
        return dict([(e.code, e) for e in self.countries()])

    def find(self, abbr, code, aux):
        if aux:
            qs = self.filter(
                type__abbr=abbr,
                country__code=code,
                code=aux
            ).select_related(*self.base_select_related)
        else:
            qs = self.filter(
                type__abbr=abbr,
                code=code
            ).select_related(
                'continent',
                'continent__type',
                'capital',
                'capital__type'
            )

        return qs.select_related('type', 'flag')

    def type_related(self, ref, qs=None):
        ref_abbr = ref if isinstance(ref, str) else ref.abbr
        qs = qs or self.filter(type__abbr=ref_abbr)

        related = self.select_related_by_type.get(ref_abbr, self.base_select_related)
        qs = qs.select_related(*related)
        if ref_abbr == 'co':
            qs = qs.prefetch_related('entityinfo')

        return qs


class TravelLogManager(Manager):

    def checklist(self, user):
        return dict(
            self.filter(user=user).order_by('-arrival').values_list('entity').annotate(
                count=Count('entity')
            )
        )
