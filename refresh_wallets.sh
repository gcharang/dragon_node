#!/bin/bash

x=0;
username="smk762"
test=$(pgrep -a python3 | grep 'start_chains')

while [ $x -le 10 ];
    do
      if [ ${#test} -gt 30 ]; then
         test=$(pgrep -a python | grep 'start_chains')
         $((x++))
         echo "start_chains is running"
         sleep 20
      else
         echo "refreshing wallets..."
         /usr/bin/python3 /home/${username}/dragon_node/refresh_wallets.py
         x=11
      fi
done
