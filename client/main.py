import time, os, errno
import configparser
import iperf3
import json
import coloredlogs, logging
from subprocess import check_output
from datetime import datetime
from time import sleep

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

time = datetime.now()

host_id = os.environ['HOSTNAME']
client_id = os.environ['CLIENT_ID']

def iperf(config_port):
    duration = os.environ['DURATION']
    protocol = os.environ['PROTOCOL']
    blksize = int(os.environ['BLKSIZE'])
    num_streams = int(os.environ['NUM_STREAMS'])
    base_port = int(os.environ['PORT'])
    port = config_port

    if config_port < 1:
        port = base_port

    client = iperf3.Client()
    client.duration = duration
    client.host_id = host_id
    client.port = port
    client.protocol = protocol
    client.blksize = blksize
    client.num_streams = num_streams
    result = client.run()

    if result.error:
        print(result.error)
        # if the server is busy try a new port - there are 4 daemons running. Iterate though these until we get a success. Sure, this could have a negative impact on performance but most of the networks we're testing are sub 100Mbit/s
        port += 1
        if port > base_port + 4:
            port = base_port

        logger.warning("Retrying on port %s" % port)
        sleep(1)
        iperf(port)
    else:
        return result.json


def check_filename(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


output = {}

output["host_id"] = host_id
output["client_id"] = client_id
output["datetime"] = time

try:
    logger.info("Performing Iperf Test..")
    output["iperf"] = iperf(0)
except:
    logger.warning(
        "There was an error performing the TCP iPerf test. Proceeding...")
    pass

try:
    logger.info("Complete!\n\nPerforming latency test....")
    ping_json = json.loads(check_output(["pingparsing", host_id]))
    ping_json[host_id]['jitter'] = ping_json[host_id]["rtt_max"] - ping_json[
        host_id]["rtt_min"]
    output["ping"] = ping_json

except:
    logger.warning(
        "There was an error performing the latency test. Proceeding...")
    pass

try:
    logger.info("Complete!\n\nPerforming speetest.net test....")

    speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
    output["speedtest"] = speedtest_json

except:
    logger.warning(
        "There was an error performing the speedtest test. Proceeding...")
    pass

perf_file = "/share/perf.json"
log_file = "/log/" + str(time) + ".json"

check_filename(perf_file)
check_filename(log_file)

with open('%s' % perf_file, 'w') as f:
    json.dump(output, f)

with open('%s' % log_file, 'w') as f:
    json.dump(output, f)

logger.info("Complete!\n")
