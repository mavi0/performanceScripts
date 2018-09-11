from subprocess import check_output
# from pprint import pprint
import configparser
import sys
import json

with open('clients.json') as c:
    clients = json.load(c)

print(clients["test"])
#
# print("Complete!\n\nPerforming latency test....")
# ping_json = json.loads(check_output(["pingparsing", client.server_hostname]))
# ping_json[client.server_hostname]['jitter'] = ping_json[client.server_hostname]["rtt_max"] - ping_json[client.server_hostname]["rtt_min"]
# with open('ping.json' , 'w') as ping_file:
#         json.dump(ping_json, ping_file)
#
# print("Complete!\n\nPerforming speetest.net test....")
#
# speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
# with open('speedtest.json' , 'w') as speedtest_file:
#         json.dump(speedtest_json, speedtest_file)
#
# print("Complete!\n")
