#!/bin/bash

starting_dir="${PWD}"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

collectors="atomic-api blockchain-api hyperion-api"
for collector in ${collectors}
do
  if [ -n "$(docker ps | grep ${collector})" ]; then
    docker stop "${collector}"
  fi
done

cd "${starting_dir}"

exit 0
