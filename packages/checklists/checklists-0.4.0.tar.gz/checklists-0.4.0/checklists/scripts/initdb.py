"""Script used to populate demo database with reference data."""

from django.core.management import call_command


def run(*args):
    call_command('runscript', 'load_activities')
    call_command('runscript', 'load_ages')
    call_command('runscript', 'load_directions')
    call_command('runscript', 'load_plumages')
    call_command('runscript', 'load_protocols')
    call_command('runscript', 'load_ranks')
    call_command('runscript', 'load_sexes')
    call_command('runscript', 'load_species_groups', script_args=args)
    call_command('runscript', 'load_species', script_args=args)

    call_command('runscript', 'load_map')
