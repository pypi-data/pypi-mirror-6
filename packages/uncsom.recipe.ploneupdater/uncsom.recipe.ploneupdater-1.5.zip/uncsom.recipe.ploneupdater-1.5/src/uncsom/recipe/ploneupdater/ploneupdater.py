import sys
import transaction

from Testing import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.Portal import PloneSite
from zope.component.hooks import setSite
from argparse import ArgumentParser


class PloneUpdater(object):
    """Plone sites updater
    """

    def __init__(self, options, app):
        self.admin_user = options.user
        self.profile = options.profile
        self.update = options.update
        self.pack = options.pack
        self.install = options.install
        self.app = app

    def log(self, site, msg):
        print >> sys.stdout, "uncsom.recipe.ploneupdater", site, msg

    def authenticate(self):
        """wrap the request in admin security context
        """
        admin = self.app.acl_users.getUserById(self.admin_user)
        if admin is None:
            self.log("", "admin user {admin} not found".format(
                admin=self.admin_user))
            return False
        admin = admin.__of__(self.app.acl_users)
        newSecurityManager(None, admin)
        self.app = makerequest.makerequest(self.app)
        return True

    def pack_database(self):
        self.log('', "Packing Database")
        self.app.Control_Panel.Database.manage_pack()
        transaction.commit()

    def upgrade_plone(self, site):
        self.log(site, "Upgrading Plone")
        portal = self.app[site]
        portal.REQUEST.set('REQUEST_METHOD', 'POST')
        portal.portal_migration.upgrade()
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
        transaction.commit()

    def upgrade_profile(self, site, product):
        setSite(self.app[site])
        qi = self.app[site].portal_quickinstaller
        self.log(site, "Upgrading: " + str(product))
        qi.upgradeProduct(product)
        transaction.commit()

    def get_plone_sites(self):
        return [obj.id for obj in self.app.objectValues()
                if type(obj.aq_base) is PloneSite]

    def remove_invalid_imports(self, site):
        self.log(site, "Removing Invalid Imports")
        ps = self.app[site].portal_setup
        reg = ps.getImportStepRegistry()
        steps = reg.listStepMetadata()
        invalid_steps = [step['id'] for step in steps if step['invalid']]
        ps.manage_deleteImportSteps(invalid_steps)
        transaction.commit()

    def run_profile(self, site):
        setSite(self.app[site])
        ps = self.app[site].portal_setup
        self.log(site, "Running profile: " + self.profile)
        if not self.profile.startswith('profile-'):
            self.profile = "profile-%s" % self.profile
        ps.runAllImportStepsFromProfile(self.profile)
        transaction.commit()

    def install_product(self, site):
        setSite(self.app[site])
        qi = self.app[site].portal_quickinstaller
        products = [p['id'] for p in qi.listInstallableProducts()]

        if self.install in products:
            self.log(site, "Installing Product: {product}".format(
                product=self.install))
            qi.installProducts(products=[self.install])
        else:
            self.log(site, "Product {product} unavailable for install".format(
                product=self.install))

    def __call__(self):
        if not self.authenticate():
            return

        if self.pack:
            self.pack_database()

        plone_sites = self.get_plone_sites()

        for site in plone_sites:
            if self.update or (not self.pack and self.profile == ''
                               and self.install == ''):
                self.remove_invalid_imports(site)
                self.upgrade_plone(site)
                self.upgrade_products(site)
            if self.profile != '':
                self.run_profile(site)
            if self.install != '':
                self.install_product(site)
        transaction.commit()

if __name__ == '__main__' and "app" in locals():
    parser = ArgumentParser()
    parser.add_argument("-a", "--admin-user",
                        dest="user", default="admin")
    parser.add_argument("-c", dest="path")
    parser.add_argument("-p", "--profile", dest="profile", default="")
    parser.add_argument("-u", "--update", dest="update", action='store_true')
    parser.add_argument("-z", "--pack", dest="pack", action='store_true')
    parser.add_argument("-i", "--install", dest="install", default='')

    options = parser.parse_args()

    Updater = PloneUpdater(options, app)
    Updater()
