from django.contrib import admin

from account.models import Account

# Register your models here.
@admin.register(Account)
class AccountAdminModel(admin.ModelAdmin):
    list_display = ("pk","user","user_type","name","department")