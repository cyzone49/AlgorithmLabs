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

UP = 1
DIA = 0
SIDE = -1

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
		tb_table = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) )

		curr[:,0] = np.arange(0, ( len(t1) + 1) * INDEL, INDEL )
		curr[0] = np.arange(0, ( len(t2) + 1) * INDEL, INDEL )

		tb_table[:,0] = [0] + [ UP ] * len(t1)
		tb_table[0] = [0] + [ SIDE ] * len(t2)

		# print("curr =\n" + str(curr))
		# print("tb table = \n" + str(tb_table))


		# for each row
		for r in range(1,curr.shape[0]):
			# print("\tcurr_row = " + str(curr[r]))
			for c in range(1, curr.shape[1]):
				# print("\n\tt1[" + str(r-1) + "]="+str(t1[r-1]))
				# print("\n\tt2[" + str(c-1) + "]="+str(t2[c-1]))
				if (t1[r-1] == t2[c-1]):
					# print("\n\t\t=>> MATCH -- Diagonal!\n")
					curr[r][c] = curr[r-1][c-1] + MATCH
					tb_table[r][c] = DIA
				else:
					min_val = min( curr[r-1][c-1], curr[r][c-1], curr[r-1][c])
					# print("\n\t\tcurr[" + str(r-1) + "][" + str(c-1) + "] is " + str(curr[r-1][c-1]))
					# print("\t\tcurr[" + str(r-1) + "][" + str(c) + "] is " + str(curr[r-1][c]))
					# print("\t\tcurr[" + str(r) + "][" + str(c-1) + "] is " + str(curr[r][c-1]))
					# print("\t\tminval = " + str(min_val))
					if curr[r-1][c-1] == min_val:
						# print("\t\t=>>  Diagonal --- sub ")
						tb_table[r][c] = DIA
						curr[r][c] = min_val + SUB
					else:
						if curr[r-1][c] == min_val:
							# print("\t\t=>>  UP --- ins ")
							tb_table[r][c] = UP
						else:
							# print("\t\t=>>  SIDE --- del ")
							tb_table[r][c] = SIDE
						curr[r][c] = min_val + INDEL
				# print("\n\tcurr after last  op:\n" + str(curr)+"\n\n\n")
				# print("\n\ttb_table after last op:\n" + str(tb_table)+"\n\n\n")

		# print("curr is \n" + str(curr))
		# print("\n\ntb_table is \n" + str(tb_table))

		dir = self.traceDirection( tb_table )
		# print("\tDone back tracing. dir= " + str(dir))

		seq1 = self.getSeq( t1, dir, False )
		seq2 = self.getSeq( t2, dir, True )
		# print("seq1 = " + seq1 )
		# print("seq2 = " + seq2 )


		return curr[-1,-1], seq1, seq2

	def getSeq( self, seq, dir, horizontal_axis=False):
		# print("in get Seq with seq = " + seq)
		result = ''
		index = len(seq)-1
		for item in dir:
			# print("\t\tindex=" + str(index))
			if ( (horizontal_axis == False) & (item == SIDE) ) | ( (horizontal_axis == True) & (item == UP) ):
				# result += '-'
				result = '-' + result
				# print("\t\tresult = " + result)
			else:
				# result += seq[index]
				result = seq[index] + result
				index -= 1
			# print("\t\t=> result = " + result)
			if index == -1:
				break

		return result


	def traceDirection( self, tb ):
		# print("\n\nGET SEQUENCE starting")
		r = tb.shape[0] - 1
		c = tb.shape[1] - 1
		dir = [ tb[ r, c ] ]

		while (r != 0) & (c != 0 ):
			if   dir[0] == DIA:
				r = r - 1
				c = c - 1
			elif dir[0] == SIDE:
				c = c - 1
			else:
				r = r - 1
			dir.insert(0, tb[r,c] )

		dir.reverse()
		return dir



	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		results = []

		# score, s1, s2 = self.calcCostUnrestricted(sequences[0], sequences[1])
		# score, s1, s2 = self.calcCostUnrestricted('AGCTCATGC', 'ACTGCATC')
		# print("s1 = " + s1)
		# print("s2 = " + s2)
		# print("score= " + score)


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
					score, seq1, seq2 = self.calcCostUnrestricted( sequences[i][0:align_length], sequences[j][0:align_length] )
					# seq1=''
					# seq2=''
					alignment1 = seq1 + '  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i+1,
						len(sequences[i]), align_length, ',BANDED' if banded else '')
					alignment2 = seq2 + '  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j+1,
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
