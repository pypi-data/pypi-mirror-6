from zope import schema
from zope.interface import implements
from zope.formlib import form
from Acquisition import aq_inner
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.article.teaser.interfaces import ITeaser

from raptus.person import _
from raptus.person.interfaces import IPerson


class IPersonPortlet(IPortletDataProvider):
    """A Portlet which can render persons
    """
    name = schema.TextLine(
            title=_(u"Person portlet title"),
            description=_(u"Add a title (optional)"),
            default=u"",
            required=False)

    name_fr = schema.TextLine(
            title=_(u"Person portlet title (FR)"),
            description=_(u"Add a title (optional)"),
            default=u"",
            required=False)

    person = schema.Tuple(title=u"Select person to display:",
                     description=_(u"Select from the list below the person you wish to display."),
                     default=(),
                     required=True,
                     value_type=schema.Choice(
                         vocabulary="raptus.person.person_factory")
                     )

class Assignment(base.Assignment):
    implements(IPersonPortlet)

    name_fr = u""

    def __init__(self, name=u"", name_fr=u"", person=()):
        self.name = name
        self.name_fr = name_fr
        self.person = person

    @property
    def title(self):
        return _(u"Person")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('person_portlet.pt')
    thumb_size = 'personportlet'

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return len(self._data()) > 0

    def persons(self):
        for brain in self._data():
            person = brain.getObject()

            teaser = ITeaser(person)
            image = teaser.getTeaser(self.thumb_size)
            yield dict(title = person.title,
                       img = image,
                       position = person.position,
                       email = person.email,
                       emailLink = 'mailto:%s' % person.email,
                       phone = person.phone)

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        results = []
        for brain in context.portal_catalog(UID = self.data.person):
            results.append(brain)

        return results

    def name(self):
        if self.request.get('LANGUAGE', 'de')[:2] == 'fr':
            return self.data.name_fr
        return self.data.name


class AddForm(base.AddForm):
    form_fields = form.Fields(IPersonPortlet)
    label = _(u"Add Person Portlet")
    description = _(u"This portlet displays persons.")

    def create(self, data):
        return Assignment(name=data.get('name', u""), name_fr=data.get('name_fr', u""), person=data.get('person', ()))


class EditForm(base.EditForm):
    form_fields = form.Fields(IPersonPortlet)
    label = _(u"Edit Person Portlet")
    description = _(u"This portlet displays persons.")
