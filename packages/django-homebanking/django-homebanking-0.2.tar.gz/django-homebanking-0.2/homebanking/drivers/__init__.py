class HomeBankingBackend(object):
    def __init__(self, user_account):
        pass

    def get_accounts(self):
        raise NotImplemented()

    def get_agreements(self):
        raise NotImplemented()

    def get_entries_for_account(self, account, from_date=None, to_date=None):
        raise NotImplemented()
