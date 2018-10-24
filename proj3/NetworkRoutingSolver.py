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
    def printQueue( self, lst ):
        for i in lst:
            print("\t" + str(i.node_id) + " ::= " + str(i) )
            # for n in i.neighbors:
            #     print("\t\t " + str(n) )

    def printDict( self ):
        print("Printing dict:")
        for k,v in self.result.items():
            print("\n\tkey = " + str(k.node_id) )
            print("\tvalue is:\tdist = " + str(v.dist) + "\n\t\t\tprev(id) = " + str(v.prev))

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
        # TODO: RETURN THE SHORTEST PATH FOR destIndex
        #       INSTEAD OF THE DUMMY SET OF EDGES BELOW
        #       IT'S JUST AN EXAMPLE OF THE FORMAT YOU'LL
        #       NEED TO USE
        path_edges = []
        total_length = 0
        # node = self.network.nodes[self.source]
        # edges_left = 3

        print("\nIN getShortestPath()")
        print("src = " + str(self.source))
        print("dest = " + str(self.dest))
        # self.printDict()

        node = self.network.nodes[ self.dest ]
        prev_id = self.result[ node ].prev.node_id
        total_length = self.result[ node ].dist

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
        # TODO: RUN DIJKSTRA'S TO DETERMINE SHORTEST PATHS.
        #       ALSO, STORE THE RESULTS FOR THE SUBSEQUENT
        #       CALL TO getShortestPath(dest_index)
        print("\n\n\n\nDONE running DIJKSTRA")
        self.printDict()
        t2 = time.time()
        return (t2-t1)

    def runDijkstra( self, srcIndex, use_heap=False ):
        print("use_heap = " + str(use_heap))
        #set up steps: set up self.result (dict) and set s.dist = 0
        for node in self.network.nodes:
            self.result[ node ] = self.NodeStructure( None, None )
        self.result[ self.network.nodes[ srcIndex ] ].setDist( 0 )

        # printout -- debug
        # print("result -- type " + str(type(self.result)) + " -- initialized  is ")
        # self.printDict()

        if use_heap == False:
            print("\nUSING Array\n********************************************************************\n")
            queue = self.makeQueue( srcIndex, False )
            # iter = -1
            # prev_queue_len = len(queue)
            while len( queue ) > 0:
                # iter += 1
                # print("\n(" + str(iter) + ") ******************************* in While loop:\n")
                #
                # self.printDict()
                # print("current_queue is ")
                # self.printQueue(queue)

                curr_node, queue = self.deleteMin( queue, False)
                # print("\nafter deleting Min:")
                # print("\tqueue_Length = " + str(len(queue)))
                # print("\tin Array. curr_node = " + curr_node.__str__())

                if curr_node == None:
                    print("No more steps could be taken from here")
                    # self.printDict()
                    break
                curr_neighbors = [ edge.dest.node_id for edge in curr_node.neighbors]

                # for each node in list of neighbors of curr_node (at first: src, then: just deleted from queue )
                for node in [ node for node in queue if node.node_id in curr_neighbors ]:
                    curr_length = next( (x for x in curr_node.neighbors if x.dest.node_id == node.node_id), None).length
                    # print("\t\tnode_id = " + str(node.node_id) + " with length = " + str(self.result[ node ].dist))

                    if self.result[ node ].dist==None :
                        # print("\t\tNONE. dist( node ) == None ")
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    elif self.result[ node ].dist > ( self.result[ curr_node ].dist + curr_length ):
                        # print("\t\tYES. dist( node ) = " + str(self.result[ node ].dist) + " > dist( curr_node ) + l( curr_node, node ) = " + str(d))
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    else:
                        # print("\t\tNO")
                        pass
        else:
            print("\nUSING HEAP\n********************************************************************\n")
            # queue will just be a list structure
            queue = self.makeQueue( srcIndex, True )
            print("before doing anything: printing queue: ")
            self.printQueue( queue )
            print("len queue = " + str(len(queue)))

            # self.keys = [None] * len( queue )
            #
            # for i in range(len(self.keys)):
            #     print("\t" + str(i) + ": " + str(self.keys[i]))

            while len(queue) > 0:
                print("in while loop")

                curr_node, queue = self.deleteMin( queue, True )

                # debug
                print("finish deleteMin")
                print("\tcurr_node = " + str(curr_node.node_id ))
                print("\tqueue: ")
                self.printQueue( queue )

                if curr_node == None:
                    print("No more steps could be taken from here")
                    # self.printDict()
                    break
                curr_neighbors = [ edge.dest.node_id for edge in curr_node.neighbors]

                # for each node in list of neighbors of curr_node (at first: src, then: just deleted from queue )
                for node in [ node for node in queue if node.node_id in curr_neighbors ]:
                    curr_length = next( (x for x in curr_node.neighbors if x.dest.node_id == node.node_id), None).length
                    # print("\t\tnode_id = " + str(node.node_id) + " with length = " + str(self.result[ node ].dist))

                    if self.result[ node ].dist==None :
                        # print("\t\tNONE. dist( node ) == None ")
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    elif self.result[ node ].dist > ( self.result[ curr_node ].dist + curr_length ):
                        # print("\t\tYES. dist( node ) = " + str(self.result[ node ].dist) + " > dist( curr_node ) + l( curr_node, node ) = " + str(d))
                        self.result[ node ].dist = self.result[ curr_node ].dist + curr_length
                        self.result[ node ].prev = curr_node
                    else:
                        # print("\t\tNO")
                        pass

                    queue = self.decreaseKey( node, queue )
                self.printDict()


    def decreaseKey( self, node, queue ):
        parent_index = queue.index( node )
        queue = self.bubbleUp( node, queue )
        print("\tDone bubbling up ")
        print("Finish decreaseKey. curren queue = ")
        self.printQueue( queue )
        return queue



    def deleteMin( self, queue, use_heap=False ):
        if ( use_heap == False ):
            # print("\nDeleting Min in Array")
            min_dist = 1000000000000
            min_node = None
            for node in queue:
                if self.result[ node ].dist != None:
                    if self.result[ node ].dist < min_dist:
                        min_node = node
                        min_dist = self.result[ node ].dist

            new_queue = [node for node in queue if node != min_node ]
            return min_node, new_queue
        else:
            print("\nDeleting Min in Heap")
            print("queue before deleteMin")
            self.printQueue( queue )
            min_dist = 1000000000000
            min_node = queue.pop(0)
            print("queue after popping top node = " + str(min_node.node_id))
            self.printQueue( queue )

            # precaution: if top of heap does not have a dist, no where else to run
            if self.result[ min_node ].dist == None:
                print("Done. in DeleteMin of Heap")
                return None, queue

            if ( len(queue) == 0 ):
                print("Finish with entire queue. returning")
                return min_node, queue

            # move last node to the top of heap queue
            queue.insert( 0, queue.pop() )
            queue = self.bubbleDown( queue )
            print("\tDone bubbling down\n ")

            return min_node, queue

    def bubbleDown( self, queue ):
        print("\tat Bubble Down\n")
        self.printQueue( queue )
        # self.printDict()
        index = 0
        cont = True
        while (cont):
            print("\tCurrent node.node_id = " + str( queue[ index ].node_id ) )
            has_left_child = False
            has_right_child = False

            # make sure queue[ index ] node has child(ren)
            left_child_index = index * 2 + 1
            if left_child_index < len( queue ):
                has_left_child = True
                print("\tleftChild.node_id = " + str(queue[ left_child_index ].node_id ))

            right_child_index = index * 2 + 2
            if right_child_index < len( queue ):
                has_right_child = True
                print("\trightChild.node_id = " + str( queue[ right_child_index ].node_id ) )

            if has_left_child == False and has_right_child == False:
                print("\tcurrent node has no children")
                cont = False
            elif has_left_child == True and has_right_child == False:
                queue, index = self.swap( left_child_index, index, queue )
            elif has_left_child == False and has_right_child == True:
                queue, index = self.swap( right_child_index, index, queue )
            else:
                test_dist_result = self.testDist( left_child_index, right_child_index, queue )

                if test_dist_result == self.result[ queue[ left_child_index ] ].dist:
                    print("\n\tswapping with left")
                    queue, index = self.swap( left_child_index, index, queue )
                elif test_dist_result == self.result[ queue[ right_child_index ] ].dist:
                    print("\n\tswapping with right")
                    queue, index = self.swap( right_child_index, index, queue )
                else:
                    print("\n\tcannot swap. testDist returns -1 => both left and right have no Dist")
                    cont = False

        return queue

    def bubbleUp( self, node , queue ):
        print("\n\n\tAt Buble Up\n")
        index = queue.index( node )
        print("\t\tcurrent node is: " + str(node.node_id))
        print("\t\tdist of current node is " + str(self.result[ node ].dist))
        print("\t\tindex of current node in queue is: " + str(index))


        cont = True
        c = 4
        while ( cont ):
            print("\n\t\tIn while loop of bubble up")
            if index == 0:
                print("\t\talready at root.")
                return queue

            print("\t\tCurrent node = " + str( queue[ index ].node_id ) + " of index " + str(index))
            parent_index = math.ceil( index / 2 ) - 1
            print("\t\tCurrent parent node = " + str( queue[ parent_index ].node_id ) )

            if (self.result[ queue[ parent_index ] ].dist == None ) or (self.result[ queue[ parent_index ] ].dist > self.result[ queue[ index ] ].dist) :
                print("\t\tYes. dist(parent) = " + str( self.result[ queue[ parent_index ] ].dist ) + " > " + str( self.result[ queue[ index ] ].dist ) + " = curr dist"  )
                temp = queue[ index ]
                queue[ index ] = queue[ parent_index ]
                queue[ parent_index ] = temp
                index = parent_index
            else:
                print("\t\tNope " + str( self.result[ queue[ parent_index ] ].dist ) + " > " + str( self.result[ queue[ index ] ].dist ) + " = curr dist"  )
                cont = False

            c -= 1
            if c == 0:
                break

        return queue



    def swap( self, child_index, index, queue ):
        print("\n\tStarting swap: child_index in queue = " + str(child_index) + ", index in queue = " + str(index))
        child_dist = self.result[ queue[ child_index ] ].dist
        res_index = index
        if child_dist == None:
            print("\t\tAt Swap: queue[ child_index ] = " + str( queue[ child_index ].node_id ) + " has dist = None")
        else:
            # if current node's key/dist > its child's key/dist, swap
            curr_dist = self.result[ queue[ index ] ].dist
            print("\t\tcurr_node_id = " + str( queue[ index ].node_id ) + " with dist = " + str(curr_dist))

            if ( curr_dist == None ) or ( child_dist < self.result[ queue[ index ] ].dist ):
                print("\t\t\tchild_dist = " + str(child_dist) + " < index.dist = " + str(self.result[ queue[ index ] ].dist))
                temp = queue[ index ]
                queue[ index ] = queue[ child_index ]
                queue[ child_index ] = temp
                res_index = child_index
            else:
                print("\t\t\tchild_dist = " + str(child_dist) + " >= index.dist = " + str(self.result[ queue[ index ] ].dist))

        return queue, res_index

    def testDist( self, left_index, right_index, queue ):
        print("\n\tStarting testDist")
        left_dist = self.result[ queue[ left_index ] ].dist
        right_dist = self.result[ queue[ right_index ] ].dist
        res = -1
        if left_dist == None and right_dist == None:
            print("\t\tBoth left and right children have no dist")
        elif left_dist != None and right_dist == None:
            res = left_dist
            print("\t\tdone. res = " + str(res) + " = left_dist")
        elif left_dist == None and right_dist != None:
            res = right_dist
            print("\t\tdone. res = " + str(res) + " = right_dist")
        else:
            res = left_dist if left_dist < right_dist else right_dist
            print("\t\tdone. res = " + str(res) + " where both left and right children have dist")

        return res


    def makeQueue( self, srcIndex, use_heap=False ):
        # if (use_heap):
        #     queue = []
        #     root = self.Heap( self.network.nodes[ srcIndex ])
        # else:
        queue = []

        # add src node in first
        queue.append( self.network.nodes[ srcIndex ] )

        # add the rest of the nodes
        for node in [x for x in self.network.nodes if x != queue[0]]:
            queue.append( node )

        # print("\nArray Queue now: ")
        # self.printQueue( queue )

        return queue
