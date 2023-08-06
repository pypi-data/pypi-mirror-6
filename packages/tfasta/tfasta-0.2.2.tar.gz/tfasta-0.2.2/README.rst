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
templates. Examples are given below.

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
  - Documentation: http://pythonhosted.org/radialx/
  - Repository: https://github.com/jcstroud/tfasta/


Usage
-----

Reading Fasta Files
~~~~~~~~~~~~~~~~~~~

Reading fasta files is performed with the *fasta_parser()* function.
The following text is the first 10 lines of the
file "``short-extended.fas``"::

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

Any fasta file may be parsed with a single command::

    >>> import tfasta
    >>> fast = tfasta.fasta_parser("short-extended.fas")
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

.. _`pip`: http://www.pip-installer.org/en/latest/
.. _`easy_install`: http://peak.telecommunity.com/DevCenter/EasyInstall
