from ecreall.helpers.upgrade.interfaces import IUpgradeTool


def v2(context):
    tool = IUpgradeTool(context)
    tool.runProfile('collective.contact.facetednav.upgrades:v2')
