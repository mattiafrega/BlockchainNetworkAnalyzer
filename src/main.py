from flask import Flask, jsonify,render_template,request
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from main_flow.main_flow import analyzeGraph, downloadBuildGraph
import json
from utils import customutils as customutils
import networkx as nx
import concurrent.futures
from analyzer import analyzer
import threading
from cache import cacheutils as cache
from dotenv import load_dotenv


app = Flask(__name__)
lock = threading.Lock()

load_dotenv()
api_url_eth = "https://api.etherscan.io/api"
api_url_matic = "https://api.polygonscan.com/api"
api_key_list_eth = os.getenv('API_KEYS_ETH')
api_key_list_matic = os.getenv('API_KEYS_MATIC')
api_key_list_eth = json.loads(api_key_list_eth)
api_key_list_matic = json.loads(api_key_list_matic)

def downloadMaster(form_data):

    blockchain1 = form_data["Blockchain1"]
    blockchain2 = form_data["Blockchain2"]
    start_time = str(form_data["StartTime"])
    end_time = str(form_data["EndTime"])
    format = form_data["Format"]
    print("format", format)
    start_timestamp, end_timestamp = customutils.datetimeToUnixTs(start_time, end_time)
    start_timestamp = int(start_timestamp)
    end_timestamp = int(end_timestamp)
    print("start_timestamp", start_timestamp)
    print("end_timestamp", end_timestamp)
    print("end_timestamp - start_timestamp", end_timestamp - start_timestamp)
    if (end_timestamp - start_timestamp) < 1800:
        averagePath = True
    else:
        averagePath = False


    if(cache.get_from_cache(start_time, end_time,blockchain1, format) and cache.get_from_cache(start_time, end_time,blockchain2, format)):
        app.logger.info("Graphs already saved")
        graph_eth = cache.get_from_cache(start_time, end_time,blockchain1, format)
        graph_matic = cache.get_from_cache(start_time, end_time,blockchain2, format)
        random_graph_eth = cache.get_from_cache(start_time, end_time,"random-"+blockchain1, format)
        random_graph_matic = cache.get_from_cache(start_time, end_time,"random-"+blockchain2, format)
    else:
        app.logger.info("starting downloads..")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            worker_eth = executor.submit(downloadBuildGraph,form_data, api_key_list_eth, api_url_eth)
            worker_matic = executor.submit(downloadBuildGraph,form_data, api_key_list_matic, api_url_matic)
            graph_eth = worker_eth.result()
            graph_matic = worker_matic.result()
        
        app.logger.info("Saving graph eth")
        cache.insert_in_cache(graph_eth, form_data["Blockchain1"], form_data["StartTime"], form_data["EndTime"], format)
        edges_number1 = graph_eth.number_of_edges()
        nodes_number1 = graph_eth.number_of_nodes()
        try:
            probability1 = edges_number1 / (nodes_number1 * (nodes_number1 - 1))
            random_graph_eth = nx.gnp_random_graph(nodes_number1, probability1, directed=True)
            cache.insert_in_cache(random_graph_eth, "random-"+str(form_data["Blockchain1"]), str(form_data["StartTime"]), str(form_data["EndTime"]), format)
            app.logger.info("Saving graph matic")
            cache.insert_in_cache(graph_matic, form_data["Blockchain2"], form_data["StartTime"], form_data["EndTime"], format)
            print("graph matic saved!")
        except:
            print("something went wrong, probably ZeroDivisionError")
        try:
            edges_number2 = graph_matic.number_of_edges()
            nodes_number2 = graph_matic.number_of_nodes()
            probability2 = edges_number2 / (nodes_number2 * (nodes_number2 - 1))
            random_graph_matic = nx.gnp_random_graph(nodes_number2, probability2, directed=True)
            cache.insert_in_cache(random_graph_matic, "random-"+str(form_data["Blockchain2"]), str(form_data["StartTime"]), str(form_data["EndTime"]),format)
        except:
            print("something went wrong, probably ZeroDivisionError")

    #Graphs ready for analysis
    if('download' in form_data):
        app.logger.info("&&&&&&&&&&&&&&&&&&")
        directory = os.getcwd() + "/saved_graphs/"
        files = os.listdir(directory)

        html =  "<html> <body> <div> <h2> Downloaded Completed </h2> <p>Your file has been downloaded successfully.</p> "
        html  += " <h4>Downloaded files</h4> <ul>"
        for file in files:
            html += '<li><a href="file://{}{}">{}</a></li>'.format(directory, file, file)
        html += "</ul> <p> <a href='/start'> Go back to the form </a> </p>"
        html += "</div></body></html>"

        with open("src/templates/downloadcompleted.html", "w") as file:
            file.write(html)
            
        return render_template('downloadcompleted.html')
    else:
        measures_eth = analyzeGraph(graph_eth, averagePath)
        measures_matic = analyzeGraph(graph_matic,averagePath)
        measures_random_eth = analyzeGraph(random_graph_eth, averagePath)
        measures_random_matic = analyzeGraph(random_graph_matic, averagePath)
        if(averagePath):
            sw_eth = analyzer.getSmallWorldness( measures_eth["clustering_coefficient_mc"],measures_random_eth["clustering_coefficient_mc"], measures_eth["average_shortest_path_len"], measures_random_eth["average_shortest_path_len"])
            sw_matic = analyzer.getSmallWorldness( measures_matic["clustering_coefficient_mc"], measures_random_matic["clustering_coefficient_mc"], measures_matic["average_shortest_path_len"], measures_random_matic["average_shortest_path_len"])
            measures_eth.update({"small_world":sw_eth})
            measures_matic.update({"small_world":sw_matic})
        app.logger.info("&&&&&&&&&&&&&&&&&&")
        app.logger.info("ANALYSIS COMPLETED")

    results = [
    {
        "name": form_data["Blockchain1"],
        "measures": measures_eth
    },
    {
        "name": form_data["Blockchain2"],
        "measures": measures_matic
    },
    {
        "name": "Random "+form_data["Blockchain1"],
        "measures": measures_random_eth
    },
    {
        "name": "Random "+form_data["Blockchain2"],
        "measures": measures_random_matic
    }
    ]

    metadata = {
        "metadata": {
            "start_time": form_data["StartTime"],
            "end_time": form_data["EndTime"]
        }
    }
    results_json = results.copy()
    results_json.append(metadata)
    results_json = json.dumps(results_json,indent=4)

    with open("results.json", 'w') as file:
        file.write(results_json)

    return render_template('data.html',
                           form_data = form_data,
                           results = results)


