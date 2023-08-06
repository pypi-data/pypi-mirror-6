#!/usr/bin/env python3
"""
Efficiently extract a region from a FASTA file. The FASTA file must have been
indexed with "samtools faidx". The result is printed in FASTA format to standard output.

Regions are specified in the format "[rc:]name[:start-stop]".
If "start" and "stop" are omitted, the whole sequence is returned.
Coordinates are 1-based and both endpoints of the interval are included.
A region specification may be prefixed by 'rc:' in order to output the reverse
complement of the specified region. It must hold that start <= stop,
even when reverse complements are requested. If it does not hold, the output
sequence is empty.

Please be aware that samtools faidx uses only the part of the sequence name up to, but not including,
the first whitespace character. That is, if an entry in your FASTA file looks like this:

>seq1 this is a sequence

Then the identifier for this sequence is simply 'seq1'.

Example

To extract the first 200 nucleotides from chromosome 1, which is named 'chr1' in the FASTA file:

fastaextract hg19.fa chr1:1-200
"""
from __future__ import print_function, division

import sys
import mmap
from collections import defaultdict, namedtuple

from .. import HelpfulArgumentParser
from ..io.fasta import FastaReader, IndexedFasta, FastaWriter
from ..io.xopen import xopen
from ..dna import reverse_complement

__author__ = "Marcel Martin"


def parse_region(s):
	"""
	Parse a string like "name:begin-end".
	The returned tuple is (name, start, stop, revcomp).
	start is begin-1, stop is equal to end.

	The string may be prefixed with "rc:", in which case revcomp is set to True.

	If 'end' is not given (as in "chrx:1-"), then stop is set to None.
	If only 'name' is given (or "rc:name"), start is set to 0 and stop to None.

	This function converts from 1-based intervals to pythonic open intervals!
	"""
	revcomp = False
	if s.startswith('rc:'):
		revcomp = True
		s = s[3:]
	fields = s.rsplit(':', 1)
	if len(fields) == 1:
		region = (fields[0], 0, None, revcomp)
	else:
		start, stop = fields[1].split('-')
		start = int(start)
		stop = int(stop) if stop != '' else None
		assert 0 < start and (stop is None or start <= stop)
		region = (fields[0], start-1, stop, revcomp)
	return region


def format_region(chrom, start, stop, revcomp):
	if (start == 0) and (stop is None):
		return chrom
	else:
		assert 0 <= start <= stop
		revcomp_str = "rc:" if revcomp else ""
		return "{}{}:{}-{}".format(revcomp_str, chrom, start+1, stop)


def main():
	if sys.version[:3] < '2.7':
		print("Sorry, python version >= 2.7 required!",file=sys.stderr)
		sys.exit(1)
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument("fasta", metavar="FASTA", help="The indexed FASTA file")
	parser.add_argument("region", metavar="REGION [REGION ...]", nargs='+')
	args = parser.parse_args()
	writer = FastaWriter(sys.stdout)

	regions = [ parse_region(s) for s in args.region ]

	indexedfasta = IndexedFasta(args.fasta)
	for chrom, start, stop, revcomp in regions:
		#if stop > len(record.sequence) ...
		sequence = indexedfasta.get(chrom).read(start, stop)
		if revcomp:
			sequence = reverse_complement(sequence)
		# TODO we shouldn't need to know about indexedfasta.index
		if stop is None:
			stop = indexedfasta.index[chrom].length
		if sys.version > '3':
			sequence = sequence.decode('ascii')
		writer.write(format_region(chrom, start, stop, revcomp), sequence)


if __name__ == '__main__':
	main()
