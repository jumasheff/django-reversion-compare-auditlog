import json
from django.contrib import admin
from django import forms
from django.forms import Widget

from django.utils.safestring import mark_safe
from reversion.models import Revision, Version, VERSION_ADD
from django.utils.translation import ugettext_lazy as _
from reversion_compare.helpers import html_diff, EFFICIENCY

Version._meta.verbose_name = _("Reversion")
Version._meta.verbose_name_plural = _("Reversions")


class DateRangeFilter(admin.DateFieldListFilter):
    title = _('Date range')
    template = 'admin/filters/date_range.html'

    def queryset(self, request, queryset):
        if self.used_parameters.has_key(self.lookup_kwarg_since):
            self.start = self.used_parameters[self.lookup_kwarg_since]
        if self.used_parameters.has_key(self.lookup_kwarg_until):
            self.end = self.used_parameters[self.lookup_kwarg_until]
        return super(DateRangeFilter, self).queryset(request, queryset)


class HtmlReadonly(Widget):
    def render(self, name, value, attrs=None):
        current_obj = Version.objects.filter(serialized_data=value)[0]
        html = _render_diff(current_obj)
        return mark_safe(html)


class AuditLogForm(forms.ModelForm):
    class Meta:
        model = Version
        widgets = {
            'serialized_data': HtmlReadonly(),
        }


class AuditLogAdmin(admin.ModelAdmin):

    list_filter = [('revision__date_created', DateRangeFilter), 'content_type']
    search_fields = ['revision__user__username']
    list_display = ['get_date_created', 'get_user', 'content_type', 'get_diff', 'object_id', 'object', 'type']
    form = AuditLogForm

    class Meta:
        model = Version

    def get_date_created(self, obj):
        return '%s' % obj.revision.date_created

    get_date_created.short_description = _('Date created')

    def get_user(self, obj):
        return '%s' % obj.revision.user

    get_user.short_description = _('User')

    def get_diff(self, obj):
        result = ""
        if _is_modification(obj.type):
            result = _render_diff(obj)
        return result

    get_diff.short_description = _("Diff")
    get_diff.allow_tags = True

    # def has_add_permission(self, request):
    #     return False
    def lookup_allowed(self, lookup, value):
        return True

def _is_modification(action_type):
    return action_type != VERSION_ADD


def _render_diff(obj):
    result = ""
    try:
        diff = _get_diff_from_objects(obj)
        for key in diff:
            result += "<p>%s</p>" % key
            result += "<p>" + html_diff(diff[key]['prev'], diff[key]['current'], EFFICIENCY) + "</p>"
    except IndexError:
        result = ""
    except ValueError:
        result = ""
    return result


def _get_diff_from_objects(obj):
    prev_obj = \
        Version.objects.filter(object_id_int=obj.object_id_int, type=obj.type, content_type=obj.content_type).exclude(
            serialized_data=obj.serialized_data).order_by(
            '-revision__date_created')[0]
    prev_version = json.loads(prev_obj.serialized_data)
    current_version = json.loads(obj.serialized_data)
    diff = _compare_objects(current_version[0]['fields'], prev_version[0]['fields'])
    return diff


def _compare_objects(current_version, prev_version):
    result = {}
    for key in current_version:
        if prev_version.has_key(key) and current_version[key] != prev_version[key]:
            result[key] = {}
            result[key]['current'] = current_version[key]
            result[key]['prev'] = prev_version[key]
    return result


admin.site.register(Version, AuditLogAdmin)
