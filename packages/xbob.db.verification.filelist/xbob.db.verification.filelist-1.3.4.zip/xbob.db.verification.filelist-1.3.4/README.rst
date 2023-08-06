======================================
 Verification File Lists Database API
======================================

The Verification Filelist database API provides mechanisms to create
an API for a verification database and protocol, the user providing 
file lists.

You would normally not install this package unless you are maintaining it. What
you would do instead is to tie it in at the package you need to **use** it.
There are a few ways to achieve this:

1. You can add this package as a requirement at the ``setup.py`` for your own
   `satellite package
   <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_
   or to your Buildout ``.cfg`` file, if you prefer it that way. With this
   method, this package gets automatically downloaded and installed on your
   working environment, or

2. You can manually download and install this package using commands like
   ``easy_install`` or ``pip``.

The package is available in two different distribution formats:

1. You can download it from `PyPI <http://pypi.python.org/pypi/xbob.db.verification.filelist>`_, or

2. You can download it in its source form from `its git repository
   <https://github.com/bioidiap/xbob.db.verification.filelist>`_. When you download the
   version at the git repository, you will need to run a command to recreate
   the backend SQLite file required for its operation. This means that the
   database raw files must be installed somewhere in this case. With option
   ``a`` you can run in `dummy` mode and only download the raw data files for
   the database once you are happy with your setup.

You can mix and match points 1/2 and a/b above based on your requirements. Here
are some examples:

Modify your setup.py and download from PyPI
===========================================

That is the easiest. Edit your ``setup.py`` in your satellite package and add
the following entry in the ``install_requires`` section (note: ``...`` means
`whatever extra stuff you may have in-between`, don't put that on your
script)::

    install_requires=[
      ...
      "xbob.db.verification.filelist",
    ],

Proceed normally with your ``bootstrap/buildout`` steps and you should be all
set. That means you can now import the namespace ``xbob.db.verification.filelist`` into your scripts.

Modify your buildout.cfg and download from git
==============================================

You will need to add a dependence to `mr.developer
<http://pypi.python.org/pypi/mr.developer/>`_ to be able to install from our
git repositories. Your ``buildout.cfg`` file should contain the following
lines::

  [buildout]
  ...
  extensions = mr.developer
  auto-checkout = *
  eggs = bob
         ...
         xbob.db.verification.filelist

  [sources]
  xbob.db.verification.filelist = git https://github.com/bioidiap/xbob.db.verification.filelist.git
  ...
  
Creating file lists
===================

The initial step for using this package is to provide file lists specifying the world (train), development and evaluation set to be used by the biometric verification algorithm. The following files need to be created:

- **For training**:

1. *world file*, with default name ``train_world.lst``, and default subdirectory ``norm``. It is a 2-column file with format::
 
    filename client_id

2. two (optional) *world files*, with default names ``train_optional_world_1.lst`` and ``train_optional_world_2.lst``, and default subdirectory ``norm``. The format is the same as for the world file. These files are not needed for the most of the face recognition algorithms, hence, they need to be specified only if the algorithm uses them.

- **For enrollment**:

1. two *model files* for the development and evaluation set, with default name ``for_models.lst`` and default subdirectories ``dev`` and ``eval`` respectively. They are 3-column files with format::
  
    filename model_id client_id

- **For scoring**:

1.a. two *probe files* for the development and evaluation set, with default name ``for_probes.lst`` and default subdirectories ``dev`` and ``eval`` respectively. These files need to be provided only if the scoring is to be done exhaustively, meaning by creating a dense probe/model scoring matrix. They are 2-column files with format:: 
  
    filename client_id

1.b. two *score files* for the development and evaluation set, with default name ``for_scores.lst`` and default subdirectories ``dev`` and ``eval`` respectively.  These files need to be provided only if the scoring is to be done selectively, meaning by creating a sparse probe/model scoring matrix. They are 4-column files with format:: 

    filename model_id claimed_client_id client_id

2. two (optional) *files for t-score normalization* for the development and evaluation set, with default name ``for_tnorm.lst`` and default subdirectories ``dev`` and ``eval`` respectively. They are 3-column files with format::
  
    filename model_id client_id

3. two (optional) *files for z-score normalization* for the development and evaluation set, with default name ``for_znorm.lst`` and default subdirectories ``dev`` and ``eval`` respectively. They are 2-column files with format:: 

    filename client_id

.. note:: The verification queries will use either only the probe or only the score files, so only one of them is mandatory.
          In case both probe and score files are provided, the user should set the parameter ``use_dense_probe_file_list``, which specifies the files to consider, when creating the object of the ``Database`` class.

.. note:: If the database does not provide an evaluation set, the scoring files can be ommited.
          Similarly, if the user only define **for scoring** files and omit the remaining ones, the only valid queries will be scoring-related ones.

The summarized structure of the base directory (here denoted as ``basedir``) containing all the files should be like this::

  basedir -- norm -- train_world.lst
         |       |-- train_optional_world_1.lst
         |       |-- train_optional_world_2.lst
         |
         |-- dev -- for_models.lst
         |      |-- for_probes.lst 
         |      |-- for_scores.lst 
         |      |-- for_tnorm.lst 
         |      |-- for_znorm.lst 
         |
         |-- eval -- for_models.lst
                 |-- for_probes.lst 
                 |-- for_scores.lst 
                 |-- for_tnorm.lst 
                 |-- for_znorm.lst 
     
       
Protocols and file lists
========================

When you instantiate a database, you have to specify the base directory that contains the file lists.
If you have only a single protocol, you could specify the full path to the file lists described
above as follows::

  >>> db = xbob.db.verification.filelist.Database('basedir/protocol')

Next, you should query the data, WITHOUT specifying any protocol::
  
  >>> db.objects()

Alternatively, if you have more protocols, you could do the following::

  >>> db = xbob.db.verification.filelist.Database('basedir')
  >>> db.objects(protocol='protocol')

When a protocol is specified, it is appended to the base directory that contains the file lists.
This allows to use several protocols that are stored in the same base directory, without the need
to instantiate a new database. For instance, given two protocols 'P1' and 'P2' (with filelists
contained in 'basedir/P1' and 'basedir/P2', respectively), the following would work::

  >> db = xbob.db.verification.filelist.Database('basedir')
  >> db.objects(protocol='P1') # Get the objects for the protocol P1
  >> db.objects(protocol='P2') # Get the objects for the protocol P2

Note that if you use several protocols as explained above, the scoring part should be defined in
the same way for all the protocols, either by using ``for_probes.lst`` or ``for_scores.lst``.
This means that at the time of the database instantiation, it will be determined (or specified
using the ``use_dense_probe_file_list`` optional argument), whether the protocols should use
the content of ``for_probes.lst`` or ``for_scores.lst``. In particular, it is not possible to 
use a mixture of those for different protocols, once the database object has been created.
