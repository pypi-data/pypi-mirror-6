from zope.interface import alsoProvides
from collective.local.workspace.interfaces import IWorkspaceLayer


def set_workspace_layer(workspace, event):
    if hasattr(workspace, 'REQUEST'):
        alsoProvides(workspace.REQUEST, IWorkspaceLayer)