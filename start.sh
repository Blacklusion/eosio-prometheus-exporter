#!/bin/bash

starting_dir="${PWD}"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

collectors="atomic-api blockchain-api hyperion-api"
for collector in ${collectors}
do
  cd "${collector}"
  if [ -z "$(docker images -q ${collector}:latest)" ]; then
    ./build.sh
  fi
  if [ -z "$(docker ps | grep ${collector})" ]; then
    ./run.sh
  fi
  cd ..
done

cd "${starting_dir}"

exit 0
