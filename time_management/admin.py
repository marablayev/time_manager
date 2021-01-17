
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.postgres.fields import DateRangeField
from django.contrib.postgres.forms.ranges import RangeWidget

from time_management.models import EmployeeActivity, Holiday, HolidayMoved
from time_management.utils import write_to_xlxs


def write_to_xlxs_action(modeladmin, request, queryset):

    return write_to_xlxs()

write_to_xlxs_action.short_description = 'Экспорт данных'


class EmployeeActivityAdmin(admin.ModelAdmin):
    list_display = ('date', 'employee')
    readonly_fields = ('date', )
    actions = (write_to_xlxs_action, )

    def has_add_permission(self, request, obj=None):
        return False

    # def changelist_view(self, request, extra_context=None):
    #     """Override change_weights_action to accept without selecting instances"""
    #     if 'action' in request.POST and request.POST['action'] == 'write_to_xlxs':
    #         post = request.POST.copy()
    #         for param in EmployeeActivity.objects.all()[:1]:
    #             post.update({admin.ACTION_CHECKBOX_NAME: str(param.id)})
    #         request._set_post(post)
    #     return super(EmployeeActivityAdmin, self).changelist_view(request, extra_context)


class HolidayMovedInline(admin.TabularInline):
    model = HolidayMoved
    extra = 1


class HolidayAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dates')
    inlines = (HolidayMovedInline, )
    formfield_overrides = {
        DateRangeField: {'widget': RangeWidget(AdminDateWidget())},
    }


admin.site.register(Holiday, HolidayAdmin)
admin.site.register(EmployeeActivity, EmployeeActivityAdmin)
