import autocomplete_light

import models

from utils import i18n_fieldnames


autocomplete_light.register(
    models.Location,
    search_fields=('name',),
    autocomplete_js_attributes={'placeholder': 'location name ..'}
)

autocomplete_light.register(
    models.Species,
    search_fields=('standard_name', 'scientific_name', 'common_name_en',),
    autocomplete_js_attributes={'placeholder': 'species name ..'}
)

autocomplete_light.register(
    models.Checklist,
    search_fields=('date', 'location__name',),
    autocomplete_js_attributes={'placeholder': 'checklist ..'}
)

autocomplete_light.register(
    models.Activity,
    search_fields=('name_en',),
    autocomplete_js_attributes={'placeholder': 'activity ..'}
)

autocomplete_light.register(
    models.Observer,
    search_fields=('name',),
    autocomplete_js_attributes={'placeholder': 'observer ..'}
)


class AutocompleteMap(autocomplete_light.AutocompleteGenericBase):
    choices = (
        models.Activity.objects.all(),
        models.Age.objects.all(),
        models.Protocol.objects.all(),
        models.Sex.objects.all(),
        models.Location.objects.all(),
    )

    search_fields = (
        (i18n_fieldnames('name')),
        (i18n_fieldnames('name')),
        (i18n_fieldnames('name')),
        (i18n_fieldnames('name')),
        ('name',),
    )


autocomplete_light.register(AutocompleteMap)
