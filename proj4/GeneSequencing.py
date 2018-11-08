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
		if len(t2) > len(t1):
			temp = t1
			t1 = t2
			t2 = temp

		curr = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) )
		tb_table = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) )

		# set base column
		curr[:,0] = np.arange(0, ( len(t1) + 1) * INDEL, INDEL )
		# set base row
		curr[0] = np.arange(0, ( len(t2) + 1) * INDEL, INDEL )

		tb_table[:,0] = [0] + [ UP ] * len(t1)
		tb_table[0] = [0] + [ SIDE ] * len(t2)

		# for each row
		for r in range(1,curr.shape[0]):
			for c in range(1, curr.shape[1]):
				if (t1[r-1] == t2[c-1]):
					curr[r][c] = curr[r-1][c-1] + MATCH
					tb_table[r][c] = DIA
				else:
					min_val, direction_val = self.getMin( curr[r-1][c], curr[r-1][c-1], curr[r][c-1] )
					curr[r][c] = min_val
					tb_table[r][c] = direction_val

		dir = self.traceDirection( tb_table )


		seq1 = self.getSeq( t1, dir, False )
		seq2 = self.getSeq( t2, dir, True )
		# print("seq1 = " + seq1 )
		# print("seq2 = " + seq2 )

		return curr[-1,-1], seq1, seq2



	def cutRow( self, lst ):
		result = []
		for item in lst:
			if item == np.inf:
				break
			result.append(item)
		return np.append( np.full((1, len(lst) - len(result)), np.inf), result )

	def pushRow( self, table, r ):
		row = self.cutRow( table[r] )
		table[ r ] = row
		return table


	def calcCostBanded( self, t1, t2):
		if len(t2) > len(t1):
			temp = t1
			t1 = t2
			t2 = temp
		if len(t1)-len(t2)>MAXINDELS:
			return np.inf, 'No Alignment Possible.', 'No Alignment Possible.'

		# print("\n\n\n t1 (vertical) = " + t1)
		# print("\n\n\n t2 (horizontal) = " + t2)

		curr = np.full( ( len(t1) + 1, 2*MAXINDELS+1 ), np.inf )
		tb_table = np.full( curr.shape, np.inf )

		base = np.arange(0, ( MAXINDELS + 1 ) * INDEL, INDEL )
		curr[0] = np.append( base, np.full((1,MAXINDELS), np.inf) )
		curr[:,0] = np.append( base, np.full((1, len(t1) - MAXINDELS ), np.inf) )

		tb_table[0] = np.append( [0] + [ SIDE ] * MAXINDELS, np.full((1,MAXINDELS), np.inf) )
		tb_table[:,0] = np.append( [0] + [ UP ] * MAXINDELS, np.full((1, len(t1) - MAXINDELS ), np.inf) )

		r = 1
		center = 1
		offset = 0
		while r <= (len(t1)):

			curr_index = offset # this is current column in curr [0:6]
			curr_row = np.empty( 2 * MAXINDELS + 1 )
			curr_row.fill(np.inf)
			tb_row = np.empty( 2 * MAXINDELS + 1 )
			tb_row.fill(np.inf)

			for c in range( center - MAXINDELS, center + MAXINDELS + 1 ):
				# c is the current col index of actual table
				if c < 0:
					pass
				elif c == 0:
					curr_row[curr_index] = curr[r][c]
					tb_row[curr_index] = UP
					curr_index += 1

				elif c == ( len(t2) + 1 ):
					break
				else:

					if t1[r-1] == t2[c-1]: # letter match
						curr_row[ curr_index - offset ] = curr[ r - 1 ][ curr_index - 1 ] + MATCH
						tb_row[ curr_index - offset ] = DIA

					else:
						if curr_index > 6:
							up = np.inf
						else:
							up = curr[ r - 1 ][ curr_index ]
						diagonal = curr[ r - 1 ][ curr_index - 1 ]
						left = curr[ r ][ curr_index - offset - 1 ]

						min_val, direction_val = self.getMin( up, diagonal, left )
						curr_row[ curr_index - offset ] = min_val
						tb_row[ curr_index - offset ] = direction_val

					curr_index += 1
					curr[r] = curr_row
					tb_table[r] = tb_row

			if curr_index > 6:
				offset = 1

			center += 1
			r += 1

		keep_pushing = True
		while( keep_pushing ):
			r -= 1
			if ( curr[ r ][ 2 * MAXINDELS ] == np.inf ):
				curr = self.pushRow( curr, r )
				tb_table = self.pushRow( tb_table, r )
			else:
				keep_pushing = False

		dir = self.traceDirection( tb_table, True )
		# print("\n\n\n\n\tDone back tracing. dir= " + str(dir))
		# print("\n\n\tDone back tracing. dir= " + str(dir))
		# print("\t\t\twith len = " + str(len(dir)))


		seq1 = self.getSeq( t1, dir, False)
		seq2 = self.getSeq( t2, dir, True)

		return curr[-1,-1], seq1, seq2



	def getMin( self, up, diagonal, left ):
		min_val = min( [ up + INDEL , diagonal + SUB, left + INDEL ] )
		if min_val == ( diagonal + SUB ):
			return min_val, DIA
		elif min_val == ( up + INDEL ):
			return min_val, UP
		else:
			return min_val, SIDE




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

	def includeInf( self, lst ):
		return np.any( lst == np.inf )

	def traceDirection( self, tb, banded=False ):
		# print("\n\nGET SEQUENCE starting")
		# print("\ntb is "+ str(tb.shape) + "\n" + str(tb))
		r = tb.shape[0] - 1
		c = tb.shape[1] - 1
		dir = [ tb[ r, c ] ]
		count = 0
		while (r != 0) | (c != 0 ):
			proceed_normally = True
			if banded:
				if self.includeInf(tb[r]) == True:
					proceed_normally = True
				elif ( self.includeInf(tb[r]) == False ) & ( self.includeInf(tb[r-1]) == True ):
					proceed_normally = True
				else:
					proceed_normally = False

			if proceed_normally == False:

				if   dir[0] == DIA:
					r = r - 1
				elif dir[0] == SIDE:
					c = c - 1
				else:
					r = r - 1
					c = c + 1

			else:
				if   dir[0] == DIA:
					r = r - 1
					c = c - 1
				elif dir[0] == SIDE:
					c = c - 1
				else:
					r = r - 1

			dir.insert(0, tb[r][c] )
			count += 1

		dir.reverse()
		return dir



	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		results = []

		# self.calcCostBanded('cataca', 'cotaca')


		# if banded == False:
		# 	score, s1, s2 = self.calcCostUnrestricted(sequences[0], sequences[1])
		# else:
		# score, s1, s2 = self.calcCostBanded(sequences[8][0:align_length], sequences[9][0:align_length])
		# print("s1 = " + s1)
		# print("s2 = " + s2)
		# #
		# print("\n\n\n\nlen s1 = " + str(len(s1)))
		# print("\nlen s2 = " + str(len(s2)))
		# print("score= " + str(score))


		for i in range(len(sequences)):
			jresults = []
			for j in range(len(sequences)):

				if(j < i):
					s = {}
				else:

					if banded:
						score, alignment1, alignment2 = self.calcCostBanded( sequences[i][0:align_length], sequences[j][0:align_length] )
						# print("\nalignment1[0:100] = " + alignment1[0:100])
						# print("\n\t\twith len = " + str(len(alignment1[0:100])))
						#
						# print("\nalignment2[0:100] = " + alignment2[0:100])
						# print("\n\t\twith len = " + str(len(alignment2[0:100])))
					else:
						score, alignment1, alignment2 = self.calcCostUnrestricted( sequences[i][0:align_length], sequences[j][0:align_length] )

					# alignment1 = seq1 + '  DEBUG:(seq{}, {} chars,align_len={}{})'.format(i+1,
					# 	len(sequences[i]), align_length, ',BANDED' if banded else '')
					# alignment2 = seq2 + '  DEBUG:(seq{}, {} chars,align_len={}{})'.format(j+1,
					# 	len(sequences[j]), align_length, ',BANDED' if banded else '')

					s = {'align_cost':score, 'seqi_first100':alignment1[0:100], 'seqj_first100':alignment2[0:100]}
					table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
					table.repaint()
				jresults.append(s)
			results.append(jresults)

		# print("RESULT = ")
		# print(str(jresults))
		return results
