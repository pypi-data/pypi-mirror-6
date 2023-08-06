#!/usr/bin/env python3
"""
Print read length histogram of FASTQ file.
"""
import sys
from collections import Counter
from sqt.io.fasta import FastqReader
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def fastq_length_histogram(path):
	"""Return read length histogram"""
	lengths = Counter()
	with FastqReader(path, mode='rb') as reader:
		for record in reader:
			lengths[len(record.sequence)] += 1
	return lengths


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add('--plot', default=None, help='Plot to this file (.pdf or .png)')
	add("--title", default='Read length histogram of {}',
		help="Plot title, {} is replaced with the input file name (default: '%(default)s')")
	#add('--detailed', '-d', default=False, action='store_true',
		#help='Print information about the sequences themselves, '
			#'such as the character distribution.')
	add('fastq', nargs='+', metavar='FASTQ',
		help='Input FASTQ file(s) (may be gzipped).')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	for path in args.fastq:
		print("## File:", path)
		print("length", "frequency", sep='\t')
		lengths = fastq_length_histogram(path)
		for length in range(0, max(lengths)+1):
			freq = lengths[length]
			print(length, freq, sep='\t')
		if args.plot:
			import matplotlib.pyplot as plt
			import numpy as np
			fig = plt.figure(figsize=(20/2.54, 20/2.54))
			ax = fig.gca()
			ax.set_xlabel('Read length')
			ax.set_ylabel('Frequency')
			ax.set_title(args.title.format(path))
			l, f = list(zip(*lengths.items()))
			l = np.array(l)
			ax.bar(l - 0.5, f)
			ax.set_xlim(-1, None)
			fig.savefig(args.plot)


if __name__ == '__main__':
	main()
