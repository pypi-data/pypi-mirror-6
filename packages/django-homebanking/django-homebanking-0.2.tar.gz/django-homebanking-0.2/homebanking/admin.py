from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from homebanking.models import Account, Entry, Category, CategoryMatcher, UserAccount, Agreement

admin.site.register(Account)
admin.site.register(Entry)
admin.site.register(Category)
admin.site.register(UserAccount)
admin.site.register(Agreement)

class CategoryMatcherAdmin(OrderedModelAdmin):
    list_display = ('regex', 'category', 'move_up_down_links')

admin.site.register(CategoryMatcher, CategoryMatcherAdmin)
