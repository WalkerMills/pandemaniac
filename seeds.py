import inspect
import itertools
import networkx as nx
import random

import interface

BETWEEN = "between"
CLOSE = "close"
DEGREE = "degree"
DISCOUNT = "discount"
ITERATED = "iterated"

class SeedSelector:

    # Labels for each different centrality/influence metric
    order = [BETWEEN, CLOSE, DEGREE, DISCOUNT, ITERATED]

    def __init__(self, graph, discount=0, degree=0, iterated=0, close=0,
                 between=0, generations=3, entropy=0.0):
        # Store graph data
        self.graph = graph
        # Number of generations for the iterated degree metric
        self.generations = generations
        # (1 + entropy) * # of seeds desired (seeds) are stored for each
        # metric, and the correct number are randomly chosen from that node set
        self.multiplier = 1.0 + entropy
        # Initialize seed sets
        self.seeds = {metric: set() for metric in self.order}
        # Maps metric labels -> seed generating method (must take no arguments)
        self.seed_functions = {
            BETWEEN: self._between_seeds,
            CLOSE: self._close_seeds,
            DEGREE: lambda: self._iterated_degree_seeds(1),
            DISCOUNT: self._discount_seeds,
            ITERATED: lambda: self._iterated_degree_seeds(self.generations)
        }
        # Get information about this stack frame
        argspec = inspect.getargvalues(inspect.currentframe())
        # For each metric argument given
        for arg in filter(lambda a: a in self.order, argspec.args):
            # Store it as a class attribute
            setattr(self, arg, argspec.locals[arg])
        # Generate the random seeds
        self.generate()

    def _between_seeds(self):
        # Terminate if this metric is not being used
        if getattr(self, BETWEEN) < 1:
            return

        # Calculate betweenness centrality, filtering to non-zero ranks
        betweenness = dict(
            filter(lambda i: i[1] > 0, 
                   nx.betweenness_centrality(nx.Graph(self.graph)).items()))
        # Limited-size max heap for storing the highest ranked nodes
        largest = interface.rank_heap(int(self.between * self.multiplier))
        # For each node in the graph
        for node, rank in betweenness.items():
            # If this node is not already a seed node
            if all(map(lambda s: node not in s, self.seeds.values())):
                # Try adding its (rank, ID) tuple to the ranking max heap
                largest.insert(rank, node)

        # While we do not have enough new seeds
        for i in range(largest.size()):
            # Extract the maximum-rank node from the heap
            node, _ = largest.get_max()
            # Add the node to the seed set
            self.seeds[BETWEEN].add(node)

    def _close_seeds(self):
        # Terminate if this metric is not being used
        if getattr(self, CLOSE) < 1:
            return

        # Convert graph data into networkx Graph class
        G = nx.Graph(self.graph)
        # Limited-size max heap for storing the highest ranked nodes
        largest = interface.rank_heap(int(self.close * self.multiplier))

        # For each node in the graph
        for node in self.graph:
            # If this node is not already a seed node
            if all(map(lambda s: node not in s, self.seeds.values())):
                try:
                    # Calculate its closeness centrality
                    rank = nx.closeness_centrality(G, node)
                    # Try adding its (rank, ID) tuple to the ranking max heap
                    largest.insert(rank, node)
                except Exception:
                    # Ignore nodes for which the computation fails
                    continue

        # While we do not have enough new seeds
        for i in range(largest.size()):
            # Extract the maximum-rank node from the heap
            node, _ = largest.get_max()
            # Add the node to the seed set
            self.seeds[CLOSE].add(node)

    def _discount_seeds(self):
        # Terminate if this metric is not being used
        if getattr(self, DISCOUNT) < 1:
            return

        # Probability that a node will color its neighbor
        p = .01
        # extra * self.multiplier * self.discount of the largest nodes are
        # stored to be updated by the degree discount algorithm
        extra = 2
        # Maps node ID -> discounted node degree
        discounted = {}
        # Maps node ID -> number of neighboring seeds
        neighbors = {}
        # Limited-size max heap for storing the highest ranked nodes
        largest = interface.rank_heap(
            int(self.discount * self.multiplier * extra))

        # For each node in the graph
        for node, adjacent in self.graph.items():
            # If this node is not already a seed
            if all(map(lambda s: node not in s, self.seeds.values())):
                # Try adding its (rank, ID) tuple to the ranking max heap
                largest.insert(len(adjacent), node)
        # While the rank heap contains nodes
        while largest.size() > 0:
            # Extract the (rank, node) tuple of maximum rank
            node, rank = largest.get_max()
            # Initialize an entry in the discounted & neighbors mappings
            discounted[node] = rank
            neighbors[node] = \
                len(self.seeds[DISCOUNT].intersection(self.graph[node]))

        # While we do not have enough new seeds
        for i in range(int(self.discount * self.multiplier)):
            # Get the node with maximum discounted degree
            best_seed = max(discounted, key=discounted.get)
            # Add the node to the seed set
            self.seeds[DISCOUNT].add(best_seed)
            # Ignore this node in future iterations
            del discounted[best_seed]
            del neighbors[best_seed]
            # Discount the degrees of its neighbors
            for node in self.graph[best_seed]:
                try:
                    neighbors[node] += 1
                except KeyError:
                    continue
                dv = len(self.graph[node])
                tv = neighbors[node]
                discounted[node] = dv - 2 * tv - (dv - tv) * tv * p

    def _iterated_degree_seeds(self, generations):

        def bfs_count(node, generations):
            # Initialize a depth-limited frontier record
            frontier = [[] for i in range(generations + 1)]
            # Set current generation to 0
            current = 0
            # Add the root node to the current generation
            frontier[current].append(node)

            # While we have not traversed to the required depth
            while current < generations:
                # Move to the next generation
                current += 1
                # For each node in the last generation
                for n in frontier[current - 1]:
                    # Add its children to the current generation
                    frontier[current] += self.graph[n]
            # Return the total number of descendants (iterated out-degree)
            return sum(len(gen) for gen in frontier[1:])

        # Terminate if this metric is not being used
        new = self.degree
        label = DEGREE
        if generations == 1:
            if getattr(self, DEGREE) < 1:
                return
        else:
            if getattr(self, ITERATED) < 1:
                return
            else:
                new = self.iterated
                label = ITERATED

        # Maps node ID -> iterated out-degree
        iterated = {}
        # Limited-size max heap for storing the highest ranked nodes
        largest = interface.rank_heap(int(new * self.multiplier))
        # For each node in the graph
        for node in self.graph:
            # If this node is not already a seed
            if all(map(lambda s: node not in s, self.seeds.values())):
                # Try adding its (rank, ID) tuple to the ranking max heap
                largest.insert(bfs_count(node, generations), node)

        # While we do not have enough new seeds
        for i in range(new):
            # Extract the maximum-rank node from the heap
            node, _ = largest.get_max()
            # Add the node to the seed set
            self.seeds[label].add(node)

    def choose(self):
        # If this selector is using semi-random nodes
        if self.multiplier > 1:
            # Initialize the list of chosen seeds
            chosen = []
            # For each metric
            for metric in self.order:
                # Get the desired number of seeds
                desired = getattr(self, metric)
                # If this metric is active
                if desired > 0:
                    # Make a list from the seed set
                    possible_seeds = list(self.seeds[metric])
                    for i in range(desired):
                        # Choose a random seed from the remaining seeds
                        target = random.randrange(i, desired)
                        # Swap the selected seed into the ith position
                        tmp = possible_seeds[i]
                        possible_seeds[i] = possible_seeds[target]
                        possible_seeds[target] = tmp
                    # Trim the seed list to the desired length
                    possible_seeds = possible_seeds[:desired]
                    # Add the seeds for this metric to the chosen seeds list
                    chosen += possible_seeds
        else:
            chosen = list(itertools.chain.from_iterable(self.seeds.values()))
        return chosen

    def generate(self):
        # For each centrality/influence metric
        for metric in self.order:
            # Generate & store the desired number of seeds
            self.seed_functions[metric]()
