#!/bin/bash

starting_dir="${PWD}"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}"

if [ -x ./set-ipt.sh ]; then
  ./set-ipt.sh
else
  cat <<EOF

You should copy set-ipt.sh.example to set-ipt.sh and adjust the iptables settings in it
to work in your environment.  Also make set-ipt.sh executable.
The reason this is neccessary is that docker by default will allow full access through
iptables for any published ports.  You almost certainly don't want this to happen.
If you are protected by some other firewall mechanism (another device) other than
iptables and/or ufw - then you might be able to ignore doing this.
Currently the setup for the applications in this repository use ports 6100-6102.
The example script blocks access to them from the outside world, with the exception
of a management IP address.  After making set-ipt.sh please adjust the setting(s) in
it to improve security for your system.

EOF
fi

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
