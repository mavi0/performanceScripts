from subprocess import check_output
import configparser
import iperf3
import json

## TO DO: also save json files to unique file, for logs
client = iperf3.Client()
config = configparser.ConfigParser()
config.sections()
config.read('main.conf')
config.sections()

client.duration = 2
client.server_hostname = config['DEFAULT']['Hostname']
client.port = config['DEFAULT']['Port']
client.protocol = 'tcp'
client.blksize = 2048
client.num_streams = 4

# print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
result = client.run()
print("Performing iperf test.....")
if result.error:
    print(result.error)
else:
    # # print('')
    # # print('JSON: {0}'.format(result.json))
    # # print('Test completed:')
    # # print('  started at         {0}'.format(result.time))
    # # print('  bytes transmitted  {0}'.format(result.bytes))
    # # print('  jitter (ms)        {0}'.format(result.jitter_ms))
    # # print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))
    # #
    # # print('Average transmitted data in all sorts of networky formats:')
    # # print('  bits per second      (bps)   {0}'.format(result.bps))
    # # print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
    # print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
    # print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
    # print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))
    with open('iperf.json', 'w') as iperf_file:
        json.dump(result.json, iperf_file)

print("Complete!\n\nPerforming latency test....")
ping_json = json.loads(check_output(["pingparsing", client.server_hostname]))
ping_json[client.server_hostname]['jitter'] = ping_json[client.server_hostname]["rtt_max"] - ping_json[client.server_hostname]["rtt_min"]
json_hostname = client.server_hostname.replace(".", "_")                        #fix for zabbix. cant escape periods
ping_json_hostname = {}
ping_json_hostname[json_hostname] = ping_json.pop(client.server_hostname)

with open('ping.json' , 'w') as ping_file:
        json.dump(ping_json_hostname, ping_file)

print("Complete!\n\nPerforming speetest.net test....")

speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
with open('speedtest.json' , 'w') as speedtest_file:
        json.dump(speedtest_json, speedtest_file)

print("Complete!\n")
