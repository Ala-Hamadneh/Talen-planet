from django.contrib import admin
from .models import LahzaTransaction, WithdrawalRequest

# Register your models here.

admin.site.register(LahzaTransaction)
admin.site.register(WithdrawalRequest)