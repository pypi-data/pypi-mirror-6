Introduction
============

This addon is a ckeditor_ integration for Plone.

.. contents::

How to install
==============

You can install it as any Plone addon. Please follow official documentation_.

Please use CKeditor_ for Plone > 4.

The code source can be found at https://github.com/collective/collective.ckeditor

Please report issues at https://github.com/collective/collective.ckeditor/issues

Dependencies
------------

* Plone >= 4
* collective.plonefinder_

Upgrades
========

If you come from collective.ckeditor < 3.6.12, you will have to launch an upgrade
step to 3612.  Go to ZMi-->portal_setup-->Upgrades, choose "collective.ckeditor:default"
profile and execute the upgrade step to 3612.

Development
===========

.. attention:: 
    ConfigurationError 

    If you try to run a Zope/Plone instance with a collective.ckeditor checkout,
    your instance will break with a ``ConfigurationError``::

      Directory .../browser/ckeditor does not exist.

After checking out collective.ckeditor sources, run the included buildout.

This installs and runs the ``copy_ckeditor_code`` script. 
It takes care of copying ckeditor code in the appropriate ``browser/ckeditor`` directory.

The ``browser/ckeditor`` directory makes ckeditor javascript code available to
the browser at::

  http://yourplonesite/++resource++ckeditor/

.. image:: https://secure.travis-ci.org/collective/collective.ckeditor.png
    :target: http://travis-ci.org/collective/collective.ckeditor

How to Release
--------------

Obviously, the ckeditor code also needs to be included in the released eggs.

``collective.ckeditor`` registers an entry point for ``zest.releaser`` that (if
called properly) takes care of copying the code when preparing the release.

However, in order to take advantage of the entry point, you have to use the
``bin/fullrelease`` locally installed by the development buildout instead of
a globally installed ``fullrelease``.

Only the local ``bin/fullrelease`` script can see the entry_point registered by
``collective.ckeditor``.


Credits
=======

Companies
---------

* `Makina Corpus <http://www.makina-corpus.com>`_  `Contact us <mailto:python@makina-corpus.org>`_
* `Ecreall <http://www.ecreall.com>`_
* `BubbleNet <http://bubblenet.be>`_
* `Hexagonit <http://www.hexagonit.fi>`_

Contributors
------------

- Kai Lautaportti <kai.lautaportti@hexagonit.fi>
- Giacomo Spettoli <giacomo.spettoli@gmail.com>
- Godefroid Chapelle <gotcha@bubblenet.be>
- Mathieu Le Marec - Pasquet <kiorky@cryptelium.net>
- Jean-Mat Grimaldi <jeanmat.grimaldi@gmail.com>
- Michael Smith <msmith64@naz.edu>
- Victor Fernandez de Alba <sneridagh@gmail.com>
- Kim Paulissen <spereverde@gmail.com>
- Jean-Michel FRANCOIS aka toutpt <toutpt@gmail.com>
- Gauthier Bastien <gauthier@imio.be>

.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
.. _FCKEditor: http://plone.org/fckeditor
.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
.. _ckeditor: http://ckeditor.com/
.. _collective.plonefinder: http://plone.org/products/collective.plonefinder
