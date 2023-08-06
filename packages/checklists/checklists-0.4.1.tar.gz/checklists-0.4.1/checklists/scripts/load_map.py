from checklists.models import Map, Activity, Age, Protocol, Sex, \
    set_current_user, clear_current_user

activities = (
    ('Birding', 'birding'),
)

ages = (
    ('Juvenile', 'juvenile'),
    ('Immature', 'immature'),
    ('Adult', 'adult'),
    ('Age Unknown', 'unknown')
)

protocols = (
    ('Incidental', 'incidental'),
    ('Stationary', 'stationary'),
    ('Traveling', 'traveling'),
)

sexes = (
    ('Male', 'male'),
    ('Female', 'female'),
    ('Sex Unknown', 'unknown')
)


def run():
    set_current_user('load_map')

    Map.objects.all().delete()

    for name, slug in activities:
        Map.objects.create(
            name=name, content_object=Activity.objects.get(slug=slug))

    for name, slug in ages:
        Map.objects.create(
            name=name, content_object=Age.objects.get(slug=slug))

    for name, slug in protocols:
        Map.objects.create(
            name=name, content_object=Protocol.objects.get(slug=slug))

    for name, slug in sexes:
        Map.objects.create(
            name=name, content_object=Sex.objects.get(slug=slug))

    clear_current_user()
