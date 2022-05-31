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

BLOCKCHAIN_HEAD_BLOCK_TIME_DELTA_MS = Gauge(
    'BLOCKCHAIN_HEAD_BLOCK_TIME_DELTA_MS', 'Head block time delta in millisec')


ENDPOINT = ""
PORT = ""

def getTimestamp():
    return str(datetime.now().isoformat())

def exitMsg(*args):
  print(getTimestamp() + ": Blockchain API Exporter exiting")
  sys.exit(0)

signal.signal(signal.SIGABRT, exitMsg)
# signal.signal(signal.SIGBREAK, exitMsg)#windows
signal.signal(signal.SIGHUP, exitMsg)    #Linux
signal.signal(signal.SIGINT, exitMsg)    #linux
signal.signal(signal.SIGTERM, exitMsg)   #linux
# signal.signal(signal.SIGEGV, exitMsg)  #windows

class MyRequestHandler(MetricsHandler):

  def blockchainAPI(self):
    # host = 'https://wax.blacklusion.io/v1/chain/get_info'
    j = requests.get(self.host).json()
    # print(j)
    timeNow = datetime.now()
    timestamp = dateutil.parser.isoparse(j['head_block_time'])
    delta = (timeNow - timestamp).total_seconds() * 1000.0
    delta = max(0, delta)
    BLOCKCHAIN_HEAD_BLOCK_TIME_DELTA_MS.set(delta)
    return super(MyRequestHandler, self).do_GET()


  def do_GET(self):
    parsed_path = urllib.parse.urlsplit(self.path)
    query = urllib.parse.parse_qs(parsed_path.query)
    if ("target" in query):
      self.host = query['target'][0]
      print(getTimestamp() + ": Blockchain API Exporter request received. target = " + self.host , flush=True)
      self.blockchainAPI()

    else:
      print(getTimestamp() + ": Blockchain API Exporter request received. target = None" , flush=True)
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"No target\n")


if __name__ == '__main__':
  PORT = 8000
  print(getTimestamp() + ":"+": Blockchain API Exporter started. Listening on PORT " + str(PORT), flush=True)
  # ENDPOINT = sys.argv[2]
  ENDPOINT = ''

  server_address = ('', int(PORT))
  HTTPServer(server_address, MyRequestHandler).serve_forever()

