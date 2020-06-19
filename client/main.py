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
        # Try to load vars from env. If not, load defaults
        try:
            self.__host_id = os.environ['HOST_ID']
            self.__client_id = os.environ['CLIENT_ID']
            self.__duration =  int(os.environ['DURATION'])
            self.__protocol = os.environ['PROTOCOL']
            self.__blksize =  int(os.environ['BLKSIZE'])
            self.__num_streams =  int(os.environ['NUM_STREAMS'])
            self.__base_port =  int(os.environ['PORT'])
            self.__interval = int(os.environ['INTERVAL'])
        except:
            self.__host_id = "perf.manyproject.uk"
            self.__client_id = "default-id"
            self.__duration = 20
            self.__protocol = "tcp"
            self.__blksize = 2048
            self.__num_streams = 4
            self.__base_port = 5201
            self.__interval = 300

        self.__output = {}
        self.__output["host_id"] = self.__host_id
        self.__output["client_id"] = self.__client_id
        self.__output["datetime"] = str(self.__time)

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

    def __iperf(self, config_port, attempt):
        if attempt > 40:
            logger.error("Exceeded iperf retry.")
            return

        attempt += 1 

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
            self.__iperf(port, attempt)
        else:
            return result.json
    
    def iperf_test(self):
        try:
            logger.info("Performing Iperf Test..")
            self.__output["iperf"] = self.__iperf(0, 0)
            logger.info("Complete!")
        except:
            logger.warning(
                "There was an error performing the iperf test. Proceeding...")
            pass

    def ping_test(self):
        try:
            logger.info("Performing latency test....")
            ping_json = json.loads(check_output(["pingparsing", self.__host_id]))
            ping_json[self.__host_id]['jitter'] = ping_json[self.__host_id]["rtt_max"] - ping_json[
                self.__host_id]["rtt_min"]
            self.__output["ping"] = ping_json
            logger.info("Complete!")

        except:
            logger.warning(
                "There was an error performing the latency test. Proceeding...")
            pass

    def speedtest_test(self):
        try:
            logger.info("Performing speetest.net test....")

            speedtest_json = json.loads(check_output(["speedtest-cli", "--json"]))
            self.__output["speedtest"] = speedtest_json
            logger.info("Complete!")

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
        
        logger.info("Exporting logs to " + perf_file + " and " + log_file)
        check_filename(perf_file)
        check_filename(log_file)

        with open('%s' % perf_file, 'w') as f:
            json.dump(perf.get_output(), f)

        with open('%s' % log_file, 'w') as f:
            json.dump(perf.get_output(), f)

        logger.info("Complete!\nSleeping for " + str(perf.get_interval()) + " secs.")

        sleep(perf.get_interval())