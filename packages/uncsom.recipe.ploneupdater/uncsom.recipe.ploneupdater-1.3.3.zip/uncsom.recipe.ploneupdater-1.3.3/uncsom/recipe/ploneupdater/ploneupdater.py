import sys
import transaction

from Testing import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.Portal import PloneSite
from zope.component.hooks import setSite
from optparse import OptionParser


class PloneUpdater(object):
    """Plone sites updater
    """

    def __init__(self, options, app):
        self.admin_user = options.admin_user
        self.profile = options.profile
        self.app = app

    def log(self, site, msg):
        print >> sys.stdout, "uncsom.recipe.ploneupdater", site, msg

    def authenticate(self):
        """wrap the request in admin security context
        """
        admin = self.app.acl_users.getUserById(self.admin_user)
        admin = admin.__of__(self.app.acl_users)
        newSecurityManager(None, admin)
        self.app = makerequest.makerequest(self.app)

    def pack_database(self):
        self.log('', "Starting to pack Database")
        self.app.Control_Panel.Database.manage_pack()
        self.log('', "Database packed")
        transaction.commit()

    def upgrade_plone(self, site):
        self.log(site, "Beginning Plone Upgrade")
        portal = self.app[site]
        portal.REQUEST.set('REQUEST_METHOD', 'POST')
        portal.portal_migration.upgrade()
        self.log(site, "Finished Plone Upgrade")
        transaction.commit()

    def upgrade_products(self, site):
        qi = self.app[site].portal_quickinstaller
        products = [p for p in qi.listInstalledProducts()]
        for product in products:
            product_id = product['id']
            info = qi.upgradeInfo(product_id)
            if product['installedVersion'] != qi.getProductVersion(product_id):
                if info['available']:
                    self.upgrade_profile(site, product_id)
                else:
                    self.reinstall_product(site, product_id)

    def reinstall_product(self, site, product):
        setSite(self.app[site])
        qi = self.app[site].portal_quickinstaller
        self.log(site, "Reinstalling: " + str(product))
        qi.reinstallProducts([product])
        self.log(site, "Reinstalled: " + str(product))
        transaction.commit()

    def upgrade_profile(self, site, product):
        setSite(self.app[site])
        qi = self.app[site].portal_quickinstaller
        self.log(site, "Upgrading: " + str(product))
        qi.upgradeProduct(product)
        self.log(site, "Upgraded: " + str(product))
        transaction.commit()

    def get_plone_sites(self):
        return [obj.id for obj in self.app.objectValues()
                if type(obj.aq_base) is PloneSite]

    def remove_invalid_imports(self, site):
        ps = self.app[site].portal_setup
        reg = ps.getImportStepRegistry()
        steps = reg.listStepMetadata()
        invalid_steps = [step['id'] for step in steps if step['invalid']]
        ps.manage_deleteImportSteps(invalid_steps)
        transaction.commit()

    def run_profile(self, site):
        ps = self.app[site].portal_setup
        self.log(site, "Running profile: " + self.profile)
        if not self.profile.startswith('profile-'):
            self.profile = "profile-%s" % self.profile
        ps.runAllImportStepsFromProfile(self.profile)
        self.log(site, "Ran profile " + self.profile)
        transaction.commit()

    def __call__(self):
        self.authenticate()
        plone_sites = self.get_plone_sites()
        if self.profile != '':
            for site in plone_sites:
                self.run_profile(site)
        else:
            self.pack_database()
            for site in plone_sites:
                self.remove_invalid_imports(site)
                self.upgrade_plone(site)
                self.upgrade_products(site)
        transaction.commit()

if __name__ == '__main__' and "app" in locals():
    parser = OptionParser()
    parser.add_option("-u", "--admin-user",
                      dest="admin_user", default="admin")
    parser.add_option("-c", dest="path")
    parser.add_option("-p", "--profile", dest="profile", default="")

    (options, args) = parser.parse_args()

    Updater = PloneUpdater(options, app)
    Updater()
