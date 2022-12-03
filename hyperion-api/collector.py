#    ____ __      __  __      _
#    / __ )/ /___ ______/ /__/ /_ _______(_)___ ____
#   / __ / / __ `/ ___/ //_/ / / / / ___/ / __ \/ __ \
#   / /_/ / / /_/ / /__/ ,< / / /_/ (__ ) / /_/ / / / /
#  /_____/_/\__,_/\___/_/|_/_/\__,_/____/_/\____/_/ /_/
#  
  

import sys
import signal
from dataclasses import MISSING
from prometheus_client import Gauge, start_http_server, Counter, MetricsHandler
import requests, sys, json
from datetime import datetime
import dateutil.parser
from http.server import HTTPServer
import urllib.parse

HYPERION_MISSING_BLOCKS = Gauge('HYPERION_MISSING_BLOCKS', 'Missing blocks')
HYPERION_BLOCK_DELTA = Gauge('HYPERION_BLOCK_DELTA' , 'Block delta')
HYPERION_QUERY_TIME_MS = Gauge('HYPERION_QUERY_TIME_MS', 'query Time in millisec')
HYPERION_RABBITMQ_STATUS = Gauge('HYPERION_RABBITMQ_STATUS', 'Hyperion RabbitMQ Status')
HYPERION_NODEOSRPC_STATUS = Gauge('HYPERION_NODEOSRPC_STATUS' , 'Hyperion NodeosRPC Status')
HYPERION_ELASTICSEARCH_STATUS = Gauge('HYPERION_ELASTICSEARCH_STATUS', 'Hyperion Elasticsearch Status')


ENDPOINT = ""
PORT = ""

def getTimestamp():
  return str(datetime.now().isoformat())

def exitMsg(*args):
  print(getTimestamp() + ": Hyperion API Exporter exiting")
  sys.exit(0)

signal.signal(signal.SIGABRT, exitMsg)
# signal.signal(signal.SIGBREAK, exitMsg)#windows
signal.signal(signal.SIGHUP, exitMsg)    #Linux
signal.signal(signal.SIGINT, exitMsg)    #linux
signal.signal(signal.SIGTERM, exitMsg)   #linux
# signal.signal(signal.SIGEGV, exitMsg)  #windows


class MyRequestHandler(MetricsHandler):

  def hyperionAPI(self):
    #host = 'https://hyperion.wax.blacklusion.io/v2/health'
    # print(self.host)
    j = requests.get(self.host).json()
    # print(j)
    
    totalIndexedBlocks = lastIndexedBlock = missingBlocks = blockDelta = queryTimeMs = headBlockNum = 0
    isCached = False
    for key,value in j.items():
      if key == 'health':
        for i in range(len(value)):   
          if value[i]['service'] == 'NodeosRPC':
            headBlockNum = value[i]['service_data']['head_block_num']
      
          if value[i]['service'] == 'Elasticsearch':
            lastIndexedBlock = value[i]['service_data']['last_indexed_block']
            totalIndexedBlocks = value[i]['service_data']['total_indexed_blocks']

      if key == 'cached':
        isCached = True
      
    queryTimeMs = j['query_time_ms']
    missingBlocks = totalIndexedBlocks - lastIndexedBlock
    blockDelta = headBlockNum - lastIndexedBlock

    queryTimeMs = max(0, queryTimeMs)
    missingBlocks = max(0,missingBlocks)
    blockDelta = max(0,blockDelta)

    rabbitmq_status = 1 if j['health'][0]['status'] == 'OK' else 0
    nodeosrpc_status = 1 if j['health'][1]['status'] == 'OK' else 0
    elasticsearch_status = 1 if j['health'][2]['status'] == 'OK' else 0

    HYPERION_MISSING_BLOCKS.set(missingBlocks)
    HYPERION_BLOCK_DELTA.set(blockDelta)
    if isCached == False:
      HYPERION_QUERY_TIME_MS.set(queryTimeMs)
    HYPERION_RABBITMQ_STATUS.set(rabbitmq_status)
    HYPERION_NODEOSRPC_STATUS.set(nodeosrpc_status)
    HYPERION_ELASTICSEARCH_STATUS.set(elasticsearch_status)


    return super(MyRequestHandler, self).do_GET()


  def do_GET(self):
    unquoted = urllib.parse.unquote_plus(self.path)
    parsed_path = urllib.parse.urlsplit(unquoted)
    query = urllib.parse.parse_qs(parsed_path.query)
    if "target" in query:
      self.host = query['target'][0]
      print(getTimestamp() + ": Hyperion API Exporter request received. target = " + self.host, flush=True)
      self.hyperionAPI()
    else:
      print(getTimestamp() + ": Hyperion API Exporter request received. target = None", flush=True)
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"No target\n")


if __name__ == '__main__':
  PORT = 8000
  print(getTimestamp() + ":"+": Hyperion API Exporter started. Listening on PORT " + str(PORT), flush=True)
  # ENDPOINT = sys.argv[2]
  ENDPOINT = ''

  server_address = ('', int(PORT))
  HTTPServer(server_address, MyRequestHandler).serve_forever()

