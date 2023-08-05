from Acquisition import aq_chain
from collective.local.workspace.interfaces import IWorkspace

def get_workspace(obj):
    for item in aq_chain(obj):
        if IWorkspace.providedBy(item):
            return item
    else:
        return None