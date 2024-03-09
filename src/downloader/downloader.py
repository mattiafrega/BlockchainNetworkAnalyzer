import requests
import time
import multiprocessing as mp
import time
import networkx as nx
from generator import graphGenerator as gg

def get_blocks_by_time(start_timestamp, end_timestamp, api_key, api_url):
    """
    Retrieves the first and last block numbers within a specified time range.
    Args:
        start_timestamp (int): The starting timestamp of the time range.
        end_timestamp (int): The ending timestamp of the time range.

    Returns:
        tuple: A tuple containing the first block number and the last block number.
    """

    params = {
        'module': 'block',
        'action': 'getblocknobytime',
        'timestamp': start_timestamp,
        'closest': 'before',
        'apikey': api_key
    }

    print("getting starting block..")
    response_start = requests.get(api_url, params=params)
    data_start = response_start.json()
    first_block = data_start['result']
    print("first block: "+first_block)
    params['timestamp'] = end_timestamp

    print("getting last block..")
    response_end = requests.get(api_url, params=params)
    data_end = response_end.json()
    last_block = data_end['result']
    print("last block: "+last_block)

    return first_block, last_block


def get_graph_for_blocks(first_block, last_block, api_key, api_url):
    """
    Retrieves transactions for a range of blocks using the Etherscan API.

    Args:
        first_block (int): The starting block number.
        last_block (int): The ending block number.

    Returns:
        DiGraph: A graph containing all the transactions contained in the specified blocks.
    """
 
    tot_transactions = 0
    DiGrafo = nx.DiGraph()
    for block_number in range(int(first_block), int(last_block) + 1):
        params = {
            'module': 'proxy',
            'action': 'eth_getBlockByNumber',
            'tag': hex(block_number),
            'boolean': 'true',
            'apikey': api_key
        }

        response = requests.get(api_url, params=params)
        data = response.json()

        if 'result' in data and data['result'] is not None:
            print("transactions found in block"+ str(block_number))
            transactions = data['result'].get('transactions', [])
            print("\t num transactions: "+str(len(transactions)))
            tot_transactions += len(transactions)
            DiGrafo = gg.addToGraph(DiGrafo,transactions)
            
        #max 5 requests per second
        time.sleep(0.2)

    print("tot transactions: "+str(tot_transactions))
    return DiGrafo