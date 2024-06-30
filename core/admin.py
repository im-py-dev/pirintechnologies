from django.contrib import admin
from .models import CustomUser, Invoice

class InvoiceInline(admin.TabularInline):
    model = Invoice
    extra = 0

class CustomUserAdmin(admin.ModelAdmin):
    inlines = [InvoiceInline]

admin.site.register(CustomUser, CustomUserAdmin)
