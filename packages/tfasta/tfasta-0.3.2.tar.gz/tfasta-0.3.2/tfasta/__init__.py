#! /usr/bin/env python

'''
tfasta: Parses and creates fasta files
Copyright (c) 2014, James C. Stroud; All rights reserved.
'''

from _version import __version__

from _tfasta import fasta_parser, make_fasta, make_fasta_from_dict, \
                    string_fasta_parser, io_fasta_parser, \
                    T_DEF, T_SWISS, T_PDB, T_NR, T_NRBLAST, \
                    FASTA_WIDTH, FastaTemplate

__all__ = ["fasta_parser", "make_fasta", "make_fasta_from_dict",
           "string_fasta_parser", "io_fasta_parser",
           "T_DEF", "T_SWISS", "T_PDB", "T_NR", "T_NRBLAST",
           "FASTA_WIDTH", "FastaTemplate"]
