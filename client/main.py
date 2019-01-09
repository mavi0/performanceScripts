import time
import configparser
import iperf3
import json
from subprocess import check_output
from datetime import datetime
from time import sleep

# TO DO: also save json files to unique file, for logs. ALSO retry iperf when can't connect
config = configparser.ConfigParser()
time = datetime.now()

config.sections()
config.read('main.conf')
config.sections()

duration = 20
protocol = 'tcp'
blksize = 2048
num_streams = 4
base_port = int(config['DEFAULT']['Port'])
server_hostname = config['DEFAULT']['Hostname']


def iperf(port):
    client = iperf3.Client()
    print("Performing iperf test.....")
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
        # if the server is busy try a new port - there are 4 daemons running. Iterate though these until we get a success
        port += 1
        if port > base_port + 4:
            port = base_port

        print("Retrying on port %s" % port)
        sleep(1)
        iperf(port)
    else:

        with open('iperf.json', 'w') as iperf_file:
            json.dump(result.json, iperf_file)

        with open('iperfLogs/%s.json' % time, 'w') as iperf_log:
            json.dump(result.json, iperf_log)


iperf(base_port)

print("Complete!\n\nPerforming latency test....")
ping_json = json.loads(check_output(["pingparsing", server_hostname]))
ping_json[server_hostname]['jitter'] = ping_json[server_hostname]["rtt_max"] - ping_json[server_hostname]["rtt_min"]
# fix for zabbix. cant escape periods
json_hostname = server_hostname.replace(".", "_")
ping_json_hostname = {}
ping_json_hostname[json_hostname] = ping_json.pop(server_hostname)

with open('ping.json', 'w') as ping_file:
    json.dump(ping_json_hostname, ping_file)

with open('pingLogs/%s.json' % time, 'w') as ping_log:
    json.dump(ping_json_hostname, ping_log)

print("Complete!\n\nPerforming speetest.net test....")

try:
    speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
except subprocess.CalledProcessError as e:
    speedtest_json =
with open('speedtest.json', 'w') as speedtest_file:
    json.dump(speedtest_json, speedtest_file)

with open('speedtestLogs/%s.json' % time, 'w') as speedtest_log:
    json.dump(speedtest_json, speedtest_log)

print("Complete!\n")
