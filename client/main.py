import time
import configparser
import iperf3
import json
from subprocess import check_output
from datetime import datetime
from time import sleep

# TO DO: also save json files to unique file, for logs. ALSO retry iperf when can't connect

time = datetime.now()

server_hostname = ""


def iperf(config_file):
    global server_hostname
    config = configparser.ConfigParser()
    config.sections()
    config.read(config_file)
    config.sections()

    duration = int(config['DEFAULT']['duration'])
    protocol = config['DEFAULT']['protocol']
    blksize = int(config['DEFAULT']['blksize'])
    num_streams = int(config['DEFAULT']['num_streams'])
    base_port = int(config['DEFAULT']['port'])
    server_hostname = config['DEFAULT']['hostname']
    
    port = base_port
    client = iperf3.Client()
    client.duration = duration
    client.server_hostname = server_hostname
    client.port = port
    client.protocol = protocol
    client.blksize = blksize
    client.num_streams = num_streams

    # print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    result = client.run()
    if result.error:
        print(result.error)
        # if the server is busy try a new port - there are 4 daemons running. Iterate though these until we get a success. Sure, this could have a negative impact on performance but most of the networks we're testing are sub 100Mbit/s
        port += 1
        if port > base_port + 4:
            port = base_port

        print("Retrying on port %s" % port)
        sleep(1)
        iperf(port)
    else:
        return result.json

def save_json(json_export, file_name, log_dir):
    with open('%s' % file_name, 'w') as out_file:
        json.dump(json_export, out_file)

    log_file = log_dir + '/' + str(time) + '.json'
    with open(log_file, 'w') as out_log:
        json.dump(json_export, out_log)


def iperfTCP():
    print("Performing iperf TCP test.....")
    result = iperf("main.conf")
    save_json(result, "iperf.json", "iperfLogs")


def iperfUDP():
    print("Performing iperf UDP test.....")
    result = iperf("udp.conf")
    save_json(result, "iperfUDP.json", "iperfLogsUDP")


try:
    iperfTCP()
except:
    print("There was an error performing the TCP iPerf test. Proceeding...")
    pass

try:
    iperfUDP()
except:
    print("There was an error performing the UDP iPerf test. Proceeding...")
    pass

try:
    print("Complete!\n\nPerforming latency test....")
    ping_json = json.loads(check_output(["pingparsing", server_hostname]))
    ping_json[server_hostname]['jitter'] = ping_json[server_hostname]["rtt_max"] - ping_json[server_hostname]["rtt_min"]
    # fix for zabbix. cant escape periods
    json_hostname = server_hostname.replace(".", "_")
    ping_json_hostname = {}
    ping_json_hostname[json_hostname] = ping_json.pop(server_hostname)

    save_json(ping_json_hostname, "ping.json", "pingLogs")

except:
    print("There was an error performing the latency test. Proceeding...")
    pass

try:
    print("Complete!\n\nPerforming speetest.net test....")

    speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
    save_json(speedtest_json, "speedtest.json", "speedtestLogs")

except:
    print("There was an error performing the speedtest test. Proceeding...")
    pass
print("Complete!\n")
