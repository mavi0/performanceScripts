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

logging.info("Performing fast.com test....")

download = 0

try:
    download = check_output("fast")
except:
    d = 0

# print(check_output("fast", shell=True, stderr=subprocess.STDOUT))
# download = check_output("fast")

print("{download:", download, "}")

logging.info("Complete!\n")
