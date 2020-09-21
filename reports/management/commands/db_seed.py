from django.core.management.base import BaseCommand, CommandError
from reports.models import JobGroup


class Command(BaseCommand):
    help = 'Seeds the database with Job Groups.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding JobGroup...')
        JobGroup.objects.all().delete()
        JobGroup.objects.create(name='A', hourly_rate=20)
        JobGroup.objects.create(name='B', hourly_rate=30)
        self.stdout.write(self.style.SUCCESS('Finished.'))
