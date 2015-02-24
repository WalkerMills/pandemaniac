import inspect


class SeedSelector:

    # Labels for each different centrality/influence metric
    order = ["discount", "degree", "iterated"]

    # Default number of generations for the iterated degree metric
    generations = 2

    def __init__(self, graph, discount=0, degree=0, iterated=0):
        # Store graph data
        self.graph = graph
        # Initialize seed set
        self.seeds = set()
        # Maps metric labels -> seed generating method (must take no arguments)
        self.seed_functions = {
            "discount": self._discount_seeds,
            "degree": lambda: self._iterated_degree_seeds(1),
            "iterated": lambda: self._iterated_degree_seeds(self.generations)
        }
        # Get information about this stack frame
        argspec = inspect.getargvalues(inspect.currentframe())
        # For each argument given, besides the object reference & graph data
        for arg in argspec.args[2:]:
            # Store it as a class attribute
            setattr(self, arg, argspec.locals[arg])

    def _discount_seeds(self):
        # Terminate if this metric is not being used
        if self.discount < 1:
            return

        # Probability that a node will color its neighbor
        p = .01
        # Maps node ID -> discounted node degree
        discounted = {}
        # Maps node ID -> number of neighboring seeds
        neighbors = {}

        # Initialize the discounted node degrees & neighboring seeds
        for node, adjacent in self.graph.items():
            # If this node is not already a seed
            if node not in self.seeds:
                discounted[node] = len(adjacent)
                neighbors[node] = len(self.seeds.intersection(adjacent))

        # Current number of seed nodes
        current = len(self.seeds)
        # Target number of seed nodes
        final = len(self.seeds) + self.discount
        # While we do not have enough new seeds
        while current < final:
            # Get the node with maximum discounted degree
            best_seed = max(discounted, key=discounted.get)
            # Try adding the node to the seed set
            self.seeds.add(best_seed)
            # Update the current number of seeds
            current = len(self.seeds)
            # Ignore this node in future iterations
            del discounted[best_seed]
            del neighbors[best_seed]
            # Discount the degrees of non-seed neighbors
            for node in set(self.graph[best_seed]) - self.seeds:
                neighbors[node] += 1
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
        new = 0
        if generations == 1:
            if self.degree < 1:
                return
            else:
                new = self.degree
        else:
            if self.iterated < 1:
                return
            else:
                new = self.iterated

        # Maps node ID -> iterated out-degree
        iterated = {}
        # Calculate iterated degree for every node in the graph
        for node in self.graph:
            iterated[node] = bfs_count(node, generations)

        # Sort the nodes in the graph by degree, breaking ties by ID
        data = sorted(iterated.keys(), key=lambda k: (len(self.graph[k]), k))
        # Current number of seed nodes
        current = len(self.seeds)
        # Target number of seed nodes
        final = len(self.seeds) + new
        # Initial offset in the ranked node list
        offset = 0
        # While we do not have enough new seeds
        while current < final:
            # Try adding the current node to the seed set
            self.seeds.add(data[offset])
            # Update the current number of seeds
            current = len(self.seeds)
            # Examine the next node
            offset += 1

    def choose(self):
        # Clear any existing seeds
        self.seeds.clear()
        # For each centrality/influence metric
        for metric in self.order:
            # Generate & store the desired number of seeds
            self.seed_functions[metric]()
