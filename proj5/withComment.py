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
		pass

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
		max_cost = np.inf
		BSSF = None

		# only try 100 times max
		if times > 14000:
			times = 14000

		while times > 0:
			times -= 1
			curr = self.defaultRandomTour()
			if curr['cost'] < max_cost:
				BSSF = curr
				max_cost = curr['cost']
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
		for i in range(0, m.shape[0]):
			if not np.all(np.isinf(m[i])):
				m[i], tmp = self.reduceList( m[i] )
				bound += tmp
		for i in range(0, m.shape[1]):
			if not np.all(np.isinf(m[:,i])):
				m[:,i], tmp = self.reduceList( m[:,i] )
				bound += tmp
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
			ret += "route" + self.printRoute()
			ret += "\ncost  = " + str(self._cost)
			ret += "\nbound = " + str(self._bound)
			# ret += "\nreduced cost matrix:\n" + str(self._matrix)
			return ret

		def getRoute( self ):
			return self._route

		def getCost( self ):
			return self._cost

		def getBound( self ):
			return self._bound

		def getMatrix( self ):
			return self._matrix

		def printRoute( self ):
			# print("printing route in STATE.....")
			ret = " [ "
			for city_name in self._route:
				ret += str(city_name)
				if self._route.index(city_name) != (len(self._route)-1):
					ret += ", "
			ret += " ]"
			return ret



	@functools.total_ordering
	class Prioritize:
		def __init__(self, priority, item):
			self.priority = priority
			self.item = item

		def __eq__(self, other):
			return self.priority[0] == other.priority[0]

		def __lt__(self, other):
			# print("calling LT")
			# return self.priority[0] < other.priority[0]
			# print("Prioritize: self.priority[0] = " + str(self.priority[0]) + " || other.priority[0] = " + str(other.priority[0]))
			if self.priority[0] > other.priority[0]:
				return True
			else:
			# 	print("Prioritize: self.priority[1] = " + str(self.priority[1]) + " || other.priority[1] = " + str(other.priority[1]))
				if self.priority[1] < other.priority[1]:
			# 		print("return True (less than)")
					return True
				else:
			# 		print("return False")
					return False
				# return self.priority[1] < other.priority[1]


	def extractRoute( self, route ):
		# print("\n\n\n\n\n~~~~~Starting extractRoute()~~~~~~~")
		result = []
		while len(route) != 0:
			# print("\troute = " + str(route))
			curr_letter = route.pop(0)
			city = next( ( x for x in self._scenario.getCities() if x._name == curr_letter ), None )
			# print(str(city._name))
			result.append(city)

		return result



	def explore( self, q, BSSF ):
		# print("\n\n\n\nStarting explore()...............")
		#
		# print("\n\n\n\nPRINT QUEUE")
		# self.printQueue(q)

		top = q.get()
		parent_state = top.item
		states = 0

		# print("\n\n\n\n ~~PARENT STATE~~ \n")
		# print(str(parent_state.printRoute()))
		# print("\n\n\n\nPRINT QUEUE")
		# self.printQueue(q)


		# parent_city = parent_state.getRoute()[-1]

		# grab city object of current city in route (last one in route)
		parent_city = next((city for city in self._scenario.getCities() if city._name == parent_state.getRoute()[-1]), None)

		# consider all cities that current city (parent_city) could lead to: cost(src -> dest)  != infinity)
		for city in [ c for c in self._scenario.getCities() if parent_city.costTo(c) != np.inf ]:
			# only consider cities that are not already in route
			if city._name not in parent_state._route:

				# calculate new reduced cost matrix and new lower bound
				m =  copy.deepcopy( parent_state._matrix )
				m[ :,city._index ]      = [ np.inf ] * m.shape[0]
				m[ parent_city._index ] = [ np.inf ] * m.shape[1]
				m[ city._index, parent_city._index ] = np.inf
				m, new_bound = self.reduceCost(m)
				new_bound += parent_state._bound

				# process current state IF its lower bound is less than current bssf cost
				if new_bound < BSSF:
					new_route = list( parent_state.getRoute() )
					new_route.append(city._name)
					new_cost = parent_state.getCost() + parent_city.costTo( city )
					new_State = self.State( new_route, new_cost, new_bound, m)
					states += 1

					# if all cities are now traveled too (present in route)
					if len(new_route) == len(self._scenario.getCities()):

						cost_back = city.costTo(self._scenario.getCities()[0])
						# check if current route creates a cycle (leads back to first city)
						if cost_back != np.inf:
							# print("\n\n\n\n~~~~~~~~~~~~~~FOUND NEW SOLUTION~~~~~~~~~~~~\n")
							# # print(new_State)
							# print("\tSolution cost  = " + str(new_State._cost + cost_back))
							# print("\tSolution route = " + str(new_State._route))

							# check to see if that solution improves the previous best solution (so far)
							if BSSF > ( new_State._cost + cost_back ):
								# print("\n\n\nUpdating BSSF!!!")
								BSSF = new_State._cost + cost_back
							return q, BSSF, new_State, states
					else:
						q.put( self.Prioritize( (len(new_State._route),new_bound), new_State) )

		return q, BSSF, None, states

	def prune( self, q, bssf ):
		print("Pruning...........")
		new_queue = PriorityQueue()
		for state in q.queue:
			if ( state.item._bound < bssf.cost ):
				new_queue.put(self.Prioritize( ( len( state.item._route ), state.item._bound ), state.item ) )
				# self.printQueue(new_queue)
		pruned = len(q.queue) - len(new_queue.queue)
		print("queue size decrease after prune by: " + str( pruned ) )
		# print("\n\n\n\nnew queue:")

		return new_queue, pruned


	def branchAndBound( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)


		# INIT
		init_solution = self.genBSSF( ncities * 500 )

		# init_solution = self.genBSSF( 1 )
		current_bssf_cost = init_solution['cost']   # init BSSF
		bssf 			  = init_solution['soln']
		q 				  = PriorityQueue()
		route       	  = [ cities[0]._name ]      	# route of init state -- contains NAMES of cities
		cost        	  = 0                        	# cost of init state
		count       	  = 0                        	# number of states passed
		foundTour   	  = False
		newM, bound 	  = self.reduceCost( self.genMatrix( cities ) )
		                                 				# bound and RCM of init state
		pruned = 0
		max    = 0
		total  = 0

		q.put(self.Prioritize( (len(bssf.route),bound), self.State( route, cost, bound, newM )))

		print("init bssf.cost = " + str(current_bssf_cost))
		# print(bssf)

		start_time = time.time()
		while not q.empty() and time.time()-start_time < time_allowance:

			q, re_bssf, solution_state, curr_states_num = self.explore( q, current_bssf_cost )
			if len(q.queue) > max:
				max = len(q.queue)
			total += curr_states_num

			# inc count of solutions when a solution is found
			if solution_state != None:
				count += 1
				foundTour = True

			# update bssf if applicable
			if re_bssf < current_bssf_cost:
				# print(" ~~ UPDATING BSSF based on solution state: ")
				current_bssf_cost = re_bssf
				route = self.extractRoute( solution_state._route )
				bssf = TSPSolution( route )

				# generate new queue by pruning states using a new bssf cost
				new_queue, curr_prune = self.prune( q, bssf )
				pruned += curr_prune

				# print("lenQueue = " + str(len(q.queue)))
			# else:
			# 	print(" nope ")


		end_time = time.time()


		print("\n\nOut of While Loop\n")
		if foundTour == True:
			print("YES --- foundTour = TRUE\n\n")
			print(str(len(q.queue)))
		else:
			print("NO  --- foundTour = FALSE\n\n")

		pruned += len(q.queue)

		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time		#
		# print("ncities ( " + str(ncities) + " ) --- type: " + str(type(cities)) + "\n")

		results['count'] = count
		results['soln'] = bssf
		results['max'] = max
		results['total'] = total
		results['pruned'] = pruned
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
# print("\n\n")
# print(" ~ Out of list of cities in from parent_city.\n\tcurrent_bssf_cost = " + str(current_bssf_cost) + "\n")
# print(" ~ New Queue is: ")
# self.printQueue(q)