#ROUTES
@app.route('/start')
def form():
    #process.txt content cleaning 
    with open("process.txt", 'w') as file:
        file.write("")
    return render_template('form.html')
 
@app.route('/data/', methods = ['POST', 'GET'])
def data():
    if request.method == 'GET':
        f"The URL /data is accessed directly. Try going to '/start' to submit form"
    if request.method == 'POST':
        form_data = request.form

        app.logger.info("#####################")
        app.logger.info("STARTING NEW ANALYSIS")
        app.logger.info("received Cores "+ form_data["Cores"])
        app.logger.info("received Blockchain1 "+ form_data["Blockchain1"])
        app.logger.info("received Blockchain2 "+ form_data["Blockchain2"])
        app.logger.info("Start time"+ form_data["StartTime"])
        app.logger.info("End time "+ form_data["EndTime"])
        app.logger.info("received Format "+ form_data["Format"])
        if('download' in form_data):
            app.logger.info("received DownloadPhaseOnly "+ form_data["download"])
        else:
            app.logger.info("received DownloadPhaseOnly off")
        return downloadMaster(form_data)
 
@app.route('/logs')
def logs():
    with open('app.log', 'r') as log_file:
        logs = log_file.read()
    return render_template('logs.html', logs=logs)


@app.route('/read', methods=['GET'])
def read():
    with lock:
        with open('process.txt', 'r') as f:
            content = f.read()
    return jsonify({'content': content})

@app.route('/getJSON', methods=['GET'])
def getJSON():
    with open('results.json', 'r') as f:
        content = f.read()
    return content


if __name__ == '__main__':
    if not os.path.exists('process.txt'):
        with open('process.txt', 'w'): pass


#START
app.logger.setLevel(logging.INFO)
file_handler = TimedRotatingFileHandler('app.log', when="midnight", interval=1, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)
app.run(host='0.0.0.0', port=5000)
