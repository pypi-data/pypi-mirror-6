from django.conf.urls import patterns, url

from homebanking.views import AccountList, CategoryList, EntryList

urlpatterns = patterns('',
    url(r'^categories/(?P<category_id>\d+)/', EntryList.as_view(), name='entry_list_from_category'),
    url(r'^categories/', CategoryList.as_view(), name='category_list'),
    url(r'^accounts/(?P<account_id>\d+)/', EntryList.as_view(), name='entry_list'),
    url(r'^accounts/', AccountList.as_view(), name='account_list'),
)
