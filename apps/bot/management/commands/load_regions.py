from django.core.management.base import BaseCommand
from utils.regions import regions, districts
from apps.bot.models import Region, City


class Command(BaseCommand):
    help = 'Load regions from json'

    def handle(self, *args, **options):
        for i in regions:
            Region.objects.get_or_create(title=i[1], id=i[0])
        for i in districts:
            City.objects.get_or_create(title=i[2], id=i[0], region_id=i[1])
        self.stdout.write(self.style.SUCCESS('Regions loaded successfully'))
