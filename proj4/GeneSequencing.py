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

		# row: t1 (horizontal)
		# col: t2 (vertical)
		curr = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) )
		tb_table = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) )

		# set base column
		curr[:,0] = np.arange(0, ( len(t1) + 1) * INDEL, INDEL )
		# set base row
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
		print("\tDone back tracing. dir= " + str(dir))

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
		print("\n\nBANDED")
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
			print("\n\n\nr = " + str(r) + "\n")
			print("\n\n\noffset = " + str(offset) + "\n")

			curr_index = offset # this is current column in curr [0:6]
			curr_row = np.empty( 2 * MAXINDELS + 1 )
			curr_row.fill(np.inf)
			tb_row = np.empty( 2 * MAXINDELS + 1 )
			tb_row.fill(np.inf)

			print("\n\n\ncurr_index= " + str(curr_index) + "\n")
			print("curr_row = " + str(curr_row))

			for c in range( center - MAXINDELS, center + MAXINDELS + 1 ):
				# c is the current col index of actual table
				print("\nc = " + str(c))
				print("\tcurr_index = " + str(curr_index))
				if c < 0: #just the first few rows
					print("\tcol = c cannot be negative")
					pass
				elif c == 0: # just the rows including base case of t1 (horizontal)
					print("\tAt base horizontal. Already calculated so leave alone")
					curr_row[curr_index] = curr[r][c]
					tb_row[curr_index] = UP
					curr_index += 1

				elif c == ( len(t2) + 1 ): # just the rows that include last row
					print("\tAt the last column. Returning")
					break
				else:
					print("\t[ r = " + str(r) + " ][ c = " + str(c) + " ] with letters: t1[] = " + t1[r-1] + ", t2[] = " + t2[c-1])

					if t1[r-1] == t2[c-1]: # letter match
						print("\t\tMATCH")
						# d = curr[ r - 1 ][ c - 1 ] + MATCH
						curr_row[ curr_index - offset ] = curr[ r - 1 ][ curr_index - 1 ] + MATCH
						tb_row[ curr_index - offset ] = DIA


					else:
						# print("\n\tThree things to consider:")
						if curr_index > 6:
							up = np.inf
							# print("\t\tleft is just inf. outo of bound.")
						else:
							up = curr[ r - 1 ][ curr_index ]
							# print("\t\tcurr["+str(r-1)+"]["+str(curr_index)+"] = " + str(up) )
						diagonal = curr[ r - 1 ][ curr_index - 1 ]
						# print("\t\tcurr["+str(r-1)+"]["+str(curr_index-1)+"] = " + str(diagonal) )
						left = curr[ r ][ curr_index - offset - 1 ]
						# print("\t\tcurr["+str(r)+"]["+str(curr_index - offset -1)+"] = " + str(left))


						min_list = [ diagonal, up, left ]
						print('\t\tminlist = ' + str(min_list))
						min_val = min( min_list )
						# print("\t\tminval = " + str(min_val))
						if diagonal == min_val:
							print("\t\t=>>  Diagonal --- sub ")
							# tb_table[r][c] = DIA
							curr_row[ curr_index - offset ] = min_val + SUB
							tb_row[ curr_index - offset ] = DIA



						else:
							if up == min_val:
								print("\t\t=>>  UP --- ins ")
								tb_row[ curr_index - offset ] = UP
							elif left == min_val:
								print("\t\t=>>  SIDE --- del ")
								tb_row[ curr_index - offset ] = SIDE
							else:
								print("\t\t=>>> should not be here")
							curr_row[ curr_index - offset] = min_val + INDEL


					curr_index += 1
					print("\n\t curr_row = " + str(curr_row))
					curr[r] = curr_row
					tb_table[r] = tb_row
					print("\n\t current curr is : ")
					print(str(curr))

			# curr[r] = curr_row
			print("\n\t Finish one row. current curr is : ")
			print(str(curr))
			if curr_index > 6:
				offset = 1

			center += 1
			r += 1

		print("\n\n curr table = ")
		print(str(curr))
		print("\t\tshape = " + str(curr.shape))

		print("tb_table = ")
		print(str(tb_table))

		keep_pushing = True
		print("\nr = " + str(r) + "\n\n\n\n")
		while( keep_pushing ):
			r -= 1
			if ( curr[ r ][ 2 * MAXINDELS ] == np.inf ):
				curr = self.pushRow( curr, r )
				tb_table = self.pushRow( tb_table, r )
			else:
				keep_pushing = False

		print("\n\nFINAL table = ")
		print(str(curr))
		print("\nFINAL tb_table = ")
		print(str(tb_table))

		dir = self.traceDirection( tb_table, True )

		# print("\tDone back tracing. dir= " + str(dir))


		seq1 = self.getSeq( t1, dir, False)
		seq2 = self.getSeq( t2, dir, True)
		print("seq1 = " + seq1)
		print("seq2 = " + seq2)






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
		r = tb.shape[0] - 1
		c = tb.shape[1] - 1
		dir = [ tb[ r, c ] ]

		while (r != 0) & (c != 0 ):
			# print("\n\n\ncurrent dir = " + str(dir) + " ||| type = " + str(type(dir)))
			# print("\tr before = " + str(r))
			# print("\tc before = " + str(c))
			if len(dir) > 15:
				break
			# print("\t\ttb[r] = " + str(tb[r]) + " of type " + str(type(tb[r])))
			proceed_normally = True
			if banded:
				# print("\t\ttb["+str(r)+"] = " + str(tb[r]))
				# print("\t\ttb["+str(r-1)+"] = " + str(tb[r-1]))
				if self.includeInf(tb[r]) == True:
					proceed_normally = True
				elif ( self.includeInf(tb[r]) == False ) & ( self.includeInf(tb[r-1]) == True ):
					proceed_normally = True
				else:
					proceed_normally = False



			if proceed_normally == False:
				# print("Procedding NOT normally")
				if   dir[0] == DIA:
					# print("\tDIA")
					r = r - 1
				elif dir[0] == SIDE:
					# print("\tSIDE")
					c = c - 1
				else:
					# print("\tUP")
					r = r - 1
					c = c + 1
			else:
				if   dir[0] == DIA:
					# print("\tDIA")
					r = r - 1
					c = c - 1
				elif dir[0] == SIDE:
					# print("\tSIDE")
					c = c - 1
				else:
					# print("\tUP")
					r = r - 1
			# print("\t\tINSERT: tb["+str(r)+"]["+str(c)+"] = " + str(tb[r][c]))
			dir.insert(0, tb[r][c] )

		dir.reverse()
		return dir



	def align( self, sequences, table, banded, align_length):
		self.banded = banded
		self.MaxCharactersToAlign = align_length
		results = []

		# self.calcCostBanded('cataca', 'cotaca')
		# self.calcCostBanded(sequences[0], sequences[1])

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

					if banded:
						score, seq1, seq2 = self.calcCostBanded( sequences[i][0:align_length], sequences[j][0:align_length] )
					else:
						score, seq1, seq2 = self.calcCostUnrestricted( sequences[i][0:align_length], sequences[j][0:align_length] )

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
