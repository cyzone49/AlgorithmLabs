#!/usr/bin/python3


from CS312Graph import *
import time
import math


class NetworkRoutingSolver:
    def __init__( self):
        pass

    def initializeNetwork( self, network ):
        assert( type(network) == CS312Graph )
        self.network = network

    result = dict()

    class NodeStructure:
        def __init__( self, new_dist, new_prev ):
            self.dist = new_dist
            self.prev = new_prev

        def setDist( self, new_dist ):
            self.dist = new_dist

        def setPrev( self, new_prev ):
            self.prev = new_prev

    def getShortestPath( self, destIndex ):
        self.dest = destIndex

        path_edges = []
        total_length = 0

        node = self.network.nodes[ self.dest ]

        if ( self.result[ node ].dist == None ):
            print("destination node is unreachable")
        else:
            prev_id = self.result[ node ].prev.node_id
            total_length = self.result[ node ].dist

            # trace back: from dest -> top using prev_node of each node being looked at
            # O(n)
            while node.node_id != self.source:
                # directed edge coming from node.prev -> node
                edge = next( (x for x in self.network.nodes[ prev_id ].neighbors if x.dest.node_id == node.node_id), None)
                path_edges.append( (edge.src.loc, edge.dest.loc, '{:.0f}'.format(edge.length)) )
                # set node to node.prev to trace back further
                node = self.network.nodes[ prev_id ]
                # prev_id is the id of prev( node )
                if node.node_id != self.source:
                    prev_id = self.result[ node ].prev.node_id




        return {'cost':total_length, 'path':path_edges}

    def computeShortestPaths( self, srcIndex, use_heap=False ):
        self.source = srcIndex
        t1 = time.time()
        self.runDijkstra( srcIndex, use_heap )
        t2 = time.time()
        return (t2-t1)

    # let n = |V|
    # Prority queue implementation:
    #     Array: T(n) = O( n + n**2 ) = O( n**2 ) = O( |V|**2 )
    #     Heap:  T(n) = O( n + nlog(n) ) = O( nlog(n) ) = O( (|V|+|E|)log(|V|) )
    def runDijkstra( self, srcIndex, use_heap=False ):

        # set up steps: set up look up dictionary self.result and set s.dist = 0
        # O(n) for going through every node
        for node in self.network.nodes:
            self.result[ node ] = self.NodeStructure( None, None )
        self.result[ self.network.nodes[ srcIndex ] ].setDist( 0 )

        # use ARRAY priority queue implementation
        # T(n) = O( n + n**2 ) = O( n**2 ) = O( |V|**2 )
        if use_heap == False:
            print("\tUSING Array")
            print("\n******************\n")
            queue = self.makeQueue( srcIndex, False ) # O(n)

            # run through at most n loops == |V| for each node in queue
            # => O( n * n ) = O( n**2 )
            while len( queue ) > 0:

                # O(n) -- go through entire queue list to return min
                curr_node, queue = self.deleteMin( queue, False)

                if curr_node == None:
                    # print("No more steps could be taken from here")
                    break

                curr_neighbors = [ edge.dest.node_id for edge in curr_node.neighbors]

                # loop through 3 times
                # for each node in list of neighbors of curr_node, calculate new distance (if applicable)
                # then update look up dictionary self.result accordingly
                for node in [ node for node in queue if node.node_id in curr_neighbors ]:
                    curr_length = next( (x for x in curr_node.neighbors if x.dest.node_id == node.node_id), None).length

                    # dictionary get and set items are O(1) on average in terms of n
                    if self.result[ node ].dist==None :
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    elif self.result[ node ].dist > ( self.result[ curr_node ].dist + curr_length ):
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    else:
                        pass
                    queue = self.decreaseKey( node, queue, False ) # O(1) -- don't do anything

        # use HEAP priority queue implementation
        # T(n) = O( n*log(n) + n ) = O( n*log(n) )
        else:
            print("\tUSING Heap")
            print("\n******************\n")
            # queue will just be a list structure
            # O(n) -- just put all nodes in the queue/list with srcIndex node on top (root)
            queue = self.makeQueue( srcIndex, True )

            # at most n -- go through entire queue
            # O( n * ( (log(n) + 3 * log(n) ) ) = O( n*log(n) )
            while len(queue) > 0:

                # O( log(n) ) -- after getting root, remove it from heap ( O(1) ),
                # put last node -> top. It takes at most log(n) to bubbleDown
                # (worst case: all the way from top->bottom level => log(n) swaps )
                curr_node, queue = self.deleteMin( queue, True )

                if curr_node == None:
                    # print("No more steps could be taken from here")
                    break

                curr_neighbors = [ edge.dest.node_id for edge in curr_node.neighbors]

                # loop through 3 times
                # for each node in list of neighbors of curr_node, calculate new distance (if applicable)
                # then update look up dictionary self.result accordingly
                for node in [ node for node in queue if node.node_id in curr_neighbors ]:
                    curr_length = next( (x for x in curr_node.neighbors if x.dest.node_id == node.node_id), None).length

                    if self.result[ node ].dist==None :
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    elif self.result[ node ].dist > ( self.result[ curr_node ].dist + curr_length ):
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    else:
                        pass

                    # O( log(n) ) -- bubbleUp takes O( log(n) ) for log(n) potential swap upward
                    queue = self.decreaseKey( node, queue, True )


    # O(n) -- create a list and insert all nodes into it
    # heap is in list structure so about actually is the same big-O
    def makeQueue( self, srcIndex, use_heap=False ):
        queue = []
        # add src node in first
        queue.append( self.network.nodes[ srcIndex ] )
        # add the rest of the nodes
        for node in [x for x in self.network.nodes if x != queue[0]]:
            queue.append( node )
        return queue

    # O(log(n)) -- bubbleUp() takes O(log(n)) and is essentially the entire function
    def decreaseKey( self, node, queue, use_heap=True ):
        #parent_index = queue.index( node )
        if use_heap == True:
            queue = self.bubbleUp( node, queue )
        return queue


    def deleteMin( self, queue, use_heap=False ):
        # O(n) -- go through entire queue list to return min
        if ( use_heap == False ):
            min_dist = 1000000000000
            min_node = None
            for node in queue:
                if self.result[ node ].dist != None:
                    if self.result[ node ].dist < min_dist:
                        min_node = node
                        min_dist = self.result[ node ].dist

            new_queue = [node for node in queue if node != min_node ]
            return min_node, new_queue
        # O( log(n) )
        else:
            min_dist = 1000000000000
            min_node = queue.pop(0) #O(1) -- pop first item -- root

            # precaution: if top of heap does not have a dist, no where else to run
            if self.result[ min_node ].dist == None:
                return None, queue

            if ( len(queue) == 0 ):
                return min_node, queue

            # move last node to the top of heap queue
            # O(1) -- insert right at the top of list
            queue.insert( 0, queue.pop() )
            # O( log(n) ) -- possible log(n) swap downward through the levels of heap
            queue = self.bubbleDown( queue )

            return min_node, queue

    # O(log(n)) -- from top node, compare to smaller of two children and make necessary swap
    # each swap takes O(1) interms of n
    # each swap move node down 1 level, worst case = top -> bottom => at most log(n) swaps
    def bubbleDown( self, queue ):
        index = 0
        cont = True
        while (cont):
            has_left_child = False
            has_right_child = False

            # make sure queue[ index ] node has child(ren)
            left_child_index = index * 2 + 1
            if left_child_index < len( queue ):
                has_left_child = True

            right_child_index = index * 2 + 2
            if right_child_index < len( queue ):
                has_right_child = True

            if has_left_child == False and has_right_child == False:
                cont = False
            elif has_left_child == True and has_right_child == False:
                temp = index
                queue, index = self.swap( left_child_index, index, queue )
                # if index did not change -> did not swap! => Done Bubble Down
                if temp == index:
                    cont = False
            elif has_left_child == False and has_right_child == True:
                temp = index
                queue, index = self.swap( right_child_index, index, queue )
                # if index did not change -> did not swap! => Done Bubble Down
                if temp == index:
                    cont = False
            else:
                test_dist_result = self.testDist( left_child_index, right_child_index, queue )

                if test_dist_result == self.result[ queue[ left_child_index ] ].dist:
                    temp = index
                    queue, index = self.swap( left_child_index, index, queue )
                    # if index did not change -> did not swap! => Done Bubble Down
                    if temp == index:
                        cont = False
                elif test_dist_result == self.result[ queue[ right_child_index ] ].dist:
                    temp = index
                    queue, index = self.swap( right_child_index, index, queue )
                    # if index did not change -> did not swap! => Done Bubble Down
                    if temp == index:
                        cont = False
                else:
                    cont = False

        return queue

    # O(log(n)) -- similar to Bubble Down
    # -- check if you could swap (child and its parent)
    # worst case: go from bottom level -> top ==> log(n) swaps
    def bubbleUp( self, node , queue ):
        index = queue.index( node )
        cont = True

        while ( cont ): #worst case: log(n) loops
            if index == 0:
                return queue

            parent_index = math.ceil( index / 2 ) - 1
            if (self.result[ queue[ parent_index ] ].dist == None ) or (self.result[ queue[ parent_index ] ].dist > self.result[ queue[ index ] ].dist) :
                temp = queue[ index ]
                queue[ index ] = queue[ parent_index ]
                queue[ parent_index ] = temp
                index = parent_index
            else:
                cont = False

        return queue


    # check conditions between parent and child to be swapped.
    # if both have dist != None (infinity) then perform swap if necessary
    # O(1) #in terms of n = number of nodes
    def swap( self, child_index, index, queue ):
        child_dist = self.result[ queue[ child_index ] ].dist
        res_index = index
        if child_dist != None:
            # if current node's key/dist > its child's key/dist, swap
            curr_dist = self.result[ queue[ index ] ].dist

            if ( curr_dist == None ) or ( child_dist < self.result[ queue[ index ] ].dist ):
                temp = queue[ index ]
                queue[ index ] = queue[ child_index ]
                queue[ child_index ] = temp
                res_index = child_index

        return queue, res_index

    # O(1) -- dict lookup as hash table takes constant time on average
    # test if both children have distance != None (infinity -- not reachable)
    # by look up using dict structure self.result
    def testDist( self, left_index, right_index, queue ):
        left_dist = self.result[ queue[ left_index ] ].dist
        right_dist = self.result[ queue[ right_index ] ].dist
        res = -1
        if left_dist == None and right_dist == None:
            return res
        elif left_dist != None and right_dist == None:
            res = left_dist
        elif left_dist == None and right_dist != None:
            res = right_dist
        else:
            res = left_dist if left_dist < right_dist else right_dist

        return res
