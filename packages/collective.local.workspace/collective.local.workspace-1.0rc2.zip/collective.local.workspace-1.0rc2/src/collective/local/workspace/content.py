from zope.interface.declarations import implements
from plone.dexterity.content import Container
from collective.local.workspace.interfaces import IWorkspace
from zope.traversing.interfaces import BeforeTraverseEvent
from zope.event import notify


class Workspace(Container):

    implements(IWorkspace)
    
    def __before_publishing_traverse__(self, obj, request):
        notify(BeforeTraverseEvent(self, request))
        super(Workspace, self).__before_publishing_traverse__(obj, request)