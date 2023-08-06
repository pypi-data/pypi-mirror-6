#!/usr/bin/env python3
"""
Read in a BAM or SAM file and print out how often each CIGAR operator (MIDNSHP) was used.
"""
import sys
from collections import Counter
from pysam import Samfile
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"

def main():
	parser = HelpfulArgumentParser(description=__doc__)
	arg = parser.add_argument
	arg("bam", help="Input BAM file.")
	args = parser.parse_args()

	mode = 'r' if args.bam.endswith('.sam') else 'rb'
	infile = Samfile(args.bam, mode)
	#outfile = Samfile('-', "wh", template=infile)

	counter = Counter()
	for record in infile:
		if record.cigar is not None:
			for op, l in record.cigar:
				counter[op] += l
	ops = 'MIDNSHP'
	total = sum(counter.values())
	for op in sorted(counter):
		print("{:2} {:9} ({:7.2%})".format(ops[op], counter[op], counter[op]/total))


if __name__ == '__main__':
	main()
