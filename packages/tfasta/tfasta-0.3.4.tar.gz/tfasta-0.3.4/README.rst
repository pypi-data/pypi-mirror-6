========
 tfasta 
========

Introduction
------------

The tfasta python package simplifies working
with fasta, providing functionality
for both reading and writing fasta files.
The "t" in "tfasta" represents
"templated", which means that fasta parsing is
performed according to pre-defined or user-defined
templates::

    >>> from tfasta import fasta_parser, T_NR
    >>> fast = fasta_parser("cytb.fas", template=T_NR)
    >>> f = fast.next()
    >>> print f['gi']
    5524211
    >>> print f['accession']
    AAD44166.1
    >>> print f['sequence'][:60]
    LCLYTHIGRNIYYGSYLYSETWNTGIMLLLITMATAFMGYVLPWGQMSFWGATVITNLFS

This example parses records that follow the conventions
of the NCBI non-redundant database (nr).

More examples are given in the `tfasta full documentation`_.


Installation
------------

Install tfasta with `pip`_ (recommended) or `easy_install`_::

  sudo pip install tfasta

Optionally, download the source files from
http://pypi.python.org/pypi/tfasta/
and run the following commands in the source directory::

  python setup.py build
  sudo python setup.py install

Home Page & Repository
----------------------

  - Home Page: http://pypi.python.org/pypi/tfasta/
  - Documentation: http://pythonhosted.org/tfasta/
  - Repository: https://github.com/jcstroud/tfasta/


Basic Usage
-----------

Reading Fasta Files
~~~~~~~~~~~~~~~~~~~

Reading fasta files is performed with the *fasta_parser()* function.
The following text is the first 2 records from a file
called "``short-extended.fas``"::

    >gi|32033604|ref|ZP_00133915.1|
    ATGQVIGTFTVRNDNGLHARPSAVLVQTLKPFAAKVTVENLDRGTAPANAKSTMKVVALG
    ASQAHRLRFVAEGEDAQQAIEALAKAFVEGLGESVSFVPAVEDTIEGAAQPQAVESAKNF
    ANPTASEPTVEGQVEGTFVIQNEHGLHARPSAVLVNEVKKYNATIVVQNLDRNTQLVSAK
    SLMKIVALGVVKGHRLHFVATGDDAQKAIDGIGEAIAAGLGE
    >gi|1573424|gb|AAC22107.1|
    VEGAVVGTFTIRNEHGLHARPSANLVNEVKKFTSKITMQNLTRESEVVSAKSLMKIVALG
    VTQGHRLRFVAEGEDAKQAIESLGKAIANGLGENVSAVPPSEPDTIEIMGDQIHTPAVTE
    DDNLPANAIEAVFVIKNEQGLHARPSAILVNEVKKYNASVAVQNLDRNSQLVSAKSLMKI
    VALGVVKGTRLRFVATGEEAQQAIDGIGAVIESGLGE

Like any other fasta file, ``short-extended.fas`` may be parsed
with a single command::

    fast = fasta_parser(file_name)

For example::

    >>> from tfasta import fasta_parser
    >>> fast = fasta_parser("short-extended.fas")
    >>> f = fast.next()
    >>> print f['name']
    gi|32033604|ref|ZP_00133915.1|
    >>> print f['sequence'][:60]
    ATGQVIGTFTVRNDNGLHARPSAVLVQTLKPFAAKVTVENLDRGTAPANAKSTMKVVALG
    f = fast.next()
    print f['name']
    gi|1573424|gb|AAC22107.1|

In this example, the *fasta_parser()* function returns
an iterator of dictionaries ("``fast``") with two
keys: ``name`` and ``sequence``.
The ``name`` key corresponds to all of the plain text after
the fasta format marker "``>``" that marks a new sequence.


Iteration
~~~~~~~~~

The iterator returned by the *fasta_parser()* function
may serve in ``for`` loops::

    
    >>> from tfasta import fasta_parser
    >>> for f in fasta_parser("short-extended.fas"):
    ...   print f['name']
    gi|32033604|ref|ZP_00133915.1|
    gi|1573424|gb|AAC22107.1|
    [...]


Other Usage
-----------

See the `tfasta full documentation`_ for more sophisticated
reading and writing of fasta.


.. _`pip`: http://www.pip-installer.org/en/latest/
.. _`easy_install`: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _`tfasta full documentation`: http://pythonhosted.org/tfasta/
