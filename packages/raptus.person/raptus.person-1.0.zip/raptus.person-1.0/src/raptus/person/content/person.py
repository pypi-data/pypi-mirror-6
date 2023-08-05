# -*- coding: utf-8 -*-
"""Definition of the Person content type
"""
from AccessControl import ClassSecurityInfo

from zope.interface import implements

from Products.validation import V_REQUIRED
from Products.Archetypes import atapi
from Products.Archetypes.Storage.annotation import AnnotationStorage
from Products.ATContentTypes.content import base, schemata
from Products.ATContentTypes.configuration import zconf

from raptus.article.core.content import article

try: # raptus.multilanguagefields
    from raptus.multilanguagefields.fields import StringField, TextField
    from raptus.multilanguagefields.widgets import StringWidget, RichWidget, ImageWidget
    try: # blob
        from raptus.multilanguagefields.fields import BlobImageField as ImageField
    except:
        from raptus.multilanguagefields.fields import ImageField
except:
    from Products.Archetypes.Field import StringField, TextField
    from Products.Archetypes.Widget import StringWidget, ImageWidget, RichWidget
    try: # blob
        from plone.app.blob.field import ImageField
    except:
        from Products.Archetypes.Field import ImageField


from raptus.person import interfaces
from raptus.person.config import PROJECTNAME
from raptus.person import _


PersonSchema = article.ArticleSchema.copy() + atapi.Schema((
    TextField(
        'position',
        required = False,
        searchable = True,
        accessor = 'Position',
        storage = AnnotationStorage(),
        validators = ('isTidyHtmlWithCleanup',),
        default_output_type = 'text/x-html-safe',
        widget = RichWidget(
            description = '',
            label = _(u'label_position', default=u'Position'),
            rows = 3,
        ),
    ),
    StringField(
        name = 'phone',
        required = False,
        accessor = 'Phone',
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u'Phone'),
            description = u'',
        ),
    ),
    StringField(
        name = 'email',
        required = False,
        accessor = 'Email',
        languageIndependent = True,
        storage = AnnotationStorage(),
        widget = StringWidget(
            label = _(u'Email'),
            description = u'',
        ),
    ),
))

PersonSchema['title'].storage = AnnotationStorage()
PersonSchema['description'].storage = AnnotationStorage()

for field in PersonSchema.keys():
    if not field in ('title', 'position', 'image', 'phone', 'email',):
        PersonSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

    if field in ('text',
                 'additional-text',
                 'external-reference',
                 'internal-reference',
                 'description',
                 'hideRightPortletslot',
                 'hideLeftPortletslot',
                 'image_as_background',
                 'allowDiscussion',
                 'excludeFromNav',
                 'nextPreviousEnabled',
                 'location',
                 'creators',
                 'contributors',
                 'rights',
                 'language',):
        PersonSchema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}

schemata.finalizeATCTSchema(PersonSchema, folderish=False, moveDiscussion=True)


class Person(article.Article):
    """A person"""
    implements(interfaces.IPerson)

    portal_type = "Person"
    schema = PersonSchema

    title = atapi.ATFieldProperty('title')
    position = atapi.ATFieldProperty('position')
    phone = atapi.ATFieldProperty('phone')
    email = atapi.ATFieldProperty('email')

    security = ClassSecurityInfo()

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        return False

atapi.registerType(Person, PROJECTNAME)
