#!/usr/bin/env python
'''
Finds potential binding sites in a DNA sequence from a PWM.

Takes an input (target) sequence and scans for matches to a PWM (query).
The target should be in FASTA format, and there can be multiple sequences
scanned at the same time. A log-likelihood score will be calculated for each
position in the input target. Any positions with a score greater than 25%
of the maximum score will be reported. The output will be tab-delimited in
the following fields:

    target                   - The name of the target (FASTA)
    pos                      - The position in the target
    log-likelihood score     - The sum of all log-likelihoods for each 
                               position in the query
    matches                  - The number of bases with a log-likelihood > 0
    query                    - The query sub-sequence tested


The PWM should be a text file in TRANSFAC format:
     A      C      G      T
     0      0      40     0
     0      0      40     0
     1      0      39     0
     27     0      13     0
     21     13     1      5
     8      1      3      28
     1      2      2      35
     2      18     0      20
     3      36     0      1
     0      38     0      2

Note: any extra whitespace will be removed and columns don't 
need to be in a fixed order, just correctly labeled. These counts
will be automatically converted to relative frequencies.

Unless specified pseudo-counts will be added to each base, such that at
each position in the matrix, the count will be s+pseudo. The pseudo count
will be:
    background-freq * sqrt(total counts)

This version of a pseudo-count is useful for dealing with both high and low
count PWMs, such that effect of a pseudo-count in high-count PWMs is
proportionally smaller than with low-count PWMs.

Alternatively, you can set a constant value for the pseudo-count, which
will be used for all bases. A common value to use is 0.8 (see Nishida, 
et al. Nucleic Acids Research, 2009; doi:10.1093/nar/gkn1019).

The log-likelihood score at each position will be calculated as:
    ln(pwm-freq / background-freq)

The total score is the sum of the log-likelihood score at each position. Any
substring where the total score is greater than zero will be reported.
'''

import sys
import math

default_background_freq = {'A':0.3, 'T':0.3, 'C':0.2, 'G':0.2}

IUPAC = {
'A': 'A',
'C': 'C',
'G': 'G',
'T': 'T',
'AG': 'R',
'CT': 'Y',
'CG': 'S',
'AT': 'W',
'GT': 'K',
'AC': 'M',
'CGT': 'B',
'AGT': 'D',
'ACT': 'H',
'ACG': 'V',
'ACGT': 'N',
}

class PWM(object):
    def __init__(self, fname=None, pseudo='auto', background_freq=default_background_freq, counts=None):
        self.matrix_llh = { 'A': [], 'C': [], 'G': [], 'T': [] }
        self.totals = []
        self._length = 0
        self._maxscore = 0
        self._maxscores = []
        self.consensus = ''
        self.pseudo = pseudo
        self.background_freq = background_freq

        if fname:
            self._read_counts(fname)
        elif counts:
            self.matrix_counts = counts
        else:
            ValueError("You must specify either a filename to read a PWM from, or the PWM count matrix")

        self._length = len(self.matrix_counts['A'])

        for i in xrange(self._length):
            acc = 0
            for base in ['A', 'C', 'G', 'T']:
                acc += self.matrix_counts[base][i]

            self.totals.append(acc)

            posmax = 0
            possible = []
            for base in ['A', 'C', 'G', 'T']:
                llh = math.log(float(self.matrix_counts[base][i]) / acc / background_freq[base])
                if llh > posmax:
                    posmax = llh

                if llh > 0:
                    possible.append(base)

                self.matrix_llh[base].append(llh)

            self._maxscore += posmax
            self._maxscores.append(posmax)
            self.consensus += IUPAC[''.join(sorted(possible))]

    def _read_counts(self, fname):
        'Reads in a TRANSFAC formatted PWM'
        self.matrix_counts = { 'A': [], 'C': [], 'G': [], 'T': [] }
        with open(fname) as f:
            headers = None
            for line in f:
                cols = line.strip().split()
                if not cols:
                    continue

                cols = cols[:4]

                if not headers:
                    headers = {}
                    for i, val in enumerate(cols):
                        base = val.upper()
                        headers[i] = base
                else:
                    N=0
                    counts = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
                    for i, val in enumerate(cols):
                        count = float(val)
                        counts[headers[i]] = count
                        N += count

                    for base in counts:
                        if self.pseudo == 'auto':
                            self.matrix_counts[base].append(counts[base] + (math.sqrt(N) *  self.background_freq[base]))
                        else:
                            self.matrix_counts[base].append(counts[base] + self.pseudo)

    def revcomp(self):
        matrix_counts = { 'A': [], 'C': [], 'G': [], 'T': [] }
        matrix_counts['A'] = self.matrix_counts['T'][::-1]
        matrix_counts['C'] = self.matrix_counts['G'][::-1]
        matrix_counts['G'] = self.matrix_counts['C'][::-1]
        matrix_counts['T'] = self.matrix_counts['A'][::-1]

        return PWM(pseudo=self.pseudo, background_freq=self.background_freq, counts=matrix_counts)


    @property
    def maxscore(self):
        return self._maxscore

    @property
    def length(self):
        return len(self.totals)

    def dump(self, out=sys.stdout):
        i = 0
        out.write('Pseudo-count matrix:\n\tA\tC\tG\tT\n')
        while i < self.length:
            outcols = ['[%s]' % (i + 1)]
            consensus = []
            for base in 'A C G T'.split():
                outcols.append(str(self.matrix_counts[base][i]))

            out.write('%s\n' % '\t'.join(outcols))
            i+=1

        i = 0
        out.write('\nLog-likelihood matrix:\n\tA\tC\tG\tT\tConsensus\n')
        while i < self.length:
            outcols = ['[%s]' % (i + 1)]
            consensus = []
            for base in 'A C G T'.split():
                outcols.append(str(self.matrix_llh[base][i]))
                if self.matrix_llh[base][i] > 0:
                    consensus.append(base)

            outcols.append('/'.join(consensus))

            out.write('%s\n' % '\t'.join(outcols))
            i += 1

    def score(self, seq, thres=0):
        if len(seq) < self.length:
            raise ValueError("Length of seq (%s) is less then the PWM length (%s)" % (len(seq), self.length))

        acc = 0.0
        matches = 0
        maxpossible = self._maxscore

        for i, s in enumerate(seq):
            if (acc+maxpossible) < thres:
                return None, None

            acc += self.matrix_llh[s][i]
            if self.matrix_llh[s][i] > 0:
                matches += 1

            maxpossible -= self._maxscores[i]


        return acc, matches


def fasta_reader(fname, size=50):
    ref = None
    buf = ''
    pos = 0
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if line[0] == '>':
                if buf:
                    yield (ref, buf, pos)
                ref = line.split()[0][1:]
                pos = 0
                buf = ''
            else:
                buf += line.upper()
                while len(buf) > size:
                    yield (ref, buf[:size], pos)
                    pos += size
                    buf = buf[size:]


def pwmscan(fname, pwm, threshold=0):
    buf = ''
    cur_ref = None
    cur_pos = 0

    reader = fasta_reader(fname)

    print ""
    print "target\tpos\tlog-likelihood score\tmatches\tquery"
    while True:
        try:
            name, seq, pos = reader.next()
        except:
            break

        if name == cur_ref:
            buf += seq
        else:
            cur_ref = name
            cur_pos = pos
            buf = seq

        while len(buf) > pwm.length:
            score, matches = pwm.score(buf[:pwm.length])

            if score is not None:
                if score > threshold:
                    print '\t'.join([str(x) for x in [cur_ref, cur_pos, score, matches, buf[:pwm.length]]])

            buf = buf[1:]
            cur_pos += 1

