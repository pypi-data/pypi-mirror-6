from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from zope.configuration import xmlconfig


class FtwDownloadtokenLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.downloadtoken
        xmlconfig.file('configure.zcml', ftw.downloadtoken,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        #applyProfile(portal, 'ftw.downloadtoken:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


FTW_DOWNLOADTOKEN_FIXTURE = FtwDownloadtokenLayer()
FTW_DOWNLOADTOKEN_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_DOWNLOADTOKEN_FIXTURE,), name="FtwDownloadtoken:Integration")
FTW_DOWNLOADTOKEN_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FTW_DOWNLOADTOKEN_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name='FtwDownloadtoken:Functional')
