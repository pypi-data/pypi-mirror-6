# coding=utf-8

from plone.app.testing import PloneSandboxLayer 
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.testing import z2


class RedominoOdtTransformsPolicy(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import redomino.odttransforms
        self.loadZCML(package=redomino.odttransforms)
        z2.installProduct(app, 'redomino.odttransforms')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'redomino.odttransforms:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'redomino.odttransforms')


REDOMINO_ODTTRANSFORMS_FIXTURE = RedominoOdtTransformsPolicy()
REDOMINO_ODTTRANSFORMS_INTEGRATION_TESTING = IntegrationTesting(
                  bases=(REDOMINO_ODTTRANSFORMS_FIXTURE,), 
                  name="RedominoOdtTransformsPolicy:Integration")
REDOMINO_ODTTRANSFORMS_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(REDOMINO_ODTTRANSFORMS_FIXTURE,), name="RedominoOdtTransformsPolicy:Functional")

