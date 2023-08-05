'''

This module currently isn't in use, but could be used to calcuate the scores for
all Nmers, and then calculate a p-value based on those scores.

The idea would be to pre-calculate the scores/p-values for all Nmers, and then
you could just look up the score/p-value for a given Nmer when scanning along
a DNA target sequence.

See: Hartmann, et al. Genome Research, 2012

'''


class RandomBackground(object):
	def __init__(self, length, pwm, background_freq):
		self.total = 4 ** length
		self.scores = []

		for seq in dna_permute(length):
			score = pwm.score(seq)
			if score > 0:
				self.scores.append(score)

		self.scores.sort()


def dna_permute(length, seq=None):
	print seq
	if not seq:
		seq = ''

	if len(seq) < length:
		for base in ['A', 'C', 'G', 'T']:
			for s in dna_permute(length, '%s%s' % (seq, base)):
				yield s
	else:
		yield seq


