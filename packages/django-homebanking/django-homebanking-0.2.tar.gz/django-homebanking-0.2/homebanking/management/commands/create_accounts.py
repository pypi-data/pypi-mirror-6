from django.core.management.base import BaseCommand, CommandError
from homebanking.models import UserAccount

class Command(BaseCommand):
    help = 'Creates accounts for all agreements'

    def handle(self, *args, **options):
        user = UserAccount.get()
        for agreement in user.agreement_set.all():
            agreement.crawl_accounts()
