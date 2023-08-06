Supported options
=================

The recipe supports the following option:

admin-user
    The name of the zope instance admin. The same as defined in the ``user``
    option of your zope instance. Defaults to 'admin'


Example usage
=============

We'll start by creating a buildout that uses the recipe. Let's create a freash
zope instance::

    >>> write(sample_buildout, 'buildout.cfg', """
    ... [buildout]
    ... parts =
    ...     instance
    ...     update-plone
    ... index = http://pypi.python.org/simple
    ... find-links =
    ...     http://download.zope.org/distribution/
    ...     http://effbot.org/downloads
    ... eggs =
    ...     Plone
    ...     Pillow
    ...
    ... [instance]
    ... recipe = plone.recipe.zope2instance
    ... user = admin:admin
    ... eggs = ${buildout:eggs}
    ...
    ... [update-plone]
    ... recipe = collective.recipe.updateplone
    ... admin-user = admin
    ... """)
