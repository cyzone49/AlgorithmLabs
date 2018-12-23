	def greedy2( self,time_allowance=60.0 ):

		results       = {}
		cities        = self._scenario.getCities()
		ncities       = len(cities)                    # number of cities
		foundTour     = False                          # bool -> tour is found
		passed_cities = []                             # list of cities not to be added as second city in route
		src_city      = self._scenario.getCities()[0]  # starting city (index = 0)

		start_time = time.time()

		# run while time permits and tour is not found
		while not foundTour and time.time()-start_time < time_allowance:

			# find and add a second city to the route
			# snd_city: nearest to src_city that is not in passed_cities list
			snd_city = self.findNearest( 0, passed_cities )
			route = [ src_city, snd_city ]

			# From current city, find and add the nearest city that has not been visited (in route)
			# until all cities are added
			while len( route ) != ncities:
				dest = self.findNearest( route[-1]._index, route )

				# Break out of loop when distances from current city to not-yet-travelled cities are all infinity
				if dest == None:
					# print("NONE HERE")
					break
				route.append( dest )

			# Catch failed routes: Add 2nd city to passed_cities list

			# case: route does not include all cities (break out prematurely due to last city not leave-able
			if len(route) != ncities:
				passed_cities.append( snd_city )
				# print("Out prematurely! passed_cities is: " + str(self.printCities(passed_cities)))
				continue

			# case: no cycle
			elif route[-1].costTo( src_city ) == np.inf:
				passed_cities.append( snd_city )
				# print("Not a cycle! passed_cities is: " + str(self.printCities(passed_cities)))

			else:
				# print("Found solution !")
				# print("OUT: route["+ str(len(route))+"] = ")
				# print(self.printCities(route))
				foundTour = True
				bssf = TSPSolution( route )

		end_time = time.time()

		if foundTour == False:
			return None

		# print("Finished while loop. route = " + str(self.printCities(route)))

		results['cost']   = bssf.cost if foundTour else math.inf
		results['time']   = end_time - start_time
		results['count']  = None
		results['soln']   = bssf
		results['max']    = None
		results['total']  = None
		results['pruned'] = None
		return results
