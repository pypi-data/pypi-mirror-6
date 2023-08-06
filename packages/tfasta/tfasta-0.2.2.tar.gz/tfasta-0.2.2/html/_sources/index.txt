.. Created by phyles-quickstart.
   Add some items to the toctree.

tfasta 
======

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


Using Templates
~~~~~~~~~~~~~~~

Fasta files can be parsed according to one of several templates
that are written to the conventions of several common fasta
file sources, like swissprot, pdb, nr (the non-redundant database),
and nrblast.

The above example implicitly uses a template
called "``T_DEF``", which is the default template and yields
dictionaries with the keys ``name`` and ``sequence``.
The ``sequence`` key is universal to all templates.

The other templates (along with their keys) provided in tfasta are:
  
    - ``T_DEF`` - plain old fasta line
        - ``name`` - everything after the ">"
    - ``T_SWISS`` - fasta files from swissprot
        - ``gi_num`` - between first set of "|"s
        - ``accession`` - between 3rd and 4th "|"
        - ``description`` - after last "|"
    - ``T_PDB`` - the fasta file of the entire pdb
        - ``idCode`` - first four characters after ">"
        - ``chainID`` - any non-whitespace characters after first "_"
        - ``type`` - non-whitespace immediately following first ":"
        - ``numRes`` - numbers immediatly following first ":"
        - ``description`` - stripped characters after numRes
    - ``T_NR`` - the protein non-redundant database
        - ``gi`` - between first set of "|"s
        - ``accession`` - between 3rd and 4th "|"
        - ``description`` - stripped characters before brackets
        - ``source`` - stripped characters inside brackets
    - ``T_NRBLAST`` - fasta file produced from blast output of the nr
        - ``gi`` - between first set of "|"s
        - ``accession`` - between 3rd and 4th "|"


An example using the ``T_NR`` template follows.
The nr fasta database has records that look like this::

    >gi|5524211|gb|AAD44166.1| cytochrome b [Elephas maximus maximus]
    LCLYTHIGRNIYYGSYLYSETWNTGIMLLLITMATAFMGYVLPWGQMSFWGATVITNLFSAIPYIGTNLV
    EWIWGGFSVDKATLNRFFAFHFILPFTMVALAGVHLTFLHETGSNNPLGLTSDSDKIPFHPYYTIKDFLG
    LLILILLLLLLALLSPDMLGDPDNHMPADPLNTPLHIKPEWYFLFAYAILRSVPNKLGGVLALFLSIVIL
    GLMPFLHTSKHRSMMLRPLSQALFWTLTMDLLTLTWIGSQPVEYPYTIIGQMASILYFSIILAFLPIAGX
    IENY


This file, named "``cytb.fas``", may be parsed using the
tfasta ``T_NR`` template::

    >>> import tfasta
    >>> fast = tfasta.fasta_parser("cytb.fas",
    ...                            template=tfasta.T_NR)
    >>> f = fast.next()
    >>> print f['gi']
    5524211
    >>> print f['accession']
    AAD44166.1
    >>> print f['description']
    cytochrome b 
    >>> print f['source']
    Elephas maximus maximus
    >>> print f['sequence'][:60]
    LCLYTHIGRNIYYGSYLYSETWNTGIMLLLITMATAFMGYVLPWGQMSFWGATVITNLFS


Reading Big Fasta Files
~~~~~~~~~~~~~~~~~~~~~~~

Some fasta files may be several gigabytes in size. For this reason,
*fasta_parser()** reads fasta files incrementally, such that
only one sequence is read from the file at a time.

It is possible to force tfasta to read entire fasta files
at once by setting the ``greedy`` keyword to ``True``:

    fast = tfasta.fasta_parser("cytb.fas", template=tfasta.T_NR,
                                           greedy=True)

Preserving Gaps
~~~~~~~~~~~~~~~

Some sequences may have gaps ("-") such as those originating
from sequence alignments. To preserve gaps in the sequence 
set the ``dogaps`` keyword to ``True``::

    fast = tfasta.fasta_parser("alignment.fas", dogaps=True)


Creating Fasta
~~~~~~~~~~~~~~

Fasta formatted text can be created one at a time or in bunches.
The following examples creates fasta text from a name
and unformatted sequence::

    >>> import tfasta
    >>> name = "OVAX_CHICK GENE X PROTEIN N-Term"
    >>> seq = """
    ...       QIKDLLVSSSTDLDTTLVLVNAIYFKGMWK
    ...       afnaedtrempfhvtkqeskpvqmmcmnnsfnvatlpae
    ...       KMKILELPFASGDLSMLV
    ...       """
    >>> print tfasta.make_fasta(name, seq, width=50)
    >OVAX_CHICK GENE X PROTEIN N-Term
    QIKDLLVSSSTDLDTTLVLVNAIYFKGMWKAFNAEDTREMPFHVTKQESK
    PVQMMCMNNSFNVATLPAEKMKILELPFASGDLSMLV

The default width of a *make_fasta()* formatted
fasta sequence is 60. In this latter example, the
width is changed to 50 using the ``width`` keyword.

This next example creates fasta from an ordered dictionary,
available at https://pypi.python.org/pypi/ordereddict/
or built in to Python 2.7+::

    >>> import tfasta
    >>> from collections import OrderedDict  # python 2.7+
    >>> od = OrderedDict({ "First 10": "QIKDLLVSSS",
    ...                    "Second 10": "tdldttlvlv" })
    print tfasta.make_fasta_from_dict(od)
    >First 10
    QIKDLLVSSS
    >Second 10
    TDLDTTLVLV

Using an ordered dictionary is not required, but it does
ensure control over the order of the sequences in the fasta.
Any well-behaved "mapping object", like the built-in ``dict``
will work.

Note that *make_fasta()* *make_fasta_from_dict()*
both ignore all characters except letters and "-".


Creating Templates
~~~~~~~~~~~~~~~~~~

The creation of templates uses python regular expressions
to find fields in the first line of a sequence record
within a fasta file (the line that begins with ">").

Each field must be "saved" by the regular expression
by wrapping its sub-expression in parentheses. For
example the ``T_NRBLAST`` template regular expression is::

    ^>gi\|([^|]*)\|[^|]*\|([^|]*)\|.*$
           ~~~~~           ~~~~~ 

Here, the sub-expressions underscored by ``~`` characters
are saved by virtue of the surrounding parentheses.

The keys by which these saved fields are referred in the
dictionaries are given names, in the order that the
occure in the regular expression::

    regex = re.compile(r'^>gi\|([^|]*)\|[^|]*\|([^|]*)\|.*$')
    fields = ("gi", "accession")

Finally a template is created using the *FastaTemplate*
class::

    t_nrblast = FastaTemplate(regex, fields)

Here the template ``t_nrblast`` functions exactly as
the tfasta provided template ``T_NRBLAST``.

.. _`pip`: http://www.pip-installer.org/en/latest/
.. _`easy_install`: http://peak.telecommunity.com/DevCenter/EasyInstall

.. toctree::
   :maxdepth: 2
   :numbered:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
