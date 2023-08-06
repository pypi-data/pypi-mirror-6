#!/usr/bin/env python3
"""
Print lots of statistics about one or more FASTA files.
"""
import sys
import os
import subprocess
from collections import Counter
from sqt.io.fasta import FastaReader, IndexedFasta
from sqt import HelpfulArgumentParser

__author__ = "Marcel Martin"


def byte_frequencies(s):
	return Counter(s)


try:
	from sqt._helpers import byte_frequencies
except:
	pass


def n50(lengths, genome_size=None):
	"""
	Return N50 or NG50 value given a list of lengths.

	If the genome_size is not given, it is set to sum(lengths). The resulting
	value is the N50. If it is given, the resulting value is the NG50.

	If genome_size is greater than 2 * sum(lengths), None is returned.
	"""
	if genome_size is None:
		genome_size = sum(lengths)
	lengths = sorted(lengths, reverse=True)
	running_total = 0
	for length in lengths:
		running_total += length
		if running_total >= genome_size * 0.5:
			return length
	return None


def print_statistics(lengths, names, genome_size=None, character_frequencies=None):
	n = len(lengths)
	total = sum(lengths)
	assert len(lengths) == len(names)
	print('No. of sequences: {:11,}'.format(len(lengths)))
	if not lengths:
		return
	min_length = min(lengths)
	max_length = max(lengths)
	min_name = names[lengths.index(min_length)]
	max_name = names[lengths.index(max_length)]
	lengths.sort()
	print('Total length:   {:13,}'.format(sum(lengths)))
	print('Minimum length: {:13,} in entry "{}"'.format(min_length, min_name))
	print('Maximum length: {:13,} in entry "{}"'.format(max_length, max_name))
	print('Average length: {:16.2f}'.format(sum(lengths) / len(lengths)))
	print('Median length:  {:13,}'.format(lengths[n // 2]))
	print('N50:            {:13,}'.format(n50(lengths)))
	if genome_size:
		print('NG50:           {:13,}'.format(n50(lengths, genome_size=genome_size)))

	if character_frequencies:
		print("Character distribution (<char> <count> <percentage>):")
		assert total == sum(character_frequencies.values())
		acgt = 0
		gc = 0
		for upper, lower in (b'Aa', b'Cc', b'Gg', b'Tt'):
			freq = character_frequencies[upper] + character_frequencies[lower]
			if upper in b'GC':
				gc += freq
			print(chr(upper), '    {:14,} {:6.1%}'.format(freq, freq / total))
			acgt += freq
		other = sum(character_frequencies.values()) - acgt
		print('other {:14,} {:6.2%}'.format(other, other / total))
		print('ACGT  {:14,} {:6.2%}'.format(acgt, acgt / total))
		print('GC    {:14,} {:6.2%} (of ACGT)'.format(gc, gc / (total - other)))


def get_lengths(path):
	"""
	Return a list of all sequence lengths of a FASTA file.

	The information is read from the FASTA index file (.fai). If it does
	not exist, an attempt is made to create it.
	"""
	if not os.path.exists(path + '.fai'):
		print('FASTA index file (.fai) does not exist, running "samtools faidx" ...', file=sys.stderr)
		try:
			subprocess.check_output(['samtools', 'faidx', path])
		except (subprocess.CalledProcessError, OSError) as e:
			print('samtools faidx failed:', e)
			raise  # TODO or just do not use the index
	lengths = []
	names = []
	with IndexedFasta(path) as f:
		for index_entry in f.index.values():
			lengths.append(index_entry.length)
			names.append(index_entry.name)
	return lengths, names


def fasta_stats(path):
	"""Return a tuple (lengths, character_frequencies)."""
	lengths = []
	names = []
	counter = Counter()
	with FastaReader(path, binary=True) as reader:
		for record in reader:
			seq = record.sequence #.upper()
			lengths.append(len(seq))
			names.append(record.name)
			counter += byte_frequencies(seq)
	return lengths, names, counter


def get_argument_parser():
	parser = HelpfulArgumentParser(description=__doc__)
	add = parser.add_argument
	add('--detailed', '-d', default=False, action='store_true',
		help='Print information about the sequences themselves, '
			'such as the character distribution.')
	add('--genome-size', '-g', type=int, default=None,
		help='Estimated genome size. If given, also NG50 in addition to N50 is computed.')
	add('fasta', nargs='+', metavar='FASTA',
		help='Input FASTA [[TODO or FASTQ file(s)]] (may be gzipped).')
	return parser


def main():
	parser = get_argument_parser()
	args = parser.parse_args()

	overall_frequencies = Counter()
	overall_lengths = []
	overall_names = []
	if not args.detailed:
		character_frequencies = None
	for path in args.fasta:
		print("## File:", path)
		if args.detailed:
			lengths, names, character_frequencies = fasta_stats(path)
			overall_frequencies += character_frequencies
		else:
			lengths, names = get_lengths(path)
		print_statistics(lengths, names, args.genome_size, character_frequencies)
		overall_lengths.extend(lengths)
		overall_names.extend(names)
	if len(args.fasta) > 1:
		print("## Summary of", len(args.fasta), "files")
		print_statistics(overall_lengths, overall_names, args.genome_size, overall_frequencies if args.detailed else None)


if __name__ == '__main__':
	main()
