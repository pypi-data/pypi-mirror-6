
from interfaces import ICarouselPortlet
from portlet import CarouselPortletAssignment
from i18n import MessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets.portlets import base
from plone.app.portlets.browser import z3cformhelper

from z3c.form import field


class CarouselPortletRenderer(base.Renderer):
    render = ViewPageTemplateFile('portlet.pt')

    @property
    def title(self):
        return self.data.title

    @property
    def available(self):
        return self.data.collection_reference or \
            len(self.data.references) > 0

    @property
    def omit_border(self):
        return self.data.omit_border

    @property
    def rotate(self):
        return self.data.automatic_rotation

    def items(self):
        items = []

        collection = None
        if self.data.collection_reference:
            collection = self.data.collection_reference.to_object

        if collection:
            for brain in collection.results():
                items.append(brain.getObject())
        else:
            references = self.data.references
            for reference in references:
                items.append(reference.to_object)

        if hasattr(self.data, 'limit') and self.data.limit > 0:
            return items[:self.data.limit]

        return items


class CarouselPortletAddForm(z3cformhelper.AddForm):
    fields = field.Fields(ICarouselPortlet)
    label = _(u"Add carousel portlet")

    def create(self, data):
        return CarouselPortletAssignment(**data)


class CarouselPortletEditForm(z3cformhelper.EditForm):
    fields = field.Fields(ICarouselPortlet)
    label = _(u"Edit carousel portlet")
