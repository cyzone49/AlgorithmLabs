#!/usr/bin/python3
# why the shebang here, when it's imported?  Can't really be used stand alone, right?  And fermat.py didn't have one...
# this is 4-5 seconds slower on 1000000 points than Ryan's desktop...  Why?


from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QThread, pyqtSignal
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QThread, pyqtSignal
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time
import math


class ConvexHullSolverThread(QThread):
	def __init__( self, unsorted_points,demo):
		self.points = unsorted_points
		self.pause = demo
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	show_hull = pyqtSignal(list,tuple)
	display_text = pyqtSignal(str)

# some additional thread signals you can implement and use for debugging, if you like
	show_tangent = pyqtSignal(list,tuple)
	erase_hull = pyqtSignal(list)
	erase_tangent = pyqtSignal(list)

	def printPoints(self, myList):
		for p in myList:
			print(str(myList.index(p)) + " - " + str(p))

	def drawFromTop(self, lst, top):
		polygon = [QLineF( lst[i], top) for i in range(len(lst))]
		assert( type(polygon) == list and type(polygon[0]) == QLineF )
		self.show_hull.emit(polygon,(255,0,0))

	def solveHull(self, lst):
		if len(lst) < 4:
			result = lst
		result = self.makeHull(lst)
		return result

	# every hull (lst) defined will be sorted in clockwise order
	def makeHull(self, lst):
		if len(lst) == 1:
			return lst
		cut = math.floor(len(lst)/2)
		LHS = self.makeHull(lst[0:cut])
		RHS = self.makeHull(lst[cut:len(lst)])
		return self.mergeHulls(LHS,RHS)

	def mergeHulls(self, LHS, RHS):
		if len(LHS) == 1 & len(RHS) == 1:
			result = LHS + RHS
			return result
		elif ( (len(LHS) == 1) & (len(RHS) == 2) ) | ( (len(LHS) == 2) & (len(RHS) == 1) ):
			result = LHS + RHS
			result = self.sortClockwise(result)
			return result
		else:
			LHS_up,RHS_up = self.findUpperTangent(LHS,RHS,self.findRightMost(LHS), self.findLeftMost(RHS))
			LHS_down,RHS_down = self.findLowerTangent(LHS,RHS,self.findRightMost(LHS), self.findLeftMost(RHS))

			if LHS.index(LHS_down) > LHS.index(LHS_up): #[down:0:up]
				leftHull = LHS[ LHS.index(LHS_down):len(LHS) ] + LHS[ 0:LHS.index(LHS_up)+1]
			else: #[down:up]
				leftHull = LHS[ LHS.index(LHS_down):LHS.index(LHS_up)+1 ]

			if RHS.index(RHS_up) > RHS.index(RHS_down): #[up:0:down]
				rightHull = RHS[ RHS.index(RHS_up):len(RHS) ] + RHS[ 0:RHS.index(RHS_down)+1]
			else: #[up:down]
				rightHull = RHS[ RHS.index(RHS_up):RHS.index(RHS_down)+1 ]

			result = leftHull + rightHull
		return result

	def findUpperTangent(self, LHS, RHS, LHS_right, RHS_left):
		cont = True
		LHS = LHS[::-1] + LHS[::-1] #to find upper tangent, turn LHS counterclockwise
		RHS = RHS + RHS
		#set current points of tangent, starting with leftmost and rightmost
		LHS_current = LHS_right
		RHS_current = RHS_left

		while cont == True:
			continueRHS = True
			continueLHS = True
			for i in range( RHS.index(RHS_current) + 1, len(RHS)): #index of first occurence
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( LHS_current, RHS[i] )

				if angle > prev_angle: #angle increases
					RHS_current = RHS[i]
					prev_angle = angle
					continueLHS = True
				else:
					continueRHS = False
					break

			for i in range( LHS.index(LHS_current) + 1, len(LHS) ):
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( RHS_current, LHS[i] )

				if angle < prev_angle:
					LHS_current = LHS[i]
					prev_angle = angle
					continueRHS = True
				else:
					continueLHS = False
					break
			#cont = False (STOP) if both continue on LHS and RHS are False
			cont = continueLHS | continueRHS

		return LHS_current, RHS_current

	def findLowerTangent(self, LHS, RHS, LHS_right, RHS_left):
		cont = True

		RHS = RHS[::-1] + RHS[::-1] #to find lower tangent, turn RHS counterclockwise
		LHS = LHS + LHS
		#set current points of tangent, starting with leftmost and rightmost
		LHS_current = LHS_right
		RHS_current = RHS_left

		while cont == True:
			continueRHS = True
			continueLHS = True
			for i in range( RHS.index(RHS_current) + 1, len(RHS)): #index of first occurence
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( LHS_current, RHS[i] )

				if angle < prev_angle: #angle increases
					RHS_current = RHS[i]
					prev_angle = angle
					continueLHS = True
				else:
					continueRHS = False
					break

			for i in range( LHS.index(LHS_current) + 1, len(LHS) ):
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( RHS_current, LHS[i] )

				if angle > prev_angle:
					LHS_current = LHS[i]
					prev_angle = angle
					continueRHS = True
				else:
					continueLHS = False
					break

			cont = continueLHS | continueRHS

		return LHS_current, RHS_current



	def findRightMost(self, lst):
		p = lst[(len(lst)-1)]
		x_max = -10
		for point in lst:
			if point.x() > x_max:
				x_max = point.x()
				p = point
		return p

	def findLeftMost(self, lst):
		p = lst[0]
		x_min = 10
		for point in lst:
			if point.x() < x_min:
				x_min = point.x()
				p = point
		return p

	def sortClockwise(self, lst): #for list of 3 points
		leftMost = self.findLeftMost(lst)
		lst.remove(leftMost)
		angle_0 = self.findSlope(leftMost, lst[0])
		angle_1 = self.findSlope(leftMost, lst[1])
		if angle_0 > angle_1:
			return [leftMost, lst[0], lst[1]]
		else:
			return [leftMost, lst[1], lst[0]]

	def findSlope(self, p0, p1):
		return (float)( (p0.y() - p1.y()) / (p0.x() - p1.x()) )

	def run( self):
		assert( type(self.points) == list and type(self.points[0]) == QPointF )

		n = len(self.points)
		print( 'Computing Hull for set of {} points'.format(n) )

		t1 = time.time()
		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		sorted_points = sorted(self.points, key=lambda p:p.x())
		# print('sorted_points size: \n{}'.format(len(sorted_points)))
		# self.printPoints(sorted_points)
		
		t2 = time.time()
		print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2-t1))

		t3 = time.time()
		# TODO: COMPUTE THE CONVEX HULL USING DIVIDE AND CONQUER
		result = self.solveHull(sorted_points)

		t4 = time.time()

		# USE_DUMMY = True
		USE_DUMMY = False
		if USE_DUMMY:
			# this is a dummy polygon of the first 3 unsorted points
			polygon = [QLineF(self.points[i],self.points[(i+1)%3]) for i in range(3)]

			# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
			# object can be created with two QPointF objects corresponding to the endpoints
			assert( type(polygon) == list and type(polygon[0]) == QLineF )
			# send a signal to the GUI thread with the hull and its color
			self.show_hull.emit(polygon,(255,0,0))

		else:
			# TODO: PASS THE CONVEX HULL LINES BACK TO THE GUI FOR DISPLAY

			# Draw Hull
			polygon = [QLineF( result[i], result[(i+1)%len(result)]) for i in range(len(result))]
			assert( type(polygon) == list and type(polygon[0]) == QLineF )
			self.show_hull.emit(polygon,(255,0,0))
			# pass

		# send a signal to the GUI thread with the time used to compute the hull
		self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
