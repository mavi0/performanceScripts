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

class Perf:
    def __init__(self):
        self.__time = datetime.now()
        # Try to load vars from env. If not
        self.__host_id = self.__load_vars(os.environ['HOSTNAME'], "perf.manyproject.uk")
        self.__client_id = self.__load_vars(os.environ['CLIENT_ID'], "default-id")
        self.__duration = self.__load_vars_int(os.environ['DURATION'], 20)
        self.__protocol = self.__load_vars(os.environ['PROTOCOL'], "tcp")
        self.__blksize = self.__load_vars_int(os.environ['BLKSIZE'], 2048)
        self.__num_streams = self.__load_vars_int(os.environ['NUM_STREAMS'], 4)
        self.__base_port = self.__load_vars_int(os.environ['PORT'], 5201)
        self.__interval = self.__load_vars_int(os.environ['INTERVAL'], 300)
        self.__output = {}
        self.__output["host_id"] = self.__host_id
        self.__output["client_id"] = self.__client_id
        self.__output["datetime"] = self.__time

    def __load_vars(self, env_var, default):
        try:
            if env_var:
                return env_var
            else:
                return default
        except:
            return default

    def __load_vars_int(self, env_var, default):
        try:
            return int(load_vars(env_var, default))
        except:
            return default

    def __iperf(self, config_port):
        port = config_port

        if config_port < 1:
            port = self.__base_port

        client = iperf3.Client()
        client.duration = self.__duration
        client.host_id = self.__host_id
        client.port = port
        client.protocol = self.__protocol
        client.blksize = self.__blksize
        client.num_streams = self.__num_streams
        result = client.run()

        if result.error:
            print(result.error)
            # if the server is busy try a new port - there are 4 daemons running. Iterate though these until we get a success. Sure, this could have a negative impact on performance but most of the networks we're testing are sub 100Mbit/s
            port += 1
            if port > self.__base_port + 4:
                port = self.__base_port

            logger.warning("Retrying on port %s" % port)
            sleep(1)
            self.__iperf(port)
        else:
            return result.json
    
    def iperf_test(self):
        try:
            logger.info("Performing Iperf Test..")
            self.__output["iperf"] = self.__iperf(0)
        except:
            logger.warning(
                "There was an error performing the TCP iPerf test. Proceeding...")
            pass

    def ping_test(self):
        try:
            logger.info("Complete!\n\nPerforming latency test....")
            ping_json = json.loads(check_output(["pingparsing", self.__host_id]))
            ping_json[self.__host_id]['jitter'] = ping_json[self.__host_id]["rtt_max"] - ping_json[
                self.__host_id]["rtt_min"]
            self.__output["ping"] = ping_json

        except:
            logger.warning(
                "There was an error performing the latency test. Proceeding...")
            pass

    def speedtest_test(self):
        try:
            logger.info("Complete!\n\nPerforming speetest.net test....")

            speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
            self.__output["speedtest"] = speedtest_json

        except:
            logger.warning(
                "There was an error performing the speedtest test. Proceeding...")
            pass
    
    def get_output(self):
        return self.__output
    
    def get_time(self):
        return self.__time
    
    def get_interval(self):
        return self.__interval

def check_filename(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

if __name__ == "__main__":
    while True:
        perf = Perf()
        perf.iperf_test()
        perf.ping_test()
        perf.speedtest_test()
        
        perf_file = "/share/perf.json"
        log_file = "/log/" + str(perf.get_time()) + ".json"
        check_filename(perf_file)
        check_filename(log_file)

        with open('%s' % perf_file, 'w') as f:
            json.dump(perf.get_output(), f)

        with open('%s' % log_file, 'w') as f:
            json.dump(perf.get_output(), f)

        logger.info("Complete!\n")

        sleep(perf.get_interval())