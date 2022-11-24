#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

docker run -d --rm --name hyperion-api -p 0.0.0.0:6101:8000 hyperion-api
