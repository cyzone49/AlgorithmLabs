#!/usr/bin/python3


from CS312Graph import *
import time


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
            for n in i.neighbors:
                print("\t\t " + str(n) )

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
        t2 = time.time()
        return (t2-t1)

    def runDijkstra( self, srcIndex, use_heap=False ):
        # self.result = dict()

        for node in self.network.nodes:
            self.result[ node ] = self.NodeStructure( None, None )

        self.result[ self.network.nodes[ srcIndex ] ].setDist( 0 )

        # printout -- debug
        # print("result -- type " + str(type(self.result)) + " -- initialized  is ")
        # self.printDict()

        if ( use_heap ):
            print("\nUSING HEAP\n********************************************************************\n")
            queue = self.makeQueue( srcIndex, True )
        else:
            print("\nUSING Array\n********************************************************************\n")
            queue = self.makeQueue( srcIndex, False )
            # iter = -1
            prev_queue_len = len(queue)
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

                # for each node in list of neighbors of curr_node (at first: src)
                for node in [ node for node in queue if node.node_id in curr_neighbors ]:
                    curr_length = next( (x for x in curr_node.neighbors if x.dest.node_id == node.node_id), None).length
                    # print("\t\tnode_id = " + str(node.node_id) + " with length = " + str(self.result[ node ].dist))
                    d = self.result[ curr_node ].dist + curr_length

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
                prev_queue_len = len(queue)

                # self.printDict()


    def deleteMin( self, queue, use_heap=False ):
        if ( type(queue) == list ):
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


    def makeQueue( self, srcIndex, use_heap=False ):
        if (use_heap):
            self.makeHeap()
        else:
            queue = []

            # add src node in first
            queue.append( self.network.nodes[ srcIndex ] )

            # add the rest of the nodes
            for node in [x for x in self.network.nodes if x != queue[0]]:
                queue.append( node )

            # print("\nArray Queue now: ")
            # self.printQueue( queue )

            return queue









    def makeHeap( self ):
        return Null
