import urllib

from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope.schema import Bool, Int, TextLine, URI

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from seantis.dir.eventsportlet import _


class IEventsPortlet(IPortletDataProvider):

    """A portlet which renders events.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    url = URI(
        title=_(u'The URL of the events directory'),
        required=True,
    )

    max_events = Int(
        title=_(u'Maximum number of displayed events'),
        required=True,
        default=5,
        min=1
    )

    do_filter = Bool(
        title=_(u'Filter events by category names'),
        required=False,
        default=False
    )

    cat1 = TextLine(
        title=_(u'Filter: 1st category name'),
        required=False,
        default=u''
    )

    cat2 = TextLine(
        title=_(u'Filter: 2nd category name'),
        required=False,
        default=u''
    )


class Assignment(base.Assignment):

    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IEventsPortlet)

    def __init__(self, url=u'', max_events=5,
                 do_filter=False, cat1=u'', cat2=u''):
        self.url = url
        self.max_events = max_events
        self.do_filter = do_filter
        self.cat1 = cat1
        self.cat2 = cat2

    # title = _(u'Events portlet')

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u'Events portlet')


class Renderer(base.Renderer):

    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """


    render = ViewPageTemplateFile('events.pt')

    def build_url(self, json=True):

        url = self.data.url.strip() + '?'
        if json:
            url += 'type=json&max=' + str(self.data.max_events) + '&'
        if self.data.do_filter:
            url += 'filter=true&'
            if self.data.cat1:
                cat = urllib.quote_plus(self.data.cat1.strip().encode('utf-8'))
                url += 'cat1=' + cat + '&'
            if self.data.cat2:
                cat = urllib.quote_plus(self.data.cat2.strip().encode('utf-8'))
                url += 'cat2=' + cat
        return url

    def export_url(self):
        return self.build_url()

    def events_url(self):
        return self.build_url(False)


class AddForm(base.AddForm):

    """Addd form

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added."""

    form_fields = form.Fields(IEventsPortlet)
    label = _(u"Add events portlet")
    description = _(u"A portlet which displays events.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):

    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display."""

    form_fields = form.Fields(IEventsPortlet)
    label = _(u"Edit events portlet")
    description = _(u"A portlet which displays events.")
