from django.core.management.base import BaseCommand
from notifications.models import Trigger


SEED_TRIGGERS = [
    {
        'name': 'Login',
        'event_key': 'LOGIN',
        'description': 'Fired when a user successfully logs in.',
    },
    {
        'name': 'Logout',
        'event_key': 'LOGOUT',
        'description': 'Fired when a user logs out.',
    },
]


class Command(BaseCommand):
    help = 'Seed the database with the default LOGIN and LOGOUT triggers.'

    def handle(self, *args, **options):
        created_count = 0
        for data in SEED_TRIGGERS:
            obj, created = Trigger.objects.get_or_create(
                event_key=data['event_key'],
                defaults={'name': data['name'], 'description': data['description'], 'active': True},
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created trigger: {obj.event_key}"))
            else:
                self.stdout.write(f"  Trigger already exists: {obj.event_key}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. {created_count} trigger(s) created."))
