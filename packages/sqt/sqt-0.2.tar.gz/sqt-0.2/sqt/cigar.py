"""
CIGAR operations.

There are two ways to represent a CIGAR string:
- as a string, such as "17M1D5M4S"
- as a list of (operator, length) pairs, as used by pysam:
[ (0, 17), (1, 2), (0, 5), (0, 4) ]

The naming convention in this module uses cigar and cigar_string to
distinguish both types.

The mapping of CIGAR operator to numbers is:
MIDNSHP => 0123456
"""
import sys
from itertools import repeat, chain

__author__ = 'Marcel Martin'

# constants
M = 0  # match or mismatch
I = 1  # insertion
D = 2  # deletion
N = 3  # skipped reference region
S = 4  # soft clipping
H = 5  # hard clipping
P = 6  # padding
X = 7
EQ = 8

# use this as a sequence to map an encoded operation to the appropriate
# character
DECODE = 'MIDNSHPX='

# this dictionary maps operations to their integer encodings
_ENCODE = dict( (c,i) for (i, c) in enumerate(DECODE) )


def parse(cigar_string):
	"""
	Parse CIGAR string and return a list of (operator, length) pairs.

	>>> parse("3S17M8D4M9I3H")
	[(4, 3), (0, 17), (2, 8), (0, 4), (1, 9), (5, 3)]
	"""
	cigar = []
	n = ''  # this is a string, to which digits are appended
	for c in cigar_string:
		if c.isdigit():
			n += c
		elif c in _ENCODE:
			if n == '':
				raise ValueError("end of CIGAR string reached, but an operator was expected")
			cigar.append( (_ENCODE[c], int(n)) )
			n = ''
	return cigar


def as_string(cigar, join_by=''):
	"""
	Convert CIGAR, given as list of (operator, length) pairs, to a string.

	>>> as_string([(0, 15), (2, 1), (0, 36)])
	15M1D36M
	"""
	return join_by.join('{}{}'.format(l, DECODE[op]) for op, l in cigar)


def concat(left, right):
	"""
	Concatenate two CIGARs given as list of (operator, length) pairs.

	>>> concat(parse_cigar("1M"), parse_cigar("3M"))
	[(0, 4)]
	"""
	if left and right:
		left_last = left[-1]
		right_first = right[0]
		# same operation?
		if left_last[0] == right_first[0]:
			right[0] = ( right[0][0], right[0][1] + left[-1][1] )
			left = left[:-1]
	return left + right


def aligned_bases(cigar):
	"""
	Return the number of bases of the read that are used in the alignment. This counts
	all matches, mismatches and insertions. The CIGAR must be given as a list of
	(operator, length) pairs.

	This is equal to read_length(cigar) minus the number of soft-clipped bases.
	"""
	return sum(l for op, l in cigar if op in (M, I, EQ, X))


def read_length(cigar):
	"""
	Return length of original read given a CIGAR as list of (operator, length) pairs.
	This includes both hard- and soft-clipped bases.
	"""
	return sum(l for op, l in cigar if op in (M, I, S, H, EQ, X))


def seq_length(cigar):
	"""
	Return length of SEQ field given a CIGAR as list of (operator, length) pairs.
	This counts soft-clipped bases.

	From the SAM spec: 'sum of lengths of the M/I/S/=/X operations shall equal the length of SEQ'
	"""
	return sum(l for op, l in cigar if op in (M, I, S, EQ, X))


def ops(cigar):
	"""
	Yield all operations (as numbers, not characters) one by one.

	>>> list(ops(parse("3S2I3M")))
	[4, 4, 4, 1, 1, 0, 0, 0]
	"""
	return chain.from_iterable(repeat(op, l) for (op, l) in cigar)


def decoded_ops(cigar):
	"""
	Yield all operations (as characters) one by one.

	>>> ''.join(ops(parse("3S2I3M")))
	"SSSIIMMM"
	"""
	return chain.from_iterable(repeat(DECODE[op], l) for (op, l) in cigar)


def _assert_at_end(i):
	"""Assert that the iterator i is at its end"""
	if __debug__:
		try:
			next(i)
			assert False
		except StopIteration:
			pass


def alignment_iter(read, ref, cigar, gap='-'):
	"""
	Yield triples (read_char, reference_char, cigar_char) that
	fully describe the alignment betwen read and ref according to cigar.

	If the cigar operation is a 'M', the cigar_char is set to either
	'=' or 'X' depending on whether read_char matches reference_char
	or not.

	At gaps in the alignment, either read_char or reference_char are
	set to the given gap character.

	read -- an iterable representing the read
	ref -- an iterable representing the reference sequence
	cigar -- a list of (operator, length) pairs
	"""
	i = iter(read)
	j = iter(ref)
	for op in decoded_ops(cigar):
		if op == 'M':
			ci = chr(next(i))
			cj = chr(next(j))
			yield (ci, cj, '=' if ci == cj else 'X')
		elif op == 'I':
			yield (chr(next(i)), gap, 'I')
		elif op == 'D':
			yield (gap, chr(next(j)), 'D')
		else:
			raise ValueError("CIGAR operator {} not supported".format(op))
	_assert_at_end(i)
	_assert_at_end(j)


def print_alignment(read, ref, cigar, file=sys.stdout):
	"""
	Print an alignment between read and ref according to a CIGAR.
	This uses the alignment_iter() function from above.

	cigar -- a list of (operator, length) pairs
	"""
	row1 = ''
	row2 = ''
	align = ''
	for read_char, reference_char, op in alignment_iter(read, ref, cigar):
		row1 += read_char
		align += op
		row2 += reference_char
	print(row1, align, row2, sep='\n', file=file)


def unclipped_region(cigar):
	"""
	Return tuple (cigar, start, stop), where cigar is the given cigar without soft clipping
	and (start, stop) is the interval in which the read is *not* soft-clipped.
	"""
	if cigar[0][0] == S:
		start = cigar[0][1]
		cigar = cigar[1:]
	else:
		start = 0
	if cigar[-1][0] == S:
		stop = -cigar[-1][1]
		cigar = cigar[:-1]
	else:
		stop = None
	return (cigar, start, stop)


class Cigar:
	def __init__(self, cigar):
		if isinstance(cigar, str):
			self.cigar = parse(cigar)
		# elif isinstance(cigar, Cigar): self.cigar = cigar.cigar # no checking
		else:
			self.cigar = cigar

	def __eq__(self, other):
		return self.cigar == other.cigar

	def __ne__(self, other):
		return self.cigar != other.cigar

	def as_string(self, join_by=''):
		return as_string(self.cigar, join_by)

	def __format__(self, format_spec):
		if format_spec in ('', ' '):
			return self.as_string(join_by=format_spec)
		else:
			raise ValueError("format specification '{}' not supported".format(format_spec))

	def __repr__(self):
		return "Cigar('{}')".format(self.as_string)

	def __str__(self):
		return self.as_string()

	def __add__(self, other):
		return Cigar(concat(self.cigar, other.cigar))
