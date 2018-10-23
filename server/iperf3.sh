#!/usr/bin/env bash

iperf3 -p 5201 -s -D > iperf1Log.log
iperf3 -p 5202 -s -D > iperf2Log.log
iperf3 -p 5203 -s -D > iperf3Log.log
iperf3 -p 5204 -s -D > iperf4Log.log

# Remember to allow iperf through the firewall. Syntax:
# sudo ufw allow 5202/tcp
