# dato in input il grafo ritorna la metrica
import networkx as nx
import json
from collections import defaultdict

def getNodes(graph):
	res = graph.number_of_nodes()
	return res

def getEdges(graph):
	res = graph.number_of_edges()
	return res

def getGraphDensity(graph):
	res = nx.density(graph)
	return res

def getDegreeDistribution(graph, degree_type="tot"):
	degrees = defaultdict(list)

	graph_degree = (graph.out_degree if degree_type == "out" else 
		graph.in_degree if degree_type == "in" else 
		graph.degree)

	for key, value in sorted(graph_degree):
		degrees[value].append(key)

	for k, v in degrees.items():
		degrees[k] = len(v)

	deg_distr = dict(degrees)

	deg_distr_json = json.dumps(deg_distr)
	return deg_distr_json

def getAverageClusteringCoefficient(graph, weight=None):
	clust_coeff = nx.average_clustering(graph, weight=weight)
	return clust_coeff


def getMainComponent(graph):
	res = graph.subgraph(max(nx.weakly_connected_components(graph), key=len)).copy()
	return res

def getSmallWorldness(average_clustering, average_clustering_random, average_shortest_path_length, average_shortest_path_length_random):
    if average_clustering_random == 0 or average_shortest_path_length_random == 0:
        return "Cannot calculate Small Worldness: Division by zero in random measures."
    if average_shortest_path_length == 0:
        return "Cannot calculate Small Worldness: Division by zero in average shortest path length."
    result = (average_clustering / average_clustering_random) / (average_shortest_path_length / average_shortest_path_length_random)
    return result

def getReciprocity(graph):
	res = nx.reciprocity(graph)
	return res


def getAverageDegree(graph):
	average_degree = sum(dict(graph.degree()).values()) / len(graph)
	return average_degree

def getDiameter(graph):
    undirected_graph = graph.to_undirected()
    diameter = nx.diameter(undirected_graph)
 
    return diameter

def getAverageShortestPathLength(graph):
	undirected_graph = graph.to_undirected()
	aspl = nx.average_shortest_path_length(undirected_graph, method="dijkstra")

	return aspl