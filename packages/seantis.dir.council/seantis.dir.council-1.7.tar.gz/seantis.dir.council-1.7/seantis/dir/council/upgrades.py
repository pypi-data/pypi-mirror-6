from Products.CMFCore.utils import getToolByName
from seantis.dir.base.upgrades import reset_images, add_behavior_to_item
from seantis.dir.council.directory import ICouncilDirectory
from seantis.dir.council.item import ICouncilDirectoryItem


def upgrade_to_1000(context):

    reset_images(context, (ICouncilDirectory, ICouncilDirectoryItem))
    add_behavior_to_item(
        context, 'seantis.dir.council', ICouncilDirectoryItem
    )


def upgrade_1000_to_1001(context):
    # add collective.geo.behaviour
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile(
        'profile-collective.geo.behaviour:default'
    )

    add_behavior_to_item(
        context, 'seantis.dir.council', ICouncilDirectoryItem
    )

    # update css and js
    getToolByName(context, 'portal_css').cookResources()
    getToolByName(context, 'portal_javascripts').cookResources()
