from plone import api

from seantis.people.upgrades import (
    run_import_step_from_profile,
    upgrade_portal_type
)


def remove_faulty_type_name(context):
    run_import_step_from_profile('typeinfo', 'seantis.kantonsrat', 'default')
    api.portal.get_tool('portal_catalog').clearFindAndRebuild()


def upgrade_type_info(context):
    upgrade_portal_type(
        'seantis.kantonsrat.member', 'seantis.kantonsrat', 'default'
    )
