from subprocess import check_output
import configparser
import iperf3
import json

client = iperf3.Client()
config = configparser.ConfigParser()
config.sections()
config.read('main.conf')
config.sections()

client.duration = 1
client.server_hostname = config['DEFAULT']['Hostname']
client.port = config['DEFAULT']['Port']
client.protocol = 'udp'

# print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
result = client.run()
print("Performing iperf test.....")
if result.error:
    print(result.error)
else:
    with open('iperf.json', 'w') as iperf_file:
        json.dump(result.json, iperf_file)

print("Complete!\n\nPerforming latency test....")

ping_json = json.loads(check_output(["pingparsing", client.server_hostname]))
with open('ping.json' , 'w') as ping_file:
        json.dump(ping_json, ping_file)

print("Complete!\n\nPerforming speetest.net test....")

speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
with open('speedtest.json' , 'w') as speedtest_file:
        json.dump(speedtest_json, speedtest_file)

print("Complete!\n")
