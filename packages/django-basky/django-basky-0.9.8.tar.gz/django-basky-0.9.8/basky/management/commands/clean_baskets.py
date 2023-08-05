from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from basky.models import Basket
from basky import settings


class Command(BaseCommand):
    """
    Deletes all the baskets older than BASKY_AGE
    """

    def handle(self, *args, **options):
        # calculate the age
        age = datetime.now() - timedelta(seconds=settings.BASKY_AGE)

        # get the baskets
        baskets = Basket.objects.filter(last_modified__lt=age)
        baskets.delete()
