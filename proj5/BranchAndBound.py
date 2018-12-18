from TSPClasses import *
import heapq
import copy
from TSPState import State


def initialize_matrix(cities):
    matrix = [[math.inf for _ in range(len(cities))] for _ in range(len(cities))]  # O(n^2)
    for row, city in enumerate(cities):  # O(n^2)
        for col, other_city in enumerate(cities):
            matrix[row][col] = city.costTo(other_city)  # O(1) to get cost of city I think
    return matrix


def branch_and_bound_solution(cities, time_allowance):
    start_time = time.time()
    starting_matrix = initialize_matrix(cities)  # O(n^2)
    starting_tour = []
    starting_tour.append(cities[0])

    first_state = State(starting_tour, starting_matrix, 0.0)  # 0(n^2)

    bssf = random_solution(start_time, time_allowance, cities)  # O(n^n) worst case infinity because it may never find anything

    assert bssf.cost < math.inf
    solution_count = 0
    total_children = 1
    pruned = 0
    max_queue_size = 1

    pq = []
    # insert first state into pqueue
    heapq.heappush(pq, (first_state.priority, first_state))  # O(nlogn) according to the docs
    # while pqueue is not empty
    while len(pq) > 0 and time.time() - start_time < time_allowance:
        (_, current_state) = heapq.heappop(pq)  # O(1)
        # if current state.min_cost > bssf
        if current_state.cost > bssf.cost:
            # kill the branch and continue
            pruned += 1
            continue
        # generate all children states for this state
        children_states = generate_children(current_state, cities)  # O(n^3)
        total_children += len(children_states)

        for child in children_states:  # O(n)
            if child.cost > bssf.cost:
                pruned += 1
                continue
            if len(child.tour) == len(cities):
                new_solution = TSPSolution(child.tour)  # O(n)
                if new_solution.cost < bssf.cost:
                    solution_count += 1
                    bssf = new_solution
                continue
            heapq.heappush(pq, (child.priority, child))  # O(nlogn)
            if len(pq) > max_queue_size:
                max_queue_size = len(pq)

    end_time = time.time()
    results = {}
    results['cost'] = bssf.cost
    results['time'] = (end_time - start_time)
    results['count'] = solution_count
    results['soln'] = bssf
    results['max'] = max_queue_size
    results['total'] = total_children
    results['pruned'] = pruned + len(pq)
    return results


def generate_children(state, cities):
    child_states = []
    parent_index = state.tour[-1]._index
    possible_children = state.reduced_cost_matrix[parent_index]
    for child_index, j in enumerate(possible_children):  # O(n) children
        if j < math.inf:
            # then there is a way to get there and this state should be created
            parent_tour = copy.copy(state.tour)  # O(n)
            parent_tour.append(cities[child_index])  # O(1)
            parent_matrix = [row[:] for row in state.reduced_cost_matrix]  # O(n^2)
            child = State(parent_tour, parent_matrix,
                          (state.cost + state.reduced_cost_matrix[parent_index][child_index]))  # O(n^2)
            child_states.append(child)  # O(1)
    return child_states


def random_solution(start_time, time_allowance, cities):
    found_tour = False
    count = 0
    bssf = None
    while not found_tour and time.time() - start_time < time_allowance:
        # create a random permutation
        perm = np.random.permutation(len(cities))
        route = []
        # Now build the route using the random permutation
        for i in range(len(cities)):
            route.append(cities[perm[i]])
        bssf = TSPSolution(route)
        count += 1
        if bssf.cost < np.inf:
            # Found a valid route
            found_tour = True
    return bssf
