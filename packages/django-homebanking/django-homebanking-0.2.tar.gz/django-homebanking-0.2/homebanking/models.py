import re
from django.db import connection, models
from ordered_model.models import OrderedModel

class UserAccount(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    remote_id = models.CharField(max_length=200)

    def __unicode__(self):
        return self.username

    def crawl_and_create_agreements(self):
        backend = utils.get_backend()(self)

        agreements = backend.get_agreements()
        for agreement in agreements:
            Agreement.objects.get_or_create(owner=self, remote_id=agreement)

    def update_all_accounts(self, *args):
        for agreement in self.agreement_set.all():
            agreement.update_all_accounts(*args)

    @classmethod
    def get(cls):
        return cls.objects.all()[0]

class Agreement(models.Model):
    owner = models.ForeignKey(UserAccount)
    remote_id = models.CharField(max_length=200)

    def crawl_accounts(self):
        backend = utils.get_backend()(self.owner)
        accts = backend.get_accounts(self)
        for acct in accts:
            Account.objects.get_or_create(name=acct['name'],
                                          regnr=acct['regnr'],
                                          accountnr=acct['accountnr'],
                                          agreement=self)

    def update_all_accounts(self, *args):
        for account in self.account_set.all():
            account.update(*args)

    def __unicode__(self):
        return '%s: %s' % (self.owner, self.remote_id)


class Account(models.Model):
    name = models.CharField(max_length=50)
    regnr = models.IntegerField()
    accountnr = models.BigIntegerField()
    agreement = models.ForeignKey(Agreement)

    def __unicode__(self):
        return '%s-%s: %s' % (self.regnr, self.accountnr, self.name)

    def current_balance(self):
        entries = self.entry_set.order_by('-date', '-subindex')
        if len(entries):
            return entries[0].balance
        else:
            return None

    def update(self, from_date=None, to_date=None):
        backend = utils.get_backend()(self.agreement.owner)
        entries = backend.get_entries_for_account(self,
                                                  from_date=from_date,
                                                  to_date=to_date)

        last_seen_date = None
        subindex = {}
        for in_entry in entries:
            if in_entry['date'] in subindex:
                subindex[in_entry['date']] += 1
            else:
                subindex[in_entry['date']] = 0

            entry, created = Entry.objects.get_or_create(date=in_entry['date'],
                                                         text=in_entry['description'],
                                                         amount=in_entry['amount'],
                                                         balance=in_entry['balance'],
                                                         subindex=subindex[in_entry['date']],
                                                         account=self)
            if created:
                guessed_category = entry.guess_category()
                if guessed_category:
                    entry.category = guessed_category
                    entry.save()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    def monthly_summary(self):
        cursor = connection.cursor()
        if connection.vendor == 'sqlite':
            stmt = "SELECT django_date_trunc('month', homebanking_entry.date), sum(amount) FROM homebanking_entry WHERE category_id = %s GROUP BY django_date_trunc('month', homebanking_entry.date)"
        elif connection.vendor == 'mysql':
            stmt = "SELECT (DATE_FORMAT(`homebanking_entry`.`date`, '%%Y-%%m-01 00:00:00')), sum(amount) FROM homebanking_entry WHERE category_id = %s GROUP BY (DATE_FORMAT(`homebanking_entry`.`date`, '%%Y-%%m-01 00:00:00'))"
        cursor.execute(stmt, [self.id])
        months = utils.months_of_interest()
        retval = dict([(month, 0) for month in months])
        rows = cursor.fetchall()[:]
        for row in rows:
            date, total = row
            date = date[:7]
            if date not in months:
                continue
            retval[date] = total
        return retval

class Entry(models.Model):
    date = models.DateField()
    text = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    subindex = models.IntegerField(default=-1)
    account = models.ForeignKey(Account)
    category = models.ForeignKey(Category, default=1)

    def __unicode__(self):
        return self.text

    def guess_category(self):
        for matcher in CategoryMatcher.objects.all():
            if matcher.match(self):
                return matcher.category
        return None

class CategoryMatcher(OrderedModel):
    category = models.ForeignKey(Category, default=1)
    regex = models.CharField(max_length=200)

    class Meta(OrderedModel.Meta):
        pass

    def __unicode__(self):
        return '%s -> %s' % (self.regex, self.category)

    def match(self, entry):
        if re.search(self.regex, entry.text, re.IGNORECASE):
            return True
        return False

from homebanking import utils
