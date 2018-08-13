# from subprocess import call
# import configparser

# call(["ls", "-l"])
#
# # config = configparser.ConfigParser()
# # config['DEFAULT'] = {'ServerAliveInterval': '45',
# #                      'Compression': 'yes',
# #                      'CompressionLevel': '9'}
# # config['bitbucket.org'] = {}
# # config['bitbucket.org']['User'] = 'hg'
# # config['topsecret.server.com'] = {}
# # topsecret = config['topsecret.server.com']
# # topsecret['Port'] = '50022'     # mutates the parser
# # topsecret['ForwardX11'] = 'no'  # same here
# # config['DEFAULT']['ForwardX11'] = 'yes'
# # with open('example.ini', 'w') as configfile:
# #   config.write(configfile)
#
# config = configparser.ConfigParser()
# config.sections()
# # []
# config.read('example.ini')
# # ['example.ini']
# config.sections()
# # ['bitbucket.org', 'topsecret.server.com']
# 'bitbucket.org' in config
# # True
# 'bytebong.com' in config
# # False
# config['bitbucket.org']['User']
# # 'hg'
# config['DEFAULT']['Compression']
# # 'yes'
# topsecret = config['topsecret.server.com']
# topsecret['ForwardX11']
# # 'no'
# topsecret['Port']
# #'50022'
# for key in config['bitbucket.org']: print(key)
#
# config['bitbucket.org']['ForwardX11']
# # 'yes'

#!/usr/bin/env python3

import iperf3
import json

client = iperf3.Client()
client.duration = 1
client.server_hostname = '148.88.224.176'
client.port = 5201
client.protocol = 'udp'


print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
result = client.run()

if result.error:
    print(result.error)
else:
    print('')
    print('JSON: {0}'.format(result.json))
    print('Test completed:')
    print('  started at         {0}'.format(result.time))
    print('  bytes transmitted  {0}'.format(result.bytes))
    print('  jitter (ms)        {0}'.format(result.jitter_ms))
    print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))

    print('Average transmitted data in all sorts of networky formats:')
    print('  bits per second      (bps)   {0}'.format(result.bps))
    print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
    print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
    print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
    print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))
    with open('data.txt', 'w') as outfile:
        json.dump(result.json, outfile)
