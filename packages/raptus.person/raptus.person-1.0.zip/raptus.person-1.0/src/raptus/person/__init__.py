"""Main product initializer
"""

from Products.Archetypes import atapi
from Products.CMFCore import utils
from Products.CMFCore.permissions import setDefaultRoles

from raptus.person import config


from zope.i18nmessageid import MessageFactory
_ = MessageFactory('raptus.person')

def initialize(context):
    from content import person

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSION[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)
