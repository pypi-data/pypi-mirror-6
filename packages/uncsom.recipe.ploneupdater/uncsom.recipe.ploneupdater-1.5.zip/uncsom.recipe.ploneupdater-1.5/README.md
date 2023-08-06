uncsom.recipe.ploneupdater
==========================

Upgrade all of your Plone sites quickly!

- Code repository: https://github.com/ianderso/uncsom.recipe.ploneupdater

uncsom.recipe.ploneupdater is a buildout recipe that you can use to update
plone sites. It automatizes the following tasks:

 * pack database
 * reinstall products with the quickinstaller or GenericSetup Upgrade Steps
 * run Plone migration (portal_migration.upgrade)
 * clean up invalid GS steps
 * run GS profile
 * install product

uncsom.recipe.ploneupdater will create an updater tool in the buildout bin
directory.

This tool can be called with no options to reinstall, upgrade and clean up GS.

It can be called with the --profile option to run all steps from the given
profile in GS.

The --pack option will pack the database

If the --pack or --profile options are used, update will not be performed
unless the --update option is used. So if you want to pack, apply a profile,
and update use the --pack, --profile and --update options together.
