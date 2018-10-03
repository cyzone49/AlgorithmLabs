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
			print(str(myList.index(p)) + " - " + str(p))
			# print(angle)

	def drawFromTop(self, lst, top):
		polygon = [QLineF( lst[i], top) for i in range(len(lst))]
		assert( type(polygon) == list and type(polygon[0]) == QLineF )
		self.show_hull.emit(polygon,(255,0,0))

	def solveHull(self, lst):
		if len(lst) < 4:
			result = lst
		result = self.makeHull(lst)

		print("\n\n\nFINISHED solving.\nEnding result goes in order:")
		self.printPoints(result)

		polygon = [QLineF( result[i], result[(i+1)%len(result)]) for i in range(len(result))]
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

	# def ff(self, lst, )

	def mergeHulls(self, LHS, RHS):
		# print("\nLHS = " + str(LHS))
		# print("\nRHS = " + str(RHS))
		if len(LHS) == 1 & len(RHS) == 1:
			result = LHS + RHS
			return result
		elif ( (len(LHS) == 1) & (len(RHS) == 2) ) | ( (len(LHS) == 2) & (len(RHS) == 1) ):
			result = LHS + RHS
			result = self.sortClockwise(result)
			return result
		else:
			print("\n\nSTARTING mergeHulls. The two sides are")
			print("LHS = " + str(LHS) + " OF SIZE " + str(len(LHS)))
			print("RHS = " + str(RHS) + " OF SIZE " + str(len(RHS)))


			LHS_up,RHS_up = self.findUpperTangent(LHS,RHS,self.findRightMost(LHS), self.findLeftMost(RHS))
			print("tangent upper include points:")
			print(str(LHS_up) + " index = " + str(LHS.index(LHS_up)))
			print(str(RHS_up) + " index = " + str(RHS.index(RHS_up)))
			print("\n")

			LHS_down,RHS_down = self.findLowerTangent(LHS,RHS,self.findRightMost(LHS), self.findLeftMost(RHS))
			print("tangent Lower include points:")
			print(str(LHS_down) + " index = " + str(LHS.index(LHS_down)))
			print(str(RHS_down) + " index = " + str(RHS.index(RHS_down)))
			print("\n")

			#TODO: merge with found points
			if LHS.index(LHS_down) > LHS.index(LHS_up):
				print("\tLHS_down index > LHS_up index (Up comes before Down)\n\t=>> current = [0 -> up -> down -> end].\n\t\t[down:0:up]\n")
				print("\t\t[down:0] = " + str( LHS[ LHS.index(LHS_down):len(LHS) ]))
				print("\t\t[0:up] = " + str( LHS[ 0:LHS.index(LHS_up)+1 ] ) )
				leftHull = LHS[ LHS.index(LHS_down):len(LHS) ] + LHS[ 0:LHS.index(LHS_up)+1]
			else:
				print("\tLHS_down index < LHS_up index (Down comes before Up)\n\t=>> current = [0 -> down -> up -> end].\n\t\t[down:up]\n")
				print("\t\t[down:up] = " + str(LHS[ LHS.index(LHS_down):LHS.index(LHS_up)+1 ]))
				leftHull = LHS[ LHS.index(LHS_down):LHS.index(LHS_up)+1 ]


			if RHS.index(RHS_up) > RHS.index(RHS_down):
				print("\tRHS_up index > RHS_down index (Down comes before Up)\n\t=>> current = [0 -> down -> up -> end].\n\t\t[up:0:down]\n")
				print("\t\t[up:0] = " + str(RHS[ RHS.index(RHS_up):len(RHS) ]))
				print("\t\t[0:down] = " + str(RHS[ 0:RHS.index(RHS_down)+1 ]) )
				rightHull = RHS[ RHS.index(RHS_up):len(RHS) ] + RHS[ 0:RHS.index(RHS_down)+1]
			else:
				print("\tRHS_up index < RHS_down index (Up comes before Down)\n\t=>> current = [0 -> up -> down -> end].\n\t\t[up:down]\n")
				print("\t\t[up:down] = " + str( RHS[ RHS.index(RHS_up):RHS.index(RHS_down)+1 ] ) )
				rightHull = RHS[ RHS.index(RHS_up):RHS.index(RHS_down)+1 ]

			print("leftHull = " + str(leftHull))
			print("rightHull = " + str(rightHull))

			result = leftHull + rightHull

		print("\nEnding mergeHulls. Result = " + str(result) + "\n\n\n\n\n\n\n")
		return result

	def findUpperTangent(self, LHS, RHS, LHS_right, RHS_left):
		cont = True

		LHS = LHS[::-1] + LHS[::-1]
		RHS = RHS + RHS
		# print("\n\n\n\nPREPARE TO FIND UPPER TANGENT\n")
		# print("LHS = " + str(LHS))
		# print("RHS = " + str(RHS))
		#set current points of tangent, starting with leftmost and rightmost
		LHS_current = LHS_right
		RHS_current = RHS_left

		while cont == True:
			# print("\n\n\n\n\n\nINTO CONT in UPPER TANGENT")
			continueRHS = True
			continueLHS = True


			for i in range( RHS.index(RHS_current) + 1, len(RHS)): #index of first occurence
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( LHS_current, RHS[i] )
				# print("connect LHS right -> RHS at i = " + str(i))
				# print("prev_angle = " + str(prev_angle))
				# print("current angle = " + str(angle) + "\n\tbetween:\n\t\t" + str(LHS_current) + " and\n\t\t" + str(RHS[i]))
				# print( str(angle > prev_angle) + "\n\n")

				if angle > prev_angle: #angle increases
					RHS_current = RHS[i]
					prev_angle = angle
					continueLHS = True
					# print("RHS_current CHANGED: now is = " + str(RHS_current) + "\n")
				else:
					# print("RHS no longer changing\n")
					continueRHS = False
					break

			for i in range( LHS.index(LHS_current) + 1, len(LHS) ):
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( RHS_current, LHS[i] )
				# print("connect RHS left -> LHS")
				# print("prev_angle = " + str(prev_angle))
				# print("current angle = " + str(angle))

				if angle < prev_angle:
					LHS_current = LHS[i]
					prev_angle = angle
					continueRHS = True
					# print("LHS_current CHANGED: now is = " + str(LHS_current) + "\n")
				else:
					# print("LHS no longer changing\n")
					continueLHS = False
					break

			cont = continueLHS | continueRHS

			# print("cont now is " + str(cont))

		return LHS_current, RHS_current

	def findLowerTangent(self, LHS, RHS, LHS_right, RHS_left):
		cont = True

		RHS = RHS[::-1] + RHS[::-1]
		LHS = LHS + LHS
		# print("\n\n\n\nPREPARE TO FIND LOWER TANGENT\n")
		# print("LHS = " + str(LHS))
		# print("RHS = " + str(RHS))
		#set current points of tangent, starting with leftmost and rightmost
		LHS_current = LHS_right
		RHS_current = RHS_left

		while cont == True:
			# print("\n\n\n\n\n\nINTO CONT in LOWER TANGENT")
			continueRHS = True
			continueLHS = True


			for i in range( RHS.index(RHS_current) + 1, len(RHS)): #index of first occurence
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( LHS_current, RHS[i] )
				# print("connect LHS right -> RHS at i = " + str(i))
				# print("prev_angle = " + str(prev_angle))
				# print("current angle = " + str(angle) + "\n\tbetween:\n\t\t" + str(LHS_current) + " and\n\t\t" + str(RHS[i]))
				# print( str(angle < prev_angle) + "\n\n")


				if angle < prev_angle: #angle increases
					RHS_current = RHS[i]
					prev_angle = angle
					continueLHS = True
					# print("RHS_current CHANGED: now is = " + str(RHS_current) + "\n")
				else:
					# print("RHS no longer changing\n")
					continueRHS = False
					# if i == RHS.index(RHS_current) + 1:
					# 	print("NO CHANGE!! BREAKING OUT of cont. FOUND \n")
					# 	cont = False
					break

			for i in range( LHS.index(LHS_current) + 1, len(LHS) ):
				prev_angle = self.findSlope( LHS_current, RHS_current)
				# get slope of current on LHS and next on RHS
				angle = self.findSlope( RHS_current, LHS[i] )
				# print("connect RHS left -> LHS")
				# print("prev_angle = " + str(prev_angle))
				# print("current angle = " + str(angle))

				if angle > prev_angle:
					LHS_current = LHS[i]
					prev_angle = angle
					continueRHS = True
					# print("LHS_current CHANGED: now is = " + str(LHS_current) + "\n")
				else:
					# print("LHS no longer changing\n")
					continueLHS = False
					break

			cont = continueLHS | continueRHS

			# print("cont now is " + str(cont))

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
		# self.drawFromTop(sorted_points, up_y)

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
