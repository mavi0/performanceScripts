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

logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s ',filename='iperf.log',level=logging.DEBUG)

duration = 20
protocol = 'tcp'
blksize = 2048
num_streams = 4
base_port = int(config['DEFAULT']['Port'])
server_hostname = config['DEFAULT']['Hostname']

def iperf( port ):
    client = iperf3.Client()
    logging.info("Performing iperf test.....")
    client.duration = duration
    client.server_hostname = server_hostname
    client.port = port
    client.protocol = protocol
    client.blksize = blksize
    client.num_streams = num_streams

    # print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    result = client.run()
    if result.error:
        logging.warning(result.error)
        #if the server is busy try a new port - there are 4 daemons running. Iterate though these until we get a success
        port += 1
        if port > base_port + 4:
            port = base_port

        logging.info("Retrying on port %s" % port)
        sleep(1)
        iperf(port)
    else:
        print(json.dumps(result.json))
        logging.info("Test Complete!")

        with open('iperfLogs/%s.json' % time, 'w') as iperf_log:
            json.dump(result.json, iperf_log)

        with open('iperf.json' % time, 'w') as iperf_log:
            json.dump(result.json, iperf_log)


iperf(base_port)
