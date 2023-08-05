from __future__ import absolute_import

from homebanking import drivers
import sparnord

class SparNordBackend(drivers.HomeBankingBackend):
    connection_cache = {}

    def __init__(self, user_account):
        self.sn = sparnord.SparNord(username=user_account.username,
                                    password=user_account.password,
                                    user_id=user_account.remote_id)

    def get_agreements(self):
        return self.sn.get_agreements()

    def get_accounts(self, agreement):
        self.sn.agreement_id = agreement.remote_id
        return self.sn.get_accounts()

    def get_entries_for_account(self, account, from_date=None, to_date=None):
        self.sn.agreement_id = account.agreement.remote_id
        entries = list(self.sn.get_account_info_csv(str(account.accountnr),
                                                    from_date=from_date,
                                                    to_date=to_date))
        entries.reverse()
        for entry in entries:
            yield {'date': entry.entry_date,
                   'description': entry.description,
                   'amount': entry.amount,
                   'balance': entry.balance}

def get_backend(user_account):
    if not user_account in SparNordBackend.connection_cache:
        SparNordBackend.connection_cache[user_account] = SparNordBackend(user_account)
    return SparNordBackend.connection_cache[user_account]

backend_class = get_backend
