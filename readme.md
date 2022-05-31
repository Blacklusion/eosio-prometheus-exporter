# eosio-prometheus-exporter
Collect metrics for your Prometheus deployment using our purpose-built exporters for EOSIO based blockchains. It supports the following target types:
1. Nodeos
2. Hyperion
3. Atomic

All exporters are using the multi-target infrastructure, meaning that you will only need to set up a single exporter per server, that can handle multiple instances of e.g. nodeos.