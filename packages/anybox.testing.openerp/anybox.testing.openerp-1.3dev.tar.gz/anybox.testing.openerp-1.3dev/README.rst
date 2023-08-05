anybox.testing.openerp
======================

This distribution is intended to provide testing tools and especially
unit test base classes to enhance those that come builtin with OpenERP
(version >= 7)

Currently, it features these base test classes:

  - SharedSetupTransactionCase_
  - TransactionCase_

How to install
~~~~~~~~~~~~~~

in general, all you need is to make ``anybox.testing.openerp``
importable from the python executable that is to run the tests.

Users of the `Buildout recipe
<http://pypi.python.org/pypi/anybox.recipe.openerp>`_ just have to add
``anybox.testing.openerp`` to their lists of eggs, preferably in a
buildout configuration intended for developers::

   [buildout]
   extends = buildout.cfg

   [openerp]
   eggs += anybox.testing.openerp

(assuming of course that the part installing OpenERP is named
``openerp``)

.. _SharedSetupTransactionCase:

SharedSetupTransactionCase
~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    from anybox.testing.openerp import SharedSetupTransactionCase

This class allows to mutualize at the test class level
test data preparations, so that it does not have to be executed again
and again. It relies internally on PostgreSQL savepoints to do so.

The simplest usage is to load some XML files::

    class MyTestCase(SharedSetupTransactionCase):

        _data_files = ('employees.xml',
                       'products.xml')

        _module_ns = 'tests'

Paths are relative to the directory holding the test python modules
(typically ``tests``) ; ``_module_ns`` is meant to specify in which
(existing or not) OpenERP module's namespace the data is to be
inserted. This is necessary, e.g., for cross-referencing in
``one2many`` values.

You may also subclass the ``initTestData`` class
method to insert your own preparations::

        @classmethod
        def initTestData(cls):
            # if you need them XML data files:
            super(MyTestCase, cls).initTestData()
            cls.initLotsOfStuff()

Finally, this class comes equipped with the `utility and assertion methods`_.


.. _TransactionCase:

TransactionCase
~~~~~~~~~~~~~~~
::

    from anybox.testing.openerp import TransactionCase

This is a simple subclass of ``openerp.tests.common.TransactionCase``
featuring:

* the `utility and assertion methods`_
* (in Python >= 2.7 context only) a more robust ``tearDown`` that
  protects against exceptions during ``setUp``.

  Such exceptions have been witnessed to cause PostgreSQL to deadlock,
  which is a major source of developper headaches and of loss of time.

.. _utility and assertion methods:

Utility and assertion methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Both ``TransactionCase`` and ``SharedSetupTransactionCase`` feature
additional helper methods. These are

 - ``assertRecord()``
 - ``searchUnique()``
 - ``readUnique()``

They allow for more direct writing and more readability.
Check the docstrings for more details. This documentation should get
Sphinxed soon.

Why a separate package
~~~~~~~~~~~~~~~~~~~~~~

We (Anybox) are very open to direct inclusion in OpenERP core, and are ready
to submit this as a proper merge request (hence involving a
bit more of our own resources than has already been done).

That being said, the reasons for a separate package are:

 - we don't want to depend on actual inclusion in the core for
   our projects
 - we need this to be available in v7 branch (current stable)
 - we might want or need to stay ahead of whichever inclusions can occur in
   the future ; using a published version is more convenient for us
   than keeping track in our private VCSes.

Why not an addon ?
~~~~~~~~~~~~~~~~~~

Do you *really* want to see a module for unit testing to appear in
your modules list ?

Authors
~~~~~~~

 - Georges Racinet (@gracinet on identi.ca & twitter), Anybox SAS,
   http://anybox.fr, GPG: 0x33AB0A35 on public key servers.

Contributing
~~~~~~~~~~~~

We are very open to contributions. Don't hesitate to fork and issue
pull requests on the `BitBucket repository
<http://bitbucket.org/anybox/anybox.testing.openerp>`_




