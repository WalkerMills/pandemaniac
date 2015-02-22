import json

def degree_discount(num_seeds, data):
    # tuneable parameter for inferring influence of node on neighbors
    p = .01
    # chosen seed nodes
    seed_nodes = []
    # dynamic degrees of nodes (will be discounted)
    dynamic_deg = {}
    # original degrees of nodes
    static_deg = {}
    # number of neighbors of given node in seed_nodes
    seed_nbors = {}

    # create a list of (node, degree) tuples
    for node in data:
        dynamic_deg[node] = len(data[node])
        static_deg[node] = len(data[node])
        seed_nbors[node] = 0


    # run degree discount algorithm
    for i in range(num_seeds):
        # save node with highest discounted degree
        best_seed = max(dynamic_deg, key=dynamic_deg.get)
        seed_nodes.append(best_seed)
        print(best_seed)
        # remove this node from the dictionary
        del dynamic_deg[best_seed]
        # discount the degree of recently selected seed
        for node in data[best_seed]:
            seed_nbors[node] += 1
            dv = static_deg[node]
            tv = seed_nbors[node]
            if node not in seed_nodes:
                dynamic_deg[node] = dv - 2 * tv - (dv - tv) * tv * p

    return seed_nodes

def main():
    with open("input.txt", "r") as f:
        data = json.load(f)
    sorted_data = sorted(data.keys(), key=lambda k: (len(data[k]), k) )
    sorted_data2 = degree_discount(10, data)

    for i in range(10):
        print('degree, degree_discount: {}, {}'.format( \
                            sorted_data[len(sorted_data) - i - 1], \
                            sorted_data2[i]))
    # to speed up computation, ignore nodes with degree below ***


if __name__ == "__main__":
    main()

