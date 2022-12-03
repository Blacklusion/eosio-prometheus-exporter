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

NODEOS_HEAD_BLOCK_TIME_DELTA_MS = Gauge(
    'NODEOS_HEAD_BLOCK_TIME_DELTA_MS', 'Head block time delta in millisec')
NODEOS_DB_STATE_SIZE_BYTES = Gauge('NODEOS_DB_STATE_SIZE_BYTES', 'DB Size in Bytes')
NODEOS_DB_STATE_USED_BYTES = Gauge('NODEOS_DB_STATE_USED_BYTES', 'DB Used size in bytes')
NODEOS_DB_STATE_FREE_BYTES = Gauge('NODEOS_DB_STATE_FREE_BYTES', 'DB Free size in bytes')


ENDPOINT = ""
PORT = ""

def getTimestamp():
  return str(datetime.now().isoformat())

def exitMsg(*args):
  print(getTimestamp() + ": NODEOS API Exporter exiting")
  sys.exit(0)

signal.signal(signal.SIGABRT, exitMsg)
# signal.signal(signal.SIGBREAK, exitMsg)#windows
signal.signal(signal.SIGHUP, exitMsg)    #Linux
signal.signal(signal.SIGINT, exitMsg)    #linux
signal.signal(signal.SIGTERM, exitMsg)   #linux
# signal.signal(signal.SIGEGV, exitMsg)  #windows

class MyRequestHandler(MetricsHandler):

  def nodeosAPI(self):
    # host = 'https://wax.blacklusion.io/v1/chain/get_info'
    j = requests.get(self.host).json()
    timeNow = datetime.now()
    timestamp = dateutil.parser.isoparse(j['head_block_time'])
    delta = (timeNow - timestamp).total_seconds() * 1000.0
    delta = max(0, delta)
    NODEOS_HEAD_BLOCK_TIME_DELTA_MS.set(delta)

    sizeBytes, usedBytes, freeBytes = -1, -1, -1
    if(self.dbTarget):
      k = requests.get(self.dbTarget)
      try:
        data = k.json()
      except json.decoder.JSONDecodeError:
        data = {}
      if (200 == k.status_code and data):
        freeBytes = data.get('free_bytes', -1)
        usedBytes = data.get('used_bytes', -1)
        sizeBytes = data.get('size', -1)

    NODEOS_DB_STATE_SIZE_BYTES.set(sizeBytes)
    NODEOS_DB_STATE_USED_BYTES.set(usedBytes)
    NODEOS_DB_STATE_FREE_BYTES.set(freeBytes)

    return super(MyRequestHandler, self).do_GET()


  def do_GET(self):
    self.host, self.dbTarget = '',''
    parsed_path = urllib.parse.urlsplit(self.path)
    query = urllib.parse.parse_qs(parsed_path.query)
    if "target" in query:
      self.host = query['target'][0]
    else:
      print(getTimestamp() + ": NODEOS API Exporter request received. target = None", flush=True)
      self.send_response(404)
      self.end_headers()
      self.wfile.write(b"No target\n")

    if "db_target" in query:
      self.dbTarget = query['db_target'][0]

    if len(self.host) > 0 and self.host != '':
      print(getTimestamp() + ": NODEOS API Exporter request received. target = " + self.host, flush=True)
      self.nodeosAPI()


if __name__ == '__main__':
  PORT = 8000
  print(getTimestamp() + ":"+": NODEOS API Exporter started. Listening on PORT " + str(PORT), flush=True)
  # ENDPOINT = sys.argv[2]
  ENDPOINT = ''

  server_address = ('', int(PORT))
  HTTPServer(server_address, MyRequestHandler).serve_forever()

