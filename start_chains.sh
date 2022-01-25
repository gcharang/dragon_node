#!/bin/bash

test_x=$(pgrep -a python3 | grep refresh_wallets.py)
test_y=$(pgrep -a python3 | grep start_chains.py)

if [[ ${#test_x} -lt 60 ]]; then
    if [[ ${#test_y} -lt 60 ]]; then
        /usr/bin/python3 /home/smk762/dragon_node/start_chains.py
    else
        echo "start_chains already running"
    fi
else
    echo "refresh_wallets is already running"
fi
