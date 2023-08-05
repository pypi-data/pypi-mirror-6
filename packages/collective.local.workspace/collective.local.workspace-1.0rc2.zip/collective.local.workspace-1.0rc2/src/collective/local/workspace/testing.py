from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

from plone.testing import z2

import collective.local.workspace


COLLECTIVE_LOCAL_WORKSPACE = PloneWithPackageLayer(
    zcml_package=collective.local.workspace,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.local.workspace:testing',
    name="COLLECTIVE_LOCAL_WORKSPACE")

INTEGRATION = IntegrationTesting(
    bases=(COLLECTIVE_LOCAL_WORKSPACE, ),
    name="INTEGRATION")

FUNCTIONAL = FunctionalTesting(
    bases=(COLLECTIVE_LOCAL_WORKSPACE, ),
    name="FUNCTIONAL")

ACCEPTANCE = FunctionalTesting(
    bases=(COLLECTIVE_LOCAL_WORKSPACE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="ACCEPTANCE")
