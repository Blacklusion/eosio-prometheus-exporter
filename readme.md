# eosio-prometheus-exporter
Collect metrics for your Prometheus deployment using our purpose-built exporters for EOSIO based blockchains. It supports the following target types:
1. Nodeos
2. Hyperion
3. Atomic

All exporters are using the multi-target infrastructure, meaning that you will only need to set up a single exporter per server, that can handle multiple instances of e.g. nodeos.


The start.sh script will call each exporters run.sh script.
The run.sh scripts will create a docker user-defined bridge network for the containers to attach to.
Other applications that query these exporters should also attach to this network.  It is called 'eosio-exporters'.
The exporters can be reached on the network by name:
* atomic-api
* blockchain-api
* hyperion-api
And all will be at port 8000.
