from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from homebanking.models import Account, Entry, Category, Agreement
from homebanking import utils

class ProtectedListView(ListView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProtectedListView, self).dispatch(*args, **kwargs)

class AccountList(ProtectedListView):
    template_name = 'account_list.html'
    model = Account

class CategoryList(ProtectedListView):
    template_name = 'category_list.html'
    model = Category

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        context['months'] = utils.months_of_interest()
        return context

    def get_queryset(self):
        return Category.objects.order_by('name')

class EntryList(ProtectedListView):
    template_name = 'entry_list.html'
    model = Entry

    def get_context_data(self, **kwargs):
        context = super(EntryList, self).get_context_data(**kwargs)
        if hasattr(self, 'account'):
            context['account'] = self.account
        if hasattr(self, 'category'):
            context['category'] = self.category
        context['categories'] = Category.objects.order_by('name').all()
        return context

    def get_queryset(self):
        if 'account_id' in self.kwargs:
            self.account = get_object_or_404(Account, id=self.kwargs['account_id'])
            return Entry.objects.filter(account=self.account).order_by('-date', '-subindex')
        elif 'category_id' in self.kwargs:
            self.category = get_object_or_404(Category, id=self.kwargs['category_id'])
            return Entry.objects.filter(category=self.category).order_by('-date', '-subindex')

    def post(self, request, **kwargs):
        qs = self.get_queryset()
        for entry in qs:
            new_category_id = int(request.POST['category.%d' % entry.id])
            if entry.category_id != new_category_id:
                entry.category_id = new_category_id
                entry.save()
        return HttpResponseRedirect(request.path)
