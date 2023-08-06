from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class MapFilter(admin.SimpleListFilter):

    title = _('content type')
    parameter_name = 'content_type__id'
    content_names = ('age', 'sex', 'activity', 'protocol', 'location')

    def lookups(self, request, model_admin):
        types = ContentType.objects.get(
            app_label='checklists', model__in=self.content_names)\
            .values_list('id', 'name', flat=True)
        return tuple([(pk, name.capitalize()) for pk, name in types])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(content_type_id=self.value())
        else:
            return queryset


