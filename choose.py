#!/usr/bin/env python3

import argparse
import json
import sys

import seeds

def parse_data(graph):
    # Open the given adjacency list file
    with open(graph, "r") as f:
        # Parse the JSON
        data = json.load(f)
        # Cast nodes & neighbors to int's
        data = {int(k): [int(n) for n in v] for k, v in data.items()}
    return data

def main():
    parser = argparse.ArgumentParser(
        description="Select seed nodes for a given graph, according to various"
                    " centrality & influence metrics")
    metrics = parser.add_argument_group("metrics",
        "These options control how many seeds are selected using each metric. "
        " By default, no seeds are selected.")
    parser.add_argument("graph", metavar="GRAPH", 
                        help="The location of the graph, stored as a node "
                             "adjacency list in JSON format")
    parser.add_argument("trials", metavar="TRIALS", type=int,
                        help="The number of trials, used to control how many "
                             "times the seeds are printed to stdout")
    metrics.add_argument("-d", "--discount", dest="discount", type=int,
                         help="The number of seeds to select using the degree"
                              " discount heuristic", default=0)
    metrics.add_argument("-D", "--degree", dest="degree", type=int,
                         help="The number of seeds to select by maximum "
                              "degree", default=0)
    metrics.add_argument("-i", "--iterated", dest="iterated", type=int,
                         help="The number of seeds to select by maximum "
                              "iterated degree", default=0)
    parsed = parser.parse_args()
    # Load the given adjacency list
    data = parse_data(parsed.graph)
    # Initialize dictionary of keyword arguments for SeedSelector constructor
    kwargs = {}
    # For each metric
    for metric in seeds.SeedSelector.order:
        # Get the value (if any; defaults to 0) that was given by the user
        value = getattr(parsed, metric)
        # Map the metric label to its given value
        kwargs[metric] = value
    # Initialize the seed selector
    gen = seeds.SeedSelector(data, **kwargs)
    # Choose the seed nodes
    gen.choose()
    # Print as many copies of the newline-delimited seeds as necessary
    for i in range(parsed.trials):
        sys.stdout.write("".join("{}\n".format(s) for s in gen.seeds))
    sys.stdout.flush()

if __name__ == "__main__":
    main()

