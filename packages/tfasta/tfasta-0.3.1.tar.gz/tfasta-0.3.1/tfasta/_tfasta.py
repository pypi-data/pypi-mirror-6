#! /usr/bin/env python

"""
tfasta: reading and writing of fast files

This is automatically generated documentation and should
not be relied on for the API. Please
see the official documentation at http://pythonhosted.org/tfasta/.

The most useful functions are:

     - B{L{fasta_parser}}: returns an iterator for a fasta file
     - B{L{string_fasta_parser}}: returns an iterator for fasta text
     - B{L{io_fasta_parser}}: returns an iterator for fasta text
     - B{L{make_fasta_from_dict}}: returns a string representation
             of a fasta file given a C{dict} of sequences
             keyed by record name
     - B{L{make_fasta}}: returns a string representation of a
             fasta record given a sequence (as a C{str}) and
             a name (also as a C{str})

See L{tfasta_templates} documentation for supported fasta file types.

@var FASTA_WIDTH: default width of fasta sequences
@type FASTA_WIDTH: int
"""

import re
import sys
import cStringIO
from tfasta_templates import FastaTemplate, TEMPLATES

T_DEF = TEMPLATES['default']
T_SWISS = TEMPLATES['swissprot']
T_PDB = TEMPLATES['pdb']
T_NR = TEMPLATES['nr']
T_NRBLAST = TEMPLATES['nrblast']

FASTA_WIDTH = 60

CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-"

#######################################################################
# io_fasta_parser()
#######################################################################
def io_fasta_parser(fastafile, template=None, dogaps=False):
  """
  Helper generator function for L{fasta_parser} and
  L{string_fasta_parser}.

  Given I{fastafile} (C{file}-like object, open for reading),
  returns an iterator that iterates over the fasta file.
  It will C{yield} dictionaries keyed according
  to the C{fields} in C{template}. These dictionaries will all also
  include a sequence keyed by "sequence".
  
  @param fastafile: C{file}-like object containing fasta text,
                    opened for reading
  @param template: instance of C{FastaTemplate} class--choose from
                   TEMPLATES or define your own.
  @type template: FastaTemplate
  @param dogaps: a C{bool} specifying whether to keep "-" in the
                 sequence after parsing the file
                   - if C{False}, then gaps are ignored
                   - handy if processing an alignment
  """
  letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

  # set the default template if necessary
  if (template is None):
    template = T_DEF
  # gaps
  if dogaps:
    alphabet = letters + "-"
  else:
    alphabet = letters
  # set the flag to tells us if we have found a fasta entry
  found_first = False
  fasta = []
  # main loop
  while (True):
    aline = fastafile.readline()
    # see if end of file
    if (not aline):
      if (found_first):
        yield entry
      break
    # see if the line matches the supplied regex
    fasta_match = template.match(aline)
    if (fasta_match):
      if (found_first):
        yield entry
      else:
        found_first = True
      # start a new entry because we found a match
      entry = {"sequence" : ""}
      # fill the hash described in template
      index = 0  # which key (field) we are on
      # iterate over all of the fields
      while (index < len(template.fields)):
        # match group 0 is entire match, so must add 1
        entry[template.get_field(index)] = fasta_match.group(index+1)
        index = index + 1
    else:
      # probably a sequence line
      if (found_first):
        seqline = "".join([c.upper() for c in aline if c.upper() in alphabet])
        # it is a sequence line because we must be in a record
        entry["sequence"] = entry["sequence"] + seqline
      else:
        # file not true fasta format, keep going to find first record
        pass
  # clean up
  fastafile.close()


