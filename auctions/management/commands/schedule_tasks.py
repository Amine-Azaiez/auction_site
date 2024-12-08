from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json

class Command(BaseCommand):
    help = 'Schedule the periodic tasks'

    def handle(self, *args, **kwargs):
        # Create an interval schedule (runs every 1 minute)
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        # Create a periodic task to send winner emails
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Send winner emails',
            task='auction.tasks.check_and_send_winner_emails',
            args=json.dumps([]),
        )

        self.stdout.write(self.style.SUCCESS('Successfully scheduled tasks.'))
