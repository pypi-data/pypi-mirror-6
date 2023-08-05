from zope.component import adapts
from zope.i18nmessageid.message import MessageFactory

from plone.stringinterp.adapters import BaseSubstitution,MailAddressSubstitution
from plone.stringinterp.interfaces import IStringSubstitution

from collective.local.workspace import api, CLWMessageFactory as _


PMF = MessageFactory('plone')

class WorkspaceTitleSubstitution(BaseSubstitution):
    adapts(IStringSubstitution)

    category = PMF(u'All Content')
    description = _(u'Workspace title')

    def safe_call(self):
        workspace = api.get_workspace(self.context)
        if workspace:
            return workspace.title_or_id()
        else:
            return ""


class WorkspaceURLSubstitution(BaseSubstitution):
    adapts(IStringSubstitution)

    category = PMF(u'All Content')
    description = _(u'Workspace URL')

    def safe_call(self):
        workspace = api.get_workspace(self.context)
        if workspace:
            return workspace.absolute_url()
        else:
            return ""


class WorkspaceManagerEmailSubstitution(MailAddressSubstitution):

    category = PMF(u'E-Mail Addresses')
    description = _(u'Workspace managers')

    def safe_call(self):
        return self.getEmailsForRole('WorkspaceManager')