#######################################################################
# fasta_parser()
#######################################################################
def fasta_parser(filename,template=None,greedy=None,dogaps=False):
  """
  Given a I{filename}, returns an iterator that iterates
  over the fasta file. It will C{yield} dictionaries keyed according
  to the C{fields} in C{template}. These dictionaries will all also
  include a sequence keyed by "sequence". Yielding dictionaries
  allows for flexibility in the types of fasta files parsed.

  File format testing is not done, so make sure its a fasta file.

  @param filename: name of the fasta file
  @type filename: str
  @param template: instance of C{FastaTemplate} class--choose from
                   TEMPLATES or define your own.
  @type template: FastaTemplate
  @param greedy: a C{bool} specifying whether to read the
      whole fasta file in at once. Set to C{True} for many smaller
      files or to C{False} for a few or one REALLY big ones.
  @type greedy: bool
  @param dogaps: a C{bool} specifying whether to keep "-" in the
                 sequence after parsing the file
                   - if C{False}, then gaps are ignored
                   - handy if processing an alignment
  """
  # be safe if greediness is not specified
  if (greedy is None):
    greedy = False
  # open the fasta file
  fastafile = open(filename)
  # flag to for finding the first record
  if (greedy):
    # read the whole file and make a switch, no-one the wiser
    afile = cStringIO.StringIO(fastafile.read())
    fastafile.close()
    fastafile = afile
  return io_fasta_parser(fastafile, template, dogaps)

#######################################################################
# parse_string_fasta()
#######################################################################
def string_fasta_parser(astr, template=None, dogaps=False):
  """
  Given I{astr} (string of fasta), returns an iterator that iterates
  over the fasta file. It will C{yield} dictionaries keyed according
  to the C{fields} in C{template}. These dictionaries will all also
  include a sequence keyed by "sequence". Yielding dictionaries
  allows for flexibility in the types of fasta files parsed.

  This function will do its best to remove unneeded whitespace,
  including line breaks.

  Beyond simple extra whitespace, the `astr` should be properly
  formatted fasta text.

  @param astr: fasta text
  @type astr: str
  @param template: instance of C{FastaTemplate} class--choose from
                   TEMPLATES or define your own.
  @type template: FastaTemplate
  @param dogaps: a C{bool} specifying whether to keep "-" in the
                 sequence after parsing the file
                   - if C{False}, then gaps are ignored
                   - handy if processing an alignment
  """
  astr = "\n".join([s.strip() for s in astr.splitlines() if s.strip()])
  fastafile = cStringIO.StringIO(astr)
  return io_fasta_parser(fastafile, template, dogaps)

###################################################################
# make_fasta_from_dict()
###################################################################
def make_fasta_from_dict(adict, width=FASTA_WIDTH):
  """
  Give it a C{dict} of sequences keyed by name of the sequence
  and it returns a fasta representation as a C{str}.

  @param adict: C{dict} of sequences keyed by name
  @type adict: dict

  @return: fasta representation of sequences as a C{str}
  @rtype: str
  """
  fastastr = ""
  names = adict.keys()
  names.sort()
  for aname in names:
    aseq = adict[aname]
    fastastr = "\n".join([fastastr, make_fasta(aname, aseq, width)])
  return fastastr


###################################################################
# make_fasta()
###################################################################
def make_fasta(name, seq, width=FASTA_WIDTH):
  """
  Give it a sequence I{name} and a sequence (I{seq}) and it
  returns a fasta representation as a C{str}.

  @param name: name of sequence
  @type name: str
  @param seq: sequence as a C{str}
  @type seq: str

  @return: a string representation of a fasta record
  @rtype: str
  """
  seq = "".join([c for c in seq if c in CHARS])
  seq = seq.upper()
  place = 0
  fastaseq = ">" + str(name)
  while place < len(seq):
    char = seq[place]
    if (place % width) == 0:
      fastaseq = fastaseq + "\n"
    fastaseq = fastaseq + char
    place = place + 1
  fastaseq = fastaseq
  return fastaseq



#######################################################################
# test_parser
#######################################################################
def test_parser(template, filename):
  """
  Tests for proper construction of a parser using I{template} or
  of the fasta file named I{filename}.

  @param template: C{FastaTemplate} describing fasta record
  @type template: FastaTemplate
  @param filename: name of fasta file
  @type filename: str

  @raise Exception: raises C{Exception} if fasta file is malformed
                    or if the I{template} didn't work

  @return: C{True} if it works.
  @rtype: bool
  """
  newfasRE = re.compile(r'>')

  afile = open(filename)
  for aline in afile:
    if newfasRE.search(aline):
      if not template.match(aline):
        afile.close()
        raise Exception, "%s\n\nmalformed fasta file: '%s'" % \
                         (aline, filename)
  afile.close()
  return True

