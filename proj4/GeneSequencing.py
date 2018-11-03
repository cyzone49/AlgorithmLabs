#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import math
import time
import numpy as np

# Used to compute the bandwidth for banded version
MAXINDELS = 3

# Used to implement Needleman-Wunsch scoring
MATCH = -3
INDEL = 5
SUB = 1

class GeneSequencing:

	def __init__( self ):
		pass


# This is the method called by the GUI.  _sequences_ is a list of the ten sequences, _table_ is a
# handle to the GUI so it can be updated as you find results, _banded_ is a boolean that tells
# you whether you should compute a banded alignment or full alignment, and _align_length_ tells you
# how many base pairs to use in computing the alignment

	# return min cost of alignment
	def calcCostUnrestricted( self, t1, t2):
		# print("t1 = " + t1 + " ==== size = " + str(len(t1)))
		# print("t2 = " + t2 + " ==== size = " + str(len(t2)))
		curr = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) )
		curr[:,0] = np.arange(0, ( len(t1) + 1) * INDEL, INDEL )
		curr[0] = np.arange(0, ( len(t2) + 1) * INDEL, INDEL )
		# for each row
		for r in range(1,curr.shape[0]):
			# print("\tcurr_row = " + str(curr[r]))
			for c in range(1, curr.shape[1]):
				if (t1[r-1] == t2[c-1]):
					curr[r][c] = curr[r-1][c-1] + MATCH
				else:
					min_val = min( curr[r-1][c-1], curr[r][c-1], curr[r-1][c])
					if curr[r-1][c-1] == min_val:
						curr[r][c] = min_val + SUB
					else:
						curr[r][c] = min_val + INDEL

		return curr[-1,-1]


	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		results = []

		for i in range(len(sequences)):
			jresults = []
			for j in range(len(sequences)):

				if(j < i):
					s = {}
				else:
###################################################################################################
# your code should replace these three statements and populate the three variables: score, alignment1 and alignment2
					# score = i+j;
					# print("\n\tseq[" + str(i) + "] = " + str(sequences[i][0:align_length]))
					# print("\n\tseq[" + str(j) + "] = " + str(sequences[j][0:align_length]))
					score = self.calcCostUnrestricted( sequences[i][0:align_length], sequences[j][0:align_length] )
					alignment1 = 'abc-easy  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i+1,
						len(sequences[i]), align_length, ',BANDED' if banded else '')
					alignment2 = 'as-123--  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j+1,
						len(sequences[j]), align_length, ',BANDED' if banded else '')
###################################################################################################
					s = {'align_cost':score, 'seqi_first100':alignment1, 'seqj_first100':alignment2}
					table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
					table.repaint()
				jresults.append(s)
			results.append(jresults)

		print("RESULT = ")
		print(str(jresults))
		return results
