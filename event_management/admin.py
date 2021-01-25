from django.contrib import admin

from .models import Event, EventConfirmation, EventDocs


class EventDocsInline(admin.TabularInline):
    model = EventDocs

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False


class EventConfirmationInline(admin.TabularInline):
    model = EventConfirmation

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False


class EventAdmin(admin.ModelAdmin):
    inlines = [EventConfirmationInline, EventDocsInline]
    list_display = ('id', 'title', 'employee', 'place', 'date_time')


admin.site.register(Event, EventAdmin)
