import time, os, errno, copy
import iperf3
import json
import coloredlogs, logging
import subprocess
from datetime import datetime
from time import sleep
from pathlib import Path
import speedtest
from mikrotik import MikrotikBtest


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

class Perf:
    def __init__(self):
        self.__time = datetime.now()
        # Try to load vars from env. If not, load defaults
        self.__host_id = os.environ.get('HOST_ID', "perf.manyproject.uk")
        self.__client_id = os.environ.get('CLIENT_ID', "default-id")
        self.__duration =  int(os.environ.get('DURATION', 20))
        self.__iperf_retry =  int(os.environ.get('IPERF_RETRY', 40))
        self.__protocol = os.environ.get('PROTOCOL', "UDP")
        self.__blksize =  int(os.environ.get('BLKSIZE', 2048))
        self.__num_streams =  int(os.environ.get('NUM_STREAMS', 4))
        self.__base_port =  int(os.environ.get('PORT', 5201))
        self.__port_range =  int(os.environ.get('PORT_RANGE', 4))
        self.__interval = int(os.environ.get('INTERVAL', 300))
        self.__output = {}
        self.__output["host_id"] = self.__host_id
        self.__output["client_id"] = self.__client_id
        self.__output["datetime"] = str(self.__time)

    # def __load_vars(self, env_var, default):
    #     try:
    #         if env_var:
    #             return env_var
    #         else:
    #             return default
    #     except:
    #         return default

    # def __load_vars_int(self, env_var, default):
    #     try:
    #         return int(load_vars(env_var, default))
    #     except:
    #         return default

    def mikrotik_btest(self):
        m = MikrotikBtest()
        self.__output["mikrotik"] = m.get_output()


    def __iperf(self):
        attempt = 0
        port = copy.deepcopy(self.__base_port)
        for attempt in range(self.__iperf_retry):            
            attempt += 1 
            # if self.__protocol == "TCP":
            #     logger.info("Performing TCP Iperf Test on port: %s" % port)
            #     client = iperf3.Client()
            #     client.duration = self.__duration
            #     client.server_hostname = self.__host_id
            #     client.port = port
            #     client.protocol = self.__protocol
            #     client.blksize = self.__blksize
            #     client.num_streams = self.__num_streams
            #     result = client.run()
            if self.__protocol == "UDP":
                logger.info("Performing UDP Iperf Test on port: %s" % port)
                attempt = 0
                for attempt in range(self.__iperf_retry):
                    dl_json = json.loads(subprocess.check_output(["iperf3", "-c", self.__host_id, "-i", "1", "-l", "1300", "-b", "600M", "-t", "10", "-R", "-u", "-J"]).decode('utf-8'))
                    if "end" in dl_json: break
                    if "error" in dl_json:
                        attempt += 1
                        logger.info("error - the server is busy running a test. Attempt: %s" % attempt)
                        if attempt == self.__iperf_retry: 
                            raise Exception("Too many retries perfroming UDP download") 
                        sleep(6)
                for attempt in range(self.__iperf_retry):
                    ul_json = json.loads(subprocess.check_output(["iperf3", "-c", self.__host_id, "-i", "1", "-l", "1300", "-b", "600M", "-t", "10", "-u", "-J"]).decode('utf-8'))
                    if "end" in ul_json: break
                    if "error" in ul_json:
                        attempt += 1
                        logger.info("error - the server is busy running a test. Attempt: %s" % attempt)
                        if attempt == self.__iperf_retry: 
                            raise Exception("Too many retries perfroming UDP download")
                        sleep(6)

                iperf_json = {}
                iperf_json["udp_dl"] = dl_json
                iperf_json["udp_ul"] = ul_json
                return iperf_json
  
            else:
                raise Exception("Incompatible Iperf port specified: " + self.__protocol) 

            # if result.error:
            #     print(result.error)
            #     # if the server is busy try a new port - there are 4 daemons running. Iterate though these until we get a success. Sure, this could have a negative impact on performance but most of the networks we're testing are sub 100Mbit/s
            #     port += 1
            #     if port > self.__base_port + self.__port_range:
            #         port = copy.deepcopy(self.__base_port)

            #     logger.warning("Retrying on port %s" % port)
            #     sleep(1)
            # else:
            #     return result.json
        
        return ""
    
    def iperf_test(self):
        try:
            self.__output["iperf"] = self.__iperf()
            logger.info("Complete!")
        except Exception as e:
            logger.warning(e)
            logger.warning(
                "There was an error performing the iperf test. Proceeding...")
            pass

    def ping_test(self):
        try:
            logger.info("Performing latency test....")
            ping_json = json.loads(subprocess.check_output(["pingparsing", self.__host_id]).decode('utf-8'))
            ping_json[self.__host_id]['jitter'] = ping_json[self.__host_id]["rtt_max"] - ping_json[
                self.__host_id]["rtt_min"]
            self.__output["ping"] = ping_json
            logger.info("Complete!")

        except Exception as e:
            logger.info(e)
            logger.warning(
                "There was an error performing the latency test. Proceeding...")
            pass

    def librespeed_test(self):
        try:
            logger.info("Performing librespeed test....")
            proc = subprocess.Popen(["/perfclient/speedtest-cli/out/librespeed-cli-linux-amd64", "--local-json", "servers.json", "--json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            speedtest_json = json.loads(err.decode('utf-8'))
            self.__output["librespeed"] = speedtest_json
            logger.info("Complete!")

        except Exception as e:
            logger.info(e)
            logger.warning(
                "There was an error performing the speedtest test. Proceeding...")
            pass

    def ookla_speedtest(self):
        try:
            logger.info("Performing ookla speedtest....")
            servers = []
            # If you want to test against a specific server
            # servers = [1234]
            threads = None
            # If you want to use a single threaded test
            # threads = 1
            s = speedtest.Speedtest()
            s.get_servers(servers)
            s.get_best_server()
            s.download(threads=threads)
            s.upload(threads=threads)
            s.results.share()
            results_dict = s.results.dict()
            # speedtest_json = json.loads(results_dict.decode('utf-8'))
            self.__output["ookla"] = results_dict
            logger.info("Complete!")
        except Exception as e:
            logger.info(e)
            logger.warning(
                "There was an error performing the ookla speedtest test. Proceeding...")
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
    # Path('/share/perf.json').touch()
    while True:
        perf = Perf()
        # perf.mikrotik_btest()
        # perf.ping_test()
        # perf.librespeed_test()
        # perf.ookla_speedtest()
        perf.iperf_test()

        print(perf.get_output())
        
        # perf_file = "/share/perf.json"
        # log_file = "/log/" + str(perf.get_time()) + ".json"
        
        # logger.info("Exporting logs to " + perf_file + " and " + log_file)
        # check_filename(perf_file)
        # check_filename(log_file)

        # with open('%s' % perf_file, 'w') as f:
        #     json.dump(perf.get_output(), f)

        # with open('%s' % log_file, 'w') as f:
        #     json.dump(perf.get_output(), f)

        logger.info("Complete!\nSleeping for " + str(perf.get_interval()) + " secs.")

        sleep(perf.get_interval())