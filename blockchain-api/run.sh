#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

docker run -d --rm --name blockchain-api -p 127.0.0.1:6100:8000 blockchain-api
