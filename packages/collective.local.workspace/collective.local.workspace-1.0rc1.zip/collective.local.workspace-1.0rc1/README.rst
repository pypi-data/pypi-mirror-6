==========================
collective.local.workspace
==========================

.. contents::

Introduction
============

This content type bundles all collective.local.* packages.

It adds a workspace dexterity content type where the new WorkspaceManager user role
can manage a groupware :

  - inviting new users (to the workspace only) - from collective.local.adduser
  - creating groups - from collective.local.adduser - from collective.local.addgroup

Workspace container have a "Members" tab to show all group members - from collective.local.userlisting -,
and an "Emailing" tab to send emails to workspace members - from collective.local.sendto.

A layer IWorkspaceLayer is set on request when you are in a workspace.

A `get_workspace` method in api module gives you the workspace root of any content.

String interpolators give you the title and the url of the workspace in an email
rule action.

Installation
============

Just add the egg to your buildout, and install the module.

Check that Workspace Manager role is given all the necessary permissions.
You can set them on workspace_workflow or at site root.