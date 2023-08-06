"""
This is automatically generated documentation and should
not be relied on for the API. Please
see the official documentation at http://pythonhosted.org/tfasta/.

The only things that should be used externally from this module are
I{TEMPLATES}, a C{dict} of C{FastaTemplate} instances, or
C{FastaTemplate} itself. A dictionary is
used so that templates can be selected dynamically at run-time.

Template types registered in I{TEMPLATES} are:

    - B{I{default}} - plain old fasta line
         - B{name} - everything after the ">"
    - B{I{swissprot}} - fasta files from swissprot
         - B{gi_num} - between first set of "|"s
         - B{accession} - between 3rd and 4th "|"
         - B{description} - after last "|"
    - B{I{pdb}} - the fasta file of the entire pdb
         - B{idCode} - first four characters after ">"
         - B{chainID} - any non-whitespace characters after first "_"
         - B{type} - non-whitespace immediately following first ":"
         - B{numRes} - numbers immediatly following first ":"
         - B{description} - stripped characters after I{numRes}
    - B{I{nr}} - the protein non-redundant database
         - B{gi} - between first set of "|"s
         - B{accession} - between 3rd and 4th "|"
         - B{description} - stripped characters before brackets
         - B{source} - stripped characters inside brackets
    - B{I{nrblast}} - fasta file produced from blast output of the nr
         - B{gi} - between first set of "|"s
         - B{accession} - between 3rd and 4th "|"

@var TEMPLATES: a C{dict} holding instances of C{FastaTemplate}
                used for parsing
"""

import re

#######################################################################
# FastaTemplate
#######################################################################
class FastaTemplate:
  """
  This class encapsulates template information for parsing fasta
  files. Wraps a regular expression (I{regex}) used to parse the first
  line of a fasta record and also a C{tuple} of C{str}ings (I{fields})
  that name the information contained in the first line of the fasta
  record.

  @type regex: _sre.SRE_Pattern
  @type fields: tuple
  """

  #####################################################################
  # __init__()
  #####################################################################
  def __init__(self, regex, fields):
    """
    @param regex: the compiled C{_sre.SRE_Pattern} with which to
                  parse the file
    @type regex: _sre.SRE_Pattern 
    @param fields: a C{tuple} of C{str}ings containing names of the
                   fields found by parsing the first line of the
                   fasta record
    @type fields: tuple
    """
    # self.set_regex(regex)
    # self.set_fields(fields)
    if isinstance(regex, basestring):
      regex = re.compile(regex)
    self.regex = regex
    self.fields = fields

  #####################################################################
  # match()
  #####################################################################
  def match(self, astring):
    """
    Returns a C{_sre.SRE_Match} object describing the results of using
    I{self._regex} to search I{string}.

    @param astring: a string generally containing a line of the fasta
                  file being processed
    @type astring: str

    @return: C{_sre.SRE_Match} object describing the results of using
             I{self._regex} to search I{string}
    @rtype: _sre.SRE_Match
    """
    return self.regex.match(astring)


  #####################################################################
  # set_fiels()
  #####################################################################
  def set_regex(self, rgx):
    """
    Sets the I{regex} property to I{rgx}, a C{_sre.SRE_Pattern}.

    @param rgx: a compiled regular expression of the re module
    @type rgx: _sre.SRE_Pattern
    """
    self._regex = rgx

  #####################################################################
  # set_fiels()
  #####################################################################
  def set_fields(self, ary):
    """
    Sets the I{fields} property to I{ary}, a C{tuple} of C{str}ings.

    @param ary: a C{tuple} of C{str}ings naming the fields of the
                type of fasta records
    @type ary: tuple
    """
    self._fields = tuple(ary)

  #####################################################################
  # get_regex()
  #####################################################################
  def get_regex(self):
    """
    Returns the I{regex} property.

    @return: the I{regex} property
    @rtype: _sre.SRE_Pattern
    """
    return self._regex

  #####################################################################
  # get_fields()
  #####################################################################
  def get_fields(self):
    """
    Returns the I{fields} property.

    @return: the I{fields} propery
    @rtype: tuple
    """
    return self._fields

  #####################################################################
  # get_field()
  #####################################################################
  def get_field(self, n):
    """
    Given the C{int} index I{n}, return the field at that index.

    @return: the name of the field in the I{fields} property at
             the index I{n}
    @rtype: str
    """
    return self.fields[n]

  #####################################################################
  # properties
  #####################################################################
  regex = property(get_regex, set_regex)
  fields = property(get_fields, set_fields)


#######################################################################
# _t
#######################################################################
class _t:
  """
  This C{class} is essentially a namespace to hold some values that
  will be used to provide templates for the I{TEMPLATES} C{dict}.
  """
  #####################################################################
  # __init__()
  #####################################################################
  def __init__(self):
    """
    Will raise a C{RuntimeError} if called.

    @raise RuntimeError: raises a C{RuntimeError} under all
                         circumstances
    """
    raise RuntimeError, "This class can not be instantiated."

  #####################################################################
  # default template
  #####################################################################
  _default_regex = re.compile(r'^>\ *(.*)$')
  _default_fields = ("name",)
  _default_template = FastaTemplate( _default_regex,
                                    _default_fields )
  #####################################################################
  # swissprot template
  #####################################################################
  _swissprot_regex = re.compile(r'^>gi\|([^|]*)\|sp\|([^|]*)\|(.*)$')
  _swissprot_fields = ("gi_num","accession","description")
  _swissprot_template = FastaTemplate( _swissprot_regex,
                                       _swissprot_fields )
  #####################################################################
  # pdb
  #####################################################################
  _pdb_regex = re.compile(r'^>(....)_(\S*)\s+[^:]*:(\S*)\s+length:(\S*)\s+(\S*.*)$')
  _pdb_fields = ("idCode", "chainID", "type", "numRes", "description")
  _pdb_template = FastaTemplate(_pdb_regex, _pdb_fields)

  #####################################################################
  # nr
  #####################################################################
  _nr_regex = re.compile(r'^>gi\|([^|]*)\|[^|]*\|([^|]*)\|\s*([^\[]*)\s*\[([^\]]*)\]\s*$')
  _nr_fields = ("gi", "accession", "description", "source")
  _nr_template = FastaTemplate(_nr_regex, _nr_fields)

  #####################################################################
  # nrblast
  #####################################################################
  _nrblast_regex = re.compile(r'^>gi\|([^|]*)\|[^|]*\|([^|]*)\|.*$')
  _nrblast_fields = ("gi", "accession")
  _nrblast_template = FastaTemplate(_nrblast_regex, _nrblast_fields)


#######################################################################
# TEMPLATES
#######################################################################
TEMPLATES = {
              "default"    :  _t._default_template,
              "swissprot"  :  _t._swissprot_template,
              "pdb"        :  _t._pdb_template,
              "nr"         :  _t._nr_template,
              "nrblast"    :  _t._nrblast_template
            }
