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

    
    # Unrestricted Approach
    # param: sequence 1 ( t1 ) and sequence 2 ( t2 )
    #   len(t1) = n; len(t2) = m
	# return min cost of alignment using unrestricted approach.
    # T(n) = O( n * m )    
	def calcCostUnrestricted( self, t1, t2):
		if len(t2) > len(t1):
			temp = t1
			t1 = t2
			t2 = temp

        # generate operating matrix for the two sequences
        # longer sequence is vertical (number of rows), the other is horizontal
		curr = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) ) # O(n * m)
        
        # initialize trace table to store direction of each cell
		tb_table = np.zeros( ( len( t1 ) + 1, len( t2 ) + 1 ) ) # O(n * m)

		# set base column
		curr[:,0] = np.arange(0, ( len(t1) + 1) * INDEL, INDEL ) # O( n )
		# set base row
		curr[0] = np.arange(0, ( len(t2) + 1) * INDEL, INDEL ) # O( m )

		tb_table[:,0] = [0] + [ UP ] * len(t1) # O( n )
		tb_table[0] = [0] + [ SIDE ] * len(t2) # O( m )

        # total: T(n) = O( n * m )
		# for each row ( n ) excluding first row (base)
		for r in range(1,curr.shape[0]):
            # for each column ( m ) excluding first column (base)
			for c in range(1, curr.shape[1]):
                
                # If there is a match!
				if (t1[r-1] == t2[c-1]):                    
                    
                    # set operating matrix and table cells corresponding cell accordingly
					curr[r][c] = curr[r-1][c-1] + MATCH
					tb_table[r][c] = DIA
				else:
                    # grab min value and the direction in which min value derives
					min_val, direction_val = self.getMin( curr[r-1][c], curr[r-1][c-1], curr[r][c-1] )
                    
                    # set operating matrix and table cells corresponding cell accordingly
					curr[r][c] = min_val
					tb_table[r][c] = direction_val
                    
        # traces the direction of of alignment according to direction stored in trace table tb        
		dir = self.traceDirection( tb_table )
        
        # generate alignment sequences from alignment dir list
		seq1 = self.getSeq( t1, dir, False )
		seq2 = self.getSeq( t2, dir, True )

		return curr[-1,-1], seq1, seq2



    # Banded Approach
    # param: t1 = sequence 1,
    #        t2 = sequence 2
    # where len(shorter_sequence) = n
	# return min cost of alignment using banded approach.
    # T(n) = O( k * n )
	def calcCostBanded( self, t1, t2):
        
        # set shorter -> t1, longer sequence -> t2
		if len(t2) < len(t1):
			temp = t1
			t1 = t2
			t2 = temp
            
        # sequences with significant length discrepancies can not be aligned
		if len(t1)-len(t2) > MAXINDELS:
			return np.inf, 'No Alignment Possible.', 'No Alignment Possible.'
		
        # generate operating matrix
        # number of rows = shorter sequence is vertical
        # number of columns = 2 * MAXINDELS + 1  = 7 = k = bandwidth
		curr = np.full( ( len(t1) + 1, 2*MAXINDELS+1 ), np.inf ) # O( k * n ) = O( 7n )
        
        # generate trace table tb filled with infinity values, saame shape operating matrix
		tb_table = np.full( curr.shape, np.inf ) 
        
        # initialize base columns and rows of operating matrix and trace table
		base = np.arange(0, ( MAXINDELS + 1 ) * INDEL, INDEL )
		curr[0] = np.append( base, np.full((1,MAXINDELS), np.inf) )
		curr[:,0] = np.append( base, np.full((1, len(t1) - MAXINDELS ), np.inf) )

		tb_table[0] = np.append( [0] + [ SIDE ] * MAXINDELS, np.full((1,MAXINDELS), np.inf) )
		tb_table[:,0] = np.append( [0] + [ UP ] * MAXINDELS, np.full((1, len(t1) - MAXINDELS ), np.inf) )

        # set current row to consider = 1 (1st row -- r=1 -- is base)
		r = 1
        
        # center is the center column index of curr_row
        # start at 1 (first letter of longer sequence )
        # end at len(t2) + 1 (at last letter of longer sequence )
		center = 1
        
        # offset indicates number of cell to shift right when calculate curr_row's cells
        # start at 0 (base row starts from the beginning)
        # then -> 1 after MAXINDELS + 1 rows to shift each incoming row 1 to the right
		offset = 0
        
        # while still going through each letter of shorter sequence t1 
        # T(n) = O( n * k )
		while r <= (len(t1)):
            
            # set starting column/index of curr_row to be the offset value            
			curr_index = offset 
            
            # initialize row of current r ( row_index ) -- size = k
            # and fill with infinity values
			curr_row = np.empty( 2 * MAXINDELS + 1 )
			curr_row.fill(np.inf)
			tb_row = np.empty( 2 * MAXINDELS + 1 )
			tb_row.fill(np.inf)

            # go through each cell in the k-range == 7 columns,
            # starting from center-column - MAXINDELS and ending at center-column + MAXINDELS             
            # c == row_index of the operating matrix that would be generated in unrestricted approach
            # T(n) = O( k )
			for c in range( center - MAXINDELS, center + MAXINDELS + 1 ):                
				
                # don't consider cases where c is negative
				if c < 0:
					pass
                
                # current column is the base column. 
                # Add value in current cell -> curr_row and update trace table
				elif c == 0:
					curr_row[curr_index] = curr[r][c]
					tb_row[curr_index] = UP
					curr_index += 1
                
                # when reach end of horizontal sequence (longer) breaks. Finished
				elif c == ( len(t2) + 1 ):
					break
				else:

					if t1[r-1] == t2[c-1]: # letter match
						curr_row[ curr_index - offset ] = curr[ r - 1 ][ curr_index - 1 ] + MATCH
						tb_row[ curr_index - offset ] = DIA
                        
                    # case: corresponding letters from sequences don't match
					else:
                        # set upper cell's value to infinity if considering last cell in row
						if curr_index > 6:
							up = np.inf
                        # otherwise consider it normally
						else:
							up = curr[ r - 1 ][ curr_index ]
						diagonal = curr[ r - 1 ][ curr_index - 1 ]
						left = curr[ r ][ curr_index - offset - 1 ]
                        
                        # calculate min value of three, then update current cell
                        # in curr_row and tb_row accordingly
						min_val, direction_val = self.getMin( up, diagonal, left )
						curr_row[ curr_index - offset ] = min_val
						tb_row[ curr_index - offset ] = direction_val
                    
					curr_index += 1
					curr[r] = curr_row
					tb_table[r] = tb_row
            
            # start shifting 1 cell to the right when reach a full row (size = k)
			if curr_index > 6:
				offset = 1

			center += 1
			r += 1
            
        # right now, rows of current operating matrix ( k * n ) are either
        # full (all k cells filled with int values), or
        # partially filled ( some cells are filled with int, rest are infinity)
        # where all leftover infinity values are on the right of all applying rows
        
        # so we push the last few rows that include infinity values 
        # so that all int values are on the right side of these rows
		keep_pushing = True
		while( keep_pushing ):
			r -= 1
			if ( curr[ r ][ 2 * MAXINDELS ] == np.inf ):
				curr = self.pushRow( curr, r )
				tb_table = self.pushRow( tb_table, r )
			else:
				keep_pushing = False
                
        # traces the direction of of alignment according to direction stored in trace table tb        
		dir = self.traceDirection( tb_table, True )
        
        # generate alignment sequences from alignment dir list
		seq1 = self.getSeq( t1, dir, False)
		seq2 = self.getSeq( t2, dir, True)

		return curr[-1,-1], seq1, seq2
    
    
    # generate new list from passed in list so that all infinity values are 
    # on the left and int values are on the right
	def cutRow( self, lst ):
		result = []
		for item in lst:
			if item == np.inf:
				break
			result.append(item)
		return np.append( np.full((1, len(lst) - len(result)), np.inf), result )
    
    # return a new table where table[r] row is pushed ( from cutRow() )correctly 
	def pushRow( self, table, r ):
		row = self.cutRow( table[r] )
		table[ r ] = row
		return table


    # calculate minimum value of the sums of three possible cells and their corresponding costs
    # param: values of up, diagonal, and left cells of current cell
    # return: min value and its direction
	def getMin( self, up, diagonal, left ):
		min_val = min( [ up + INDEL , diagonal + SUB, left + INDEL ] )
		if min_val == ( diagonal + SUB ):
			return min_val, DIA
		elif min_val == ( up + INDEL ):
			return min_val, UP
		else:
			return min_val, SIDE



    # Calculate corresponding alignment of passed in sequence based on direction array
    # param: seq = sequence,
    #        dir = direction list, 
    #        horizontal_axis = position of seq in operating matrix (base column or row)
    # return: alignment of passed in sequence
    # T(n) = O( n )
	def getSeq( self, seq, dir, horizontal_axis=False):
		# print("in get Seq with seq = " + seq)
		result = ''
		index = len(seq)-1
        
        # O(n)
		for item in dir:			
            # add insert/deletion '-' to alignment
			if ( (horizontal_axis == False) & (item == SIDE) ) | ( (horizontal_axis == True) & (item == UP) ):				
				result = '-' + result
            # in case of match/subtitution: add letter at current index				
			else:				
				result = seq[index] + result
				index -= 1			
			if index == -1:
				break

		return result
    
    
    # test whether current list contains an infinity value
	def includeInf( self, lst ):
		return np.any( lst == np.inf )

    # traces the direction of possible shortest path of alignment
    # param: tb = trace table
    #        banded = whether tb is generated from banded algorithm
    # T(n) = O( n )
	def traceDirection( self, tb, banded=False ):
		# print("\n\nGET SEQUENCE starting")
		# print("\ntb is "+ str(tb.shape) + "\n" + str(tb))
        
        # initialize row and column of to be accessed cell in tb
        # start at last cell and work upwards
		r = tb.shape[0] - 1
		c = tb.shape[1] - 1
		dir = [ tb[ r, c ] ]
		count = 0
        
        # keep going through the cells of trace table until reach first cell ( tb[0][0] )
		while (r != 0) | (c != 0 ):
			proceed_normally = True
            
            # in case of banded algorithm
			if banded:
                # if the row containing current cell also contains and infinity value
                # or if current does not have infinity but upper row does
                # then proceed to access trace table normally ( leftup = tb[r-1][c-1], and so on )
                # This is to account for base rows of banded algorithm where shifting of rows does not occur.
				if self.includeInf(tb[r]) == True:
					proceed_normally = True
				elif ( self.includeInf(tb[r]) == False ) & ( self.includeInf(tb[r-1]) == True ):
					proceed_normally = True
                    
                # else: shift all referenced cells one cell sideway to account 
                # This is to account for middle rows of banded algorithm where 
                # shifting of rows does occur ( each row in banded algorithm is 
                # calculated while is 1 cell shifted to the right based on upper row\,
                # then is shifted back to fit in 7*n matrix )
				else:
					proceed_normally = False
            
            # calculate corresponding rows and columns while accounting for shifting of rows
			if proceed_normally == False:

				if   dir[0] == DIA:
					r = r - 1
				elif dir[0] == SIDE:
					c = c - 1
				else:
					r = r - 1
					c = c + 1
                    
            # calculate corresponding rows and columns if proceed normally
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
        
        # reverse finished direction list to start from the [0][0] cell
        # to calculate alignment sequences
		dir.reverse()
		return dir



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

					if banded:
						score, alignment1, alignment2 = self.calcCostBanded( sequences[i][0:align_length], sequences[j][0:align_length] )						
					else:
						score, alignment1, alignment2 = self.calcCostUnrestricted( sequences[i][0:align_length], sequences[j][0:align_length] )

					s = {'align_cost':score, 'seqi_first100':alignment1[0:100], 'seqj_first100':alignment2[0:100]}
					table.item(i,j).setText('{}'.format(int(score) if score != math.inf else score))
					table.repaint()
				jresults.append(s)
			results.append(jresults)
            
		return results
