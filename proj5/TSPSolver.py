#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))




import time
import numpy as np
from TSPClasses import *
import heapq
import itertools
import math
from queue import PriorityQueue
import copy
import functools



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution,
		time spent to find solution, number of permutations tried during search, the
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	def printCities(self, cities):
		print("\n************** Printing cities **************")
		for city in cities:
			print("\n -  name        = " + str(city._name))
			print(" -  coordinates = ( " + str(city._x) + ", " + str(city._y) + " )")
			print(" -  elevation   = " + str(city._elevation))
			print(" -  index       = " + str(city._index))
			self.printCost(city)


	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)

		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this
		algorithm</returns>
	'''

	#TODO: modify to implement greedy approach.
	def greedy( self,time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)

		print("\n\n*********************** GREEDY *************************\n")

		# print("ncities ( " + str(ncities) + " ) --- type: " + str(type(cities)) + "\n")
		# self.printCities(cities)

		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		# while not foundTour and time.time()-start_time < time_allowance:
		# 	# create a random permutation
		# 	perm = np.random.permutation( ncities )
		# 	# print("\tperm = " + str(perm))
		# 	route = []
		# 	# Now build the route using the random permutation
		# 	for i in range( ncities ):
		# 		route.append( cities[ perm[i] ] )
		# 	bssf = TSPSolution(route)
		# 	count += 1
		# 	if bssf.cost < np.inf:
		# 		# Found a valid route
		# 		foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time		#
		# print("ncities ( " + str(ncities) + " ) --- type: " + str(type(cities)) + "\n")
		# self.printCities(cities
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results




	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints:
		max queue size, total number of states created, and number of pruned states.</returns>
	'''

	def printQueue( self, q ):
		if len(q.queue) == 0:
			print("\n\nEmpty Queue!\n")
			return

		print("\nPrinting queue: len = " + str(len(q.queue)) + ":")
		for i in q.queue:
			print(str(i.item))

	def printCost(self, city):
		print("\n\tCost to other cities from city " + str(city._name))
		for dest in city._scenario._cities:
			print("\t -> " + str(dest._name) + " = " + str(city.costTo(dest)))

	# for now gen by running defaultRandomTour function
	def genBSSF( self, times ):
		BSSF = 99999999
		if times > 100:
			times = 100
		while times > 0:
			times -= 1
			curr = self.defaultRandomTour()['cost']
			if curr < BSSF:
				BSSF = curr
		return BSSF

	def genMatrix( self, cities ):
		m = np.zeros((len(cities), len(cities)))
		for src in cities:
			for dest in src._scenario._cities:
				m[ src._index, dest._index ] = src.costTo(dest)
		return m

	def reduceCost( self, m ):
		# print("\nStarting reduceCost().......")
		bound = 0
		# print("starting m =\n" + str(m))

		# d = [r for r in m if not np.all(np.isinf(r)) ]

		for i in range(0, m.shape[0]):
			if not np.all(np.isinf(m[i])):
				m[i], tmp = self.reduceList( m[i] )
				bound += tmp

		# print("\ndone with row. curr_m =\n" + str(m))
		# print("bound = " + str(bound))
		for i in range(0, m.shape[1]):
			if not np.all(np.isinf(m[:,i])):
				m[:,i], tmp = self.reduceList( m[:,i] )
				bound += tmp
		# print("\ndone with row and col. curr_m =\n" + str(m))
		# print("\treturning from reduceCost().. with bound = " + str(bound))
		return m, bound

	def reduceList( self, lst ):
		if 0 not in lst:
			newLst = []
			minVal = min(lst)
			for i in range(0, len(lst)):
				newLst.append(lst[i] - minVal)
			return newLst, minVal
		else:
			return lst, 0

	class State:
		def __init__( self, route, cost, bound, matrix ):
			self._route = route
			self._cost = cost
			self._bound = bound
			self._matrix = matrix

		def __str__( self ):
			ret = "\nSTATE: "
			ret += "route" + self.printRoute(self._route)
			ret += "\ncost  = " + str(self._cost)
			ret += "\nbound = " + str(self._bound)
			ret += "\nreduced cost matrix:\n" + str(self._matrix)
			return ret

		def getRoute( self ):
			return self._route

		def getCost( self ):
			return self._cost

		def getBound( self ):
			return self._bound

		def getMatrix( self ):
			return self._matrix

		def printRoute( self, route ):
			# print("printing route in STATE.....")
			ret = " [ "
			for city_name in route:
				ret += str(city_name)
				if route.index(city_name) != (len(route)-1):
					ret += ", "
			ret += " ]"
			return ret



	@functools.total_ordering
	class Prioritize:

		def __init__(self, priority, item):
			self.priority = priority
			self.item = item

		def __eq__(self, other):
			return self.priority == other.priority

		def __lt__(self, other):
			print("\t\t\t\tPrioritize: --- self.priority = " + str(self.priority) + ", --- other.priority = " + str(other.priority))
			return self.priority < other.priority
			# if self.priority < other.priority:
			# 	print("\t\t\t\t\tso returning true")
			# 	return True
			# elif self.priority > other.priority:
			# 	print("\t\t\t\t\tso returning false")
			# 	return False
			# else:
			# 	print("\t\t\t\tPrioritize: --- self.item._cost = " + str(self.item._cost) + ", --- other.item._cost = " + str(other.item._cost))
			# 	return self.item._cost < other.item._cost





	def explore( self, q, BSSF ):
		print("\n\n\n\nStarting explore()...............")

		parent_state = q.get().item

		print("\n\t ~~PARENT STATE~~ \n")
		print(str(parent_state))

		# self.printQueue(q)

		# for debug purposes
		parent_city = parent_state.getRoute()[-1]
		print("\t current parent_city ( to leave from ) = " + str(parent_city) + " of type " + str(type(parent_city)))
		#######

		parent_city = next((city for city in self._scenario.getCities() if city._name == parent_city), None)
		# print("current parent_city = " + str(parent_city) + " of type " + str(type(parent_city)))
		# print("\tCurrent number of cities already traveled in this route: " + str(len(parent_state._route)))


		for city in [ c for c in self._scenario.getCities() if parent_city.costTo(c) != np.inf ]:
			if city._name not in parent_state._route:
				print("\n\tTraveled to " + str(city._name) + " for the first time~ ")
				m =  copy.deepcopy( parent_state._matrix )
				m[ :,city._index ]      = [ np.inf ] * m.shape[0]
				m[ parent_city._index ] = [ np.inf ] * m.shape[1]
				m[ city._index, parent_city._index ] = np.inf
				m, new_bound = self.reduceCost(m)
				new_bound += parent_state._bound
				if new_bound < BSSF:
					new_route = list( parent_state.getRoute() )
					new_route.append(city._name)
					new_cost = parent_state.getCost() + parent_city.costTo( city )
					new_State = self.State( new_route,  new_cost, new_bound, m)

					if len(new_route) == len(self._scenario.getCities()):

						cost_back = city.costTo(self._scenario.getCities()[0])
						if cost_back != np.inf:
							print("~~~~~~YESSSSSS~~~~~~~~ FOUND NEW SOLUTION~~~~~~~~~~~~")
							print(str(new_State))
							BSSF = new_cost + cost_back
							new_queue = PriorityQueue()
							for state in q.queue:
								# print(str(state))
								if state.item._bound < BSSF:
									# q.remove(state)
									new_queue.put(self.Prioritize(state.item._bound, state.item))

							return new_queue, BSSF, False
						else:
							print("~~~~~FALSE ALARM~~~~~~. No way back")
					else:
						# print("\n\nCurrent queue is: ")
						# self.printQueue(q)
						print("\t\tnew_route[" + str(len(new_route)) + "] = " + str(new_route))
						print("\t\tnew_cost = " + str(new_cost))
						print("\t\tnew_bound = " + str(new_bound))
						print("\t\tnew_matrix =\n" + str(m))
						# print("\n\n\t*********Preparing to PUT***********\n")
						# print("\n\tNo problem creating new STATE. new State is :\n" + str(dddd))
						# self.printQueue(q)

						q.put( self.Prioritize(new_bound, new_State) )
						print("\n\tSucceeded put() op.")

						# q.put( ( new_bound, self.State( new_route,  new_cost, new_bound, m) ) )
						# self.cities_traveled += 1

			# else:
			# 	print("\n\tAlready travled to city " + str(city._name) + " on this route! ")

		return q, BSSF, True




	def branchAndBound( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		# self.printCities(cities)
		q = PriorityQueue()

		# bssf == TSPSolution( route )
		# print("BSSF = " + str(BSSF))

		working_BSSF = self.genBSSF( ncities )   # init BSSF
		route = [ cities[0]._name ]      # route of init state -- contains NAMES of cities
		cost  = 0                        # cost  of init state
		count = 0                        # number of states passed
		print("first matrix before reducing cost\n" + str(self.genMatrix(cities)))
		newM, bound = self.reduceCost( self.genMatrix( cities ) )
		                                 # bound and RCM of init state

		q.put(self.Prioritize(bound, self.State( route, cost, bound, newM )))

		# q.put((12, self.State( [ cities[0], cities[1] ], cities[0].costTo(cities[1]), 12, np.zeros((5,5)))))
		# self.printQueue(q)



		start_time = time.time()
		while not q.empty() and time.time()-start_time < time_allowance:
			print("\n\n\n\n\nQueue is NOT empty! keep calling explore() with working_BSSF = " + str(working_BSSF))
			q,working_BSSF,route = self.explore( q, working_BSSF )

			print("\n\nOut of list of cities in from parent_city.\n\tworking_BSSF = " + str(working_BSSF))
			# print("\nprinting parent state here\n")
			# print(str(parent_state))
			print("\nnew Queue is: ")
			self.printQueue(q)
			if route != None:
				bssf = TSPSolution( route )
				break



			# bssf = TSPSolution(route)
			# count += 1
			# if bssf.cost < np.inf:
			# 	# Found a valid route
			# 	foundTour = True
		print("\n\nOut of While Loop")
		end_time = time.time()


		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time		#
		# print("ncities ( " + str(ncities) + " ) --- type: " + str(type(cities)) + "\n")
		# self.printCities(cities
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results






	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution,
		time spent to find best solution, total number of solutions found during search, the
		best solution found.  You may use the other three field however you like.
		algorithm</returns>
	'''

	def fancy( self,time_allowance=60.0 ):
		pass
