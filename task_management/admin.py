from django.contrib import admin

from .models import Task, TaskConfirmation


class TaskConfirmationInline(admin.TabularInline):
    model = TaskConfirmation

    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_delete_permission(self, *args, **kwargs):
        return False


class TaskAdmin(admin.ModelAdmin):
    inlines = [TaskConfirmationInline]
    list_display = ('id', 'name', 'employee', 'due_time')


admin.site.register(Task, TaskAdmin)
