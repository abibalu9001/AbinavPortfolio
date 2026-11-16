from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'subject', 'created_at', 'is_read')

    search_fields = ('name', 'phone', 'subject', 'message')

    list_filter = ('is_read', 'created_at')

    ordering = ('-created_at',)