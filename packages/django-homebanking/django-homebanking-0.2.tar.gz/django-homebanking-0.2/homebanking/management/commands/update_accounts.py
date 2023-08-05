from django.core.management.base import BaseCommand, CommandError
from homebanking.models import UserAccount

class Command(BaseCommand):
    help = 'Polls all accounts for new data'

    def handle(self, *args, **options):
        user = UserAccount.get()
        user.update_all_accounts(*args)
