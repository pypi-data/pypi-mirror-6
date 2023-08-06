#!/usr/bin/env python3
"""
Python 2 and 3 compatible fast reverse complement
"""
import sys

if sys.version < '3':
	from string import maketrans
else:
	maketrans = bytes.maketrans
	_TR_STR = str.maketrans('ACGTUMRWSYKVHDBNacgtumrwsykvhdbn', 'TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn')

_TR = maketrans(b'ACGTUMRWSYKVHDBNacgtumrwsykvhdbn', b'TGCAAKYWSRMBDHVNtgcaakywsrmbdhvn')

if sys.version < '3':
	def reverse_complement(s):
		return s.translate(_TR)[::-1]
else:
	def reverse_complement(s):
		if isinstance(s, str):
			return s.translate(_TR_STR)[::-1]
		else:
			return s.translate(_TR)[::-1]


GENETIC_CODE = {
	'AAA': 'K',
	'AAC': 'N',
	'AAG': 'K',
	'AAT': 'N',
	'ACA': 'T',
	'ACC': 'T',
	'ACG': 'T',
	'ACT': 'T',
	'AGA': 'R',
	'AGC': 'S',
	'AGG': 'R',
	'AGT': 'S',
	'ATA': 'I',
	'ATC': 'I',
	'ATG': 'M',
	'ATT': 'I',
	'CAA': 'Q',
	'CAC': 'H',
	'CAG': 'Q',
	'CAT': 'H',
	'CCA': 'P',
	'CCC': 'P',
	'CCG': 'P',
	'CCT': 'P',
	'CGA': 'R',
	'CGC': 'R',
	'CGG': 'R',
	'CGT': 'R',
	'CTA': 'L',
	'CTC': 'L',
	'CTG': 'L',
	'CTT': 'L',
	'GAA': 'E',
	'GAC': 'D',
	'GAG': 'E',
	'GAT': 'D',
	'GCA': 'A',
	'GCC': 'A',
	'GCG': 'A',
	'GCT': 'A',
	'GGA': 'G',
	'GGC': 'G',
	'GGG': 'G',
	'GGT': 'G',
	'GTA': 'V',
	'GTC': 'V',
	'GTG': 'V',
	'GTT': 'V',
	'TAC': 'Y',
	'TAT': 'Y',
	'TCA': 'S',
	'TCC': 'S',
	'TCG': 'S',
	'TCT': 'S',
	'TGC': 'C',
	'TGG': 'W',
	'TGT': 'C',
	'TTA': 'L',
	'TTC': 'F',
	'TTG': 'L',
	'TTT': 'F'
}
