def addToGraph(graph,transactions):
    for transaction in transactions:
            source = transaction['from']
            target = transaction['to']
            if source == None:
                print("!!source is none..")
                continue
            if target == None:
                print("!target is none..")
                continue
            graph.add_edge(source, target)        
    return graph
