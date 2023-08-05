import transaction

# from plone.testing import z2
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from Testing import ZopeTestCase as ztc
from OFS.Folder import Folder


class Fixture(PloneSandboxLayer):

    default_bases = (PLONE_FIXTURE, )

    class Session(dict):

        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):

        import seantis.dir.eventsportlet
        self.loadZCML(package=seantis.dir.eventsportlet)

        app.REQUEST['SESSION'] = self.Session()

        if not hasattr(app, 'temp_folder'):
            app._setObject('temp_folder', Folder('temp_folder'))
            transaction.commit()
            ztc.utils.setupCoreSessions(app)

    def tearDownZope(self, app):
        pass

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'seantis.dir.eventsportlet:default')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='seantis.dir.eventsportlet:Integration'
)
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='seantis.dir.eventsportlet:Functional'
)
