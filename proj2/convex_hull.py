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
			# if (p.y() == up_y.y()) & (p.x() == up_y.x()):
			# 	continue
			# angle = (float)( ( up_y.y() - p.y() ) / ( up_y.x() - p.x() ) )
			print(p)
			# print(angle)

	def drawFromTop(self, lst, top):
		polygon = [QLineF( lst[i], top) for i in range(len(lst))]
		assert( type(polygon) == list and type(polygon[0]) == QLineF )
		self.show_hull.emit(polygon,(255,0,0))

	def solveHull(self, lst):
		if len(lst) < 4:
			result = lst
		result = self.makeHull(lst)

		polygon = [QLineF( lst[i], lst[(i+1)%len(lst)]) for i in range(len(lst))]
		assert( type(polygon) == list and type(polygon[0]) == QLineF )
		self.show_hull.emit(polygon,(255,0,0))

	# every hull (lst) defined will be sorted in clockwise order
	def makeHull(self, lst):
		if len(lst) == 1:
			return lst
		cut = math.floor(len(lst)/2)
		LHS = self.makeHull(lst[0:cut])
		RHS = self.makeHull(lst[cut:len(lst)])
		return self.mergeHulls(LHS,RHS)

	def mergeHulls(self, LHS, RHS):
		print("\nLHS = " + str(LHS))
		print("\nRHS = " + str(RHS))
		if len(LHS) == 1 & len(RHS) == 1:
			result = LHS + RHS
		elif ( (len(LHS) == 1) & (len(RHS) == 2) ) | ( (len(LHS) == 2) & (len(RHS) == 1) ):
			result = LHS + RHS
			result = self.sortClockwise(result)
		else:
			LHS_right = self.findRightMost(LHS)
			RHS_left = self.findLeftMost(RHS)
			print("LHS_right = " + str(LHS_right) + " with index " + str(LHS.index(LHS_right)))
			print("RHS_left = " + str(RHS_left) + " with index " + str(RHS.index(RHS_left)))
			a,b = self.findUpperTangent(LHS,RHS,LHS_right, RHS_left)

			print("\n\n\n")



			result = LHS + RHS

		print("result now = " + str(result))
		return result

	def findUpperTangent(self, LHS, RHS, LHS_right, RHS_left):
		cont = True
		amax = -100


		LHS = LHS[::-1]
		print("LHS = " + str(LHS))
		print("RHS = " + str(RHS))
		#set current points of tangent, starting with leftmost and rightmost
		LHS_current = LHS_right
		RHS_current = RHS_left

		while cont == True:

			# cont_Right = True
			# cont_Left = True

			for i in range( RHS.index(RHS_current), len(RHS)+RHS.index(RHS_current) ):
				prev_angle = 0
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( LHS_current, RHS[i+1] )

				if angle > prev_angle: #angle increases					
					RHS_current = RHS[i]
					prev_angle = angle
				else:
					cont = False
					break

			for i in range( LHS.index(LHS_current), len(LHS)+LHS.index(LHS_current) ):
				angle = self.findSlope( RHS_current, LHS[i] )
				if

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



		print('sorted_points size: \n{}'.format(len(sorted_points)))
		self.printPoints(sorted_points)
		up_y = sorted_points[0]
		for p in sorted_points:
			if p.y() > up_y.y():
				up_y = p
		self.drawFromTop(sorted_points, up_y)

		t2 = time.time()
		print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2-t1))

		t3 = time.time()
		# TODO: COMPUTE THE CONVEX HULL USING DIVIDE AND CONQUER

		self.solveHull(sorted_points)





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
			pass

		# send a signal to the GUI thread with the time used to compute the hull
		self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
