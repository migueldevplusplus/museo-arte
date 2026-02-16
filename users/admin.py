from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, BuyerProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_buyer', 'is_employee', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_buyer', 'is_employee')}),
    )

class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'credit_card_number')

admin.site.register(User, CustomUserAdmin)
admin.site.register(BuyerProfile, BuyerProfileAdmin)
