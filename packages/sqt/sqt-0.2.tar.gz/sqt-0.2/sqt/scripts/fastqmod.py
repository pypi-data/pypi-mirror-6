#!/usr/bin/env python3
"""
Modify FASTQ files.

Possible modifications:
- pick a subset of reads (given by name). With lots of read names, this is faster
  than 'grep -A 3 --no-group-separator -f readnames.txt file.fastq' magic.
- trim low-quality ends
- trim reads to a given length (this is faster than fastx_trimmer)
- reverse-complement each read

The result is written to standard output in FASTQ format. Modifications are
done in the order in which they are listed above.

The algorithm for quality trimming is the same as the one used by BWA:
- Subtract the cutoff value from all qualities.
- Compute partial sums from all indices to the end of the sequence.
- Trim sequence at the index at which the sum is minimal.
"""
import sys
import errno
from sqt.io.fasta import FastqReader, FastqWriter
from sqt import HelpfulArgumentParser
from sqt.dna import reverse_complement
from sqt.qualtrim import quality_trim_index as trim_index

__author__ = "Marcel Martin"


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	parser.add_argument('--names', default=None,
		help='File with names of reads to keep, one per line (default: keep all)')
	parser.add_argument("-q", "--cutoff", type=int, default=None,
		help="Quality cutoff (default: no quality trimming)")
	parser.add_argument("--length", "-l", type=int, default=None,
		help="Shorten reads to LENGTH (default: don't shorten)")
	parser.add_argument('--reverse-complement', '-r', action='store_true',
		default=False, help='Reverse-complement each sequence')
	parser.add_argument('fastq', metavar='FASTQ',
		help='input FASTQ file')
	#parser.add_option("--histogram", action="store_true", default=False,
		#help="Print a histogram of the length of removed ends")
	#parser.add_option("-c", "--colorspace", action="store_true", default=False,
		#help="Assume input files are in color space and that the sequences contain an initial primer base")
	return parser


class ReadPicker:
	def __init__(self, file_with_names):
		read_names = []
		with open(file_with_names) as f:
			read_names = f.read().split('\n')
		self.read_names = { rn for rn in read_names if rn != '' }

	def __call__(self, read):
		rname = read.name.split(' ', maxsplit=1)[0]
		if rname.endswith('/1'):
			rname = rname[:-2]
		elif rname.endswith('/2'):
			rname = rname[:-2]
		if rname in self.read_names:
			return read
		else:
			return None


class QualityTrimmer:
	def __init__(self, cutoff):
		self.cutoff = cutoff

	def __call__(self, read):
		index = trim_index(read.qualities, self.cutoff)
		return read[:index]


class Shortener:
	def __init__(self, length):
		self.length = length

	def __call__(self, read):
		return read[:self.length]


def reverse_complementer(read):
	read.sequence = reverse_complement(read.sequence)
	read.qualities = read.qualities[::-1]
	return read


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	modifiers = []
	if args.names:
		modifiers.append(ReadPicker(args.names))
	if args.cutoff is not None:
		modifiers.append(QualityTrimmer(args.cutoff))
	if args.length:
		modifiers.append(Shortener(args.length))
	if args.reverse_complement:
		modifiers.append(reverse_complementer)
	writer = FastqWriter(sys.stdout)
	with FastqReader(args.fastq, mode='rb') as fr:
		try:
			for record in fr:
				for modifier in modifiers:
					record = modifier(record)
					if record is None:
						break
				else:
					# only executed if loop did not terminate via break
					writer.write(record)
		except IOError as e:
			if e.errno != errno.EPIPE:
				raise


if __name__ == '__main__':
	main()
