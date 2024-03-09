import networkx as nx
import os

BASE_PATH = "saved_graphs/"

def insert_in_cache(G, blockchain, start_time, end_time, format="gexf"):
    start_time = str(start_time).replace(":", "-")
    end_time = str(end_time).replace(":", "-")
    file_name = f"{start_time}-{end_time}-{blockchain}.{format}"
    file_path = os.path.join(BASE_PATH, file_name)
    if(format == "gexf"):
        nx.write_gexf(G, file_path)
    elif(format == "gml"):
        nx.write_gml(G, file_path)
    elif(format == "net"):
        nx.write_pajek(G, file_path)
    return 1

def get_from_cache(start_time, end_time, blockchain, format="gexf"): 
    
    start_time = str(start_time).replace(":", "-")
    end_time = str(end_time).replace(":", "-")
    file_name = f"{start_time}-{end_time}-{blockchain}.{format}"
    folder_path = os.path.join(BASE_PATH, "")
    if not os.path.exists(folder_path):
        create_folder(folder_path)

    try:
        if(format == "gexf"):
            G = nx.read_gexf(os.path.join(BASE_PATH, file_name))
        elif(format == "gml"):
            G = nx.read_gml(os.path.join(BASE_PATH, file_name))
        elif(format == "net"):
            G = nx.read_pajek(os.path.join(BASE_PATH, file_name))
            G = nx.DiGraph(G)
        return G
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' does not exist in cache.")
        return None

    
def create_folder(folder_path):
    try:
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    except FileExistsError:
        print(f"Folder '{folder_path}' already exists.")