import sys
import logging
from file_writer.file_writer import writeToFile
from utils import customutils
from analyzer import analyzer
import networkx as nx
from downloader import downloader as dm
import numpy as np
import concurrent.futures
import time

logger = logging.getLogger(__name__)


def downloadBuildGraph(form_data, api_key_list, api_url):

    logger.info("converting date to unix ms..")
    start_timestamp, end_timestamp = customutils.datetimeToUnixTs(form_data["StartTime"], form_data["EndTime"])

    start_timestamp = int(start_timestamp)
    end_timestamp = int(end_timestamp)
    logger.info("starting block num downloads..")
    
    first_block, last_block = dm.get_blocks_by_time(start_timestamp, end_timestamp, api_key=api_key_list[0], api_url = api_url)
    first_block = int(first_block)
    last_block = int(last_block)
    tot_blocks = last_block-first_block
    writeToFile("tot blocks: " + str(tot_blocks))
    logger.info("blocks obtained, getting transactions..")
    num_cores = int(form_data["Cores"])
    if(num_cores > 6):
        num_cores= 6
    elif(num_cores <= 0):
        num_cores = 1

    #to avoid index out of range
    if(num_cores > len(api_key_list)):
        num_cores = len(api_key_list)
    block_parts = np.linspace(first_block, last_block, num_cores+1, dtype=int)      
    logger.info("partitions created..")
    graphs = []
    writeToFile("launching download thread pool to "+ api_url)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        workers = [executor.submit(dm.get_graph_for_blocks, block_parts[i], block_parts[i+1], api_key=api_key_list[i], api_url= api_url) for i in range(num_cores)]
        for worker in workers:
            graph = worker.result()
            graphs.append(graph)
    gg_final = graphs[0]
    writeToFile("building final network..")
    for graph in graphs[1:]:
        gg_final = nx.compose(gg_final, graph)
    
    logger.info("Create graph from transactions...")
    print("\t nodes: "+str(gg_final.number_of_nodes()))
    print("\t edges: "+str(gg_final.number_of_edges()))
    edge_mem = sum([sys.getsizeof(e) for e in gg_final.edges])
    node_mem = sum([sys.getsizeof(n) for n in gg_final.nodes])
    print("Edge memory:", edge_mem , "bytes")
    print("Node memory:", node_mem, "bytes")
    print("Total memory:", edge_mem + node_mem, "bytes")
    print("Total memory:", (edge_mem + node_mem)/1000000, "MB")

    return gg_final

def execute_task(task_name, task_func, *args):
    logger.info(f"Calculating {task_name}..")
    writeToFile(f"Calculating {task_name}.. ")
    start = time.time()
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(task_func, *args)
            result = future.result()
        end = time.time()
        total = end - start
        total = round(total, 4) 
        logger.info(f"\t {task_name} calculated in {total} seconds")
        writeToFile(f"\t {task_name} calculated in {total} seconds")
        return result
    except Exception as e:
        logger.error(f"Error analyzing {task_name}: {str(e)}")
        return None
 
def analyzeGraph(graph, averagePath):
   
    tasks = {
        "number_of_nodes": analyzer.getNodes,
        "number_of_edges": analyzer.getEdges,
        "density": analyzer.getGraphDensity,
        "degree_distribution": analyzer.getDegreeDistribution,
        "degree_distribution_in": lambda g: analyzer.getDegreeDistribution(g, "in"),
        "degree_distribution_out": lambda g: analyzer.getDegreeDistribution(g, "out"),
        "clustering_coefficient": analyzer.getAverageClusteringCoefficient,
        "reciprocity": analyzer.getReciprocity,
        "average_degree": analyzer.getAverageDegree,
    }
 
    measures = {task: execute_task(task, func, graph) for task, func in tasks.items()}
 
    # Calculate main component separately after all other tasks are done
    main_component_graph = execute_task("main_component", analyzer.getMainComponent, graph)
 
    if main_component_graph is not None:
        if(averagePath):
            mc_tasks = {
                "number_of_nodes_of_main_component": analyzer.getNodes,
                "number_of_edges_of_main_component": analyzer.getEdges,
                "clustering_coefficient_mc": analyzer.getAverageClusteringCoefficient,
                "average_shortest_path_len": analyzer.getAverageShortestPathLength,
                "degree_distribution_mc": analyzer.getDegreeDistribution,
                "degree_distribution_in_mc": lambda g: analyzer.getDegreeDistribution(g, "in"),
                "degree_distribution_out_mc": lambda g: analyzer.getDegreeDistribution(g, "out"),
            } 
        else:
            mc_tasks = {
                "number_of_nodes_of_main_component": analyzer.getNodes,
                "number_of_edges_of_main_component": analyzer.getEdges,
                "clustering_coefficient_mc": analyzer.getAverageClusteringCoefficient,
                "degree_distribution_mc": analyzer.getDegreeDistribution,
                "degree_distribution_in_mc": lambda g: analyzer.getDegreeDistribution(g, "in"),
                "degree_distribution_out_mc": lambda g: analyzer.getDegreeDistribution(g, "out"),
            }
 
        mc_measures = {task: execute_task(task, func, main_component_graph) for task, func in mc_tasks.items()}
        measures.update(mc_measures)
 
    logger.info("finish to calculate measures")
    return measures
