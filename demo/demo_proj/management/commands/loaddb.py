import time
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from travel.models import TravelEntity
from . import _data


def update_site():
    domain = "localhost:8000"
    Site.objects.filter(domain="example.com").update(domain=domain, name=domain)


class Command(BaseCommand):
    help = "Seed database with sample data."

    @transaction.atomic
    def handle(self, *args, **options):
        if TravelEntity.objects.exists():
            raise CommandError(
                "This command cannot be run when any entities exist, to guard "
                "against accidental use on production."
            )

        self.stdout.write("Seeding database...")
        update_site()

        for fn in [
            _data.load_users,
            _data.load_flags,
            _data.load_types,
            _data.load_classifications,
            _data.load_entities,
            _data.load_entityinfo,
            _data.load_bucketlists,
        ]:
            self.stdout.write(f'Loading {fn.__name__}...')
            started = time.time()
            fn()
            done = time.time() - started
            self.stdout.write(f'Done in {done} second(s).')

        self.stdout.write("Seeding done.")
