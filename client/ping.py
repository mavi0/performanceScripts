import time
import configparser
import iperf3
import json
import logging
from subprocess import check_output
from datetime import datetime
from time import sleep

## TO DO: also save json files to unique file, for logs. ALSO retry iperf when can't connect
config = configparser.ConfigParser()
time = datetime.now()

config.sections()
config.read('main.conf')
config.sections()

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s ',filename='ping.log',level=logging.DEBUG)

base_port = int(config['DEFAULT']['Port'])
server_hostname = config['DEFAULT']['Hostname']

logging.info("Performing latency test....")
ping_json = json.loads(check_output(["pingparsing", server_hostname]))
ping_json[server_hostname]['jitter'] = ping_json[server_hostname]["rtt_max"] - ping_json[server_hostname]["rtt_min"]
json_hostname = server_hostname.replace(".", "_")                        #fix for zabbix. cant escape periods
ping_json_hostname = {}
ping_json_hostname[json_hostname] = ping_json.pop(server_hostname)

print(json.dumps(ping_json_hostname))

with open('ping.json' , 'w') as ping_file:
    json.dump(ping_json_hostname, ping_file)

# with open('pingLogs/%s.json' % time, 'w') as ping_log:
#     json.dump(ping_json_hostname, ping_log)

logging.info("Complete!\n")
