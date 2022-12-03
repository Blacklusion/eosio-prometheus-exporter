#    ____ __      __  __      _
#    / __ )/ /___ ______/ /__/ /_ _______(_)___ ____
#   / __ / / __ `/ ___/ //_/ / / / / ___/ / __ \/ __ \
#   / /_/ / / /_/ / /__/ ,< / / /_/ (__ ) / /_/ / / / /
#  /_____/_/\__,_/\___/_/|_/_/\__,_/____/_/\____/_/ /_/
#  

import sys
import signal
from datetime import datetime
from dataclasses import MISSING
from prometheus_client import Gauge, start_http_server, Counter, MetricsHandler
import requests, sys, json
from datetime import datetime
import dateutil.parser
from http.server import HTTPServer
import urllib.parse


ATOMIC_BLOCK_DELTA = Gauge('ATOMIC_BLOCK_DELTA', 'Block Delta');
ATOMIC_POSTGRES_STATUS = Gauge('ATOMIC_POSTGRES_STATUS', 'Atomic Postgres Status');
ATOMIC_REDIS_STATUS = Gauge('ATOMIC_REDIS_STATUS', 'Atomic Redis Status');
ATOMIC_CHAIN_STATUS = Gauge('ATOMIC_CHAIN_STATUS', 'Atomic Chain Status');
ATOMIC_BLOCK_TIME_DELTA = Gauge('ATOMIC_BLOCK_TIME_DELTA', 'Atomic Block Time Delta');


ENDPOINT = ""
PORT = ""

def getTimestamp():
  return str(datetime.now().isoformat())

def exitMsg(*args):
  print(getTimestamp() + ": Atomic API Exporter exiting")
  sys.exit(0)

signal.signal(signal.SIGABRT, exitMsg)
# signal.signal(signal.SIGBREAK, exitMsg)#windows
signal.signal(signal.SIGHUP, exitMsg)    #Linux
signal.signal(signal.SIGINT, exitMsg)    #linux
signal.signal(signal.SIGTERM, exitMsg)   #linux
# signal.signal(signal.SIGEGV, exitMsg)  #windows


class MyRequestHandler(MetricsHandler):

  def atomicAPI(self):
    #host = 'https://aa.wax.blacklusion.io/health'
    # print(self.host)
    j = requests.get(self.host).json()
    # print(j)
    headBlock = j['data']['chain']['head_block']
    blockNum = j['data']['postgres']['readers'][0]['block_num']
    
    delta = (headBlock - int(blockNum));
    delta = max(0, delta);
    postgres_status = 1 if j['data']['postgres']['status'] == 'OK' else 0;
    redis_status = 1 if j['data']['redis']['status'] == 'OK' else 0;
    chain_status = 1 if j['data']['chain']['status'] == 'OK' else 0;

    block_time_delta = abs(j['query_time'] - j['data']['chain']['head_time']);

    ATOMIC_BLOCK_DELTA.set(delta);
    ATOMIC_POSTGRES_STATUS.set(postgres_status);
    ATOMIC_REDIS_STATUS.set(redis_status);
    ATOMIC_CHAIN_STATUS.set(chain_status);
    ATOMIC_BLOCK_TIME_DELTA.set(block_time_delta);
    
    return super(MyRequestHandler, self).do_GET()


  def do_GET(self):
    parsed_path = urllib.parse.urlsplit(self.path)
    query = urllib.parse.parse_qs(parsed_path.query)
    if "target" in query:
      self.host = query['target'][0]
      print(getTimestamp() + ": Atomic API Exporter request received. target = " + self.host, flush=True)
      self.atomicAPI()
    else:
      print(getTimestamp() + ": Atomic API Exporter request received. target = None", flush=True)
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"No target\n")


if __name__ == '__main__':
  PORT = 8000
  print(getTimestamp() + ": Atomic API Exporter started. Listening on PORT " + str(PORT), flush=True)
  # ENDPOINT = sys.argv[2]
  ENDPOINT = ''

  server_address = ('', int(PORT))
  HTTPServer(server_address, MyRequestHandler).serve_forever()
