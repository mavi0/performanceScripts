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

logging.info("Performing Speedtest.net test....")

speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))

with open('speedtest.json' , 'w') as speedtest_file:
        json.dump(speedtest_json, speedtest_file)

with open('speedtestLogs/%s.json' % time, 'w') as speedtest_log:
        json.dump(speedtest_json, speedtest_log)

logging.info("Complete!\n")
