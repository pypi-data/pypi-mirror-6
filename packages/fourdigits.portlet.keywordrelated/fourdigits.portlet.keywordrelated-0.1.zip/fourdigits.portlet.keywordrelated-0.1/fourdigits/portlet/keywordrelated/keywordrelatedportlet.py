from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from fourdigits.portlet.keywordrelated import \
    KeywordRelatedPortletMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.interface import implements


class IKeywordRelatedPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    nr_items = schema.Int(
        title=_(u"Number of items"),
        description=_(u"Number of items to show in the portlet"),
        required=True,
        default=5,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IKeywordRelatedPortlet)

    def __init__(self, nr_items=5):
        self.nr_items = nr_items

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Tag-based related items"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('keywordrelatedportlet.pt')

    def items(self):
        """Query the catalog for items with the same tags as the context.
        """
        context = self.context
        nr_items = self.data.nr_items
        catalog = getToolByName(context, 'portal_catalog')
        keywords = context.Subject()
        query = {
            'Subject': keywords,
            'sort_limit': nr_items + 1,  # account for context
        }
        brains = catalog.searchResults(**query)
        brains = brains[:nr_items + 1]
        # filter the current context
        brains = [b for b in brains if b.getURL() != context.absolute_url()]
        return brains[:nr_items]

    def show_footer(self):
        """TODO: make this selectable in the portlet add/edit form
        """
        return False


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IKeywordRelatedPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IKeywordRelatedPortlet)
