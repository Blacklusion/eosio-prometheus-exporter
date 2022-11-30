#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

docker run -d --rm --name atomic-api -p 127.0.0.1:6102:8000 atomic-api
