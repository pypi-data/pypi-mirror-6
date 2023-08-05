from Acquisition import aq_parent, aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName


class View(BrowserView):
    """ View of a location
    """
    template = ViewPageTemplateFile('person.pt')

    def __call__(self):
        mtool = getToolByName(self.context, 'portal_membership')
        if not mtool.checkPermission(ModifyPortalContent, aq_inner(self.context)):
            self.request.RESPONSE.redirect(aq_parent(self.context).absolute_url())
            return u''
        return self.template()
