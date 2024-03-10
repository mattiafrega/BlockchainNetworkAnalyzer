# BlockchainNetworkAnalyzer
BlockchainNetworkAnalyzer is a software that analyzes the interactions over a specified period of time between the accounts that are involved in the transactions that are recorded on the distributed ledger technologies.
Then, using complex network theory, it attempts to provide important insights into the typical use of this technology, examining the patterns of interaction in different distributed ladgers.
In our case, vertices are addresses of a particular blockchain and the presence of an edge indicates that a transaction occurred between the two nodes.

The software is a web app built in python, using Flask.

Inspired from [DiLeNA](https://github.com/AnaNSi-research/DiLeNA) by AnaNSi-research

## Structure of the repository

- **main.py**: entrypoint of the application, with the routes to render the pages and to start the main flow
- **main_flow**: main method to handle the download - build - analysis of the network flow and in particular the ThreadPoolExecutors
- **downloader**: functions that calls the blockchain API to get blocks and transactions
- **generator**: graph builder
- **analyzer**: helper functions that wrap networkx library 
- **file_writer**: simple filewriter to track the steps and write on process.txt
- **cache**: cache utils functions to save an retrieve the graphs from the storage directory
- **utils**: other utils

## Screenshots
Start analysis page
![Start screen](https://think.suedunicorn.it/wp-content/uploads/2024/03/start_analysis1.png)
Results page
![Start screen](https://think.suedunicorn.it/wp-content/uploads/2024/03/result_analysis1.png)

### Calculated metrics
For the full transactions network:
- number of nodes
- number of edges
- density
- degree distribution
- degree distribution IN
- degree distribution OUT
- clustering coefficient
- reciprocity
- average_shortest_path_len
- average degree

For the main component:
- number of nodes 
- number of edges
- clustering coefficient
- degree distribution
- degree distribution IN
- degree distribution OUT

## Get started
### Manual [RECOMMENDED]
To get started:
- clone the repository,
- be sure to have installed all the packages included in the requirements.txt file,
- add your personal apikeys in a .env file,
```
API_KEYS_ETH='["MYAPIKEY1","MYAPIKEY2"]'
API_KEYS_MATIC='["MYAPIKEY1", "MYAPIKEY2"]'
```
- launch:
```
main.py
```
and go to localhost:5000/start

### Docker
If you're into Docker you may want to just launch
```
docker run -p 5000:5000 mattiafrega/blockchainnetworkanalyzer:latest
```
An go to the host container at :5000/start

### Quick Demo
If you just want a quick demo, visit:

https://blockchainnetworkanalyzer.suedunicorn.it/start

⚠️ Please note the online version may not be stable and runs on a development server with limited hardware capabilities. 
Because of this reason, heavy computations like average_shortest_path_len are disabled and the maximum time interval allowed for analysis is 30 minutes.
It will improve in the future.




