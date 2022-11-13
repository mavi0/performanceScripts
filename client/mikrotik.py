import os
import coloredlogs, logging
from datetime import datetime
from time import sleep
import json
import paramiko
import time
import re


logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG", logger=logger)


class MikrotikBtest:
    def __init__(self):
        self.__time = datetime.now()
        # Try to load vars from env. If not, load defaults
        self.__client_id = os.environ.get("CLIENT_ID", "default-id")
        self.__cpe_uname = os.environ.get("MIKROTIK_UNAME", "admin")
        self.__cpe_passwd = os.environ.get("MIKROTIK_PASSWD", "admin")
        self.__cpe_hostname = os.environ.get("MIKROTIK_HOSTNAME", "192.168.88.1")
        self.__mikrotik_server = os.environ.get("MIKROTIK_SERVER", "192.168.88.1")
        self.__output = {}
        self.__output["client_id"] = self.__client_id
        self.__output["datetime"] = str(self.__time)

    def __scrape(self):
        # try:
        logger.info("Connecting to Mikrotik device....")
        
        stats = {}

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            self.__cpe_hostname,
            username=self.__cpe_uname,
            password=self.__cpe_passwd,
            allow_agent=False,
            look_for_keys=False,
        )

        logger.info("Connected to: " + self.__cpe_uname + "@" + self.__cpe_hostname)
        logger.info("Performing Receive test..")

        stdin, stdout, stderr = ssh.exec_command(
            "/tool bandwidth-test address="
            + self.__mikrotik_server
            + " direction=receive duration=10s"
        )
        sleep(1)
        out = stdout.readlines()
        stats["receiveLost"] = float(re.findall("\d+", out[-8])[0])
        stats["receiveRx"] = float(re.findall("\d+", out[-9])[0])

        logger.info("Performing Transmit test..")
        stdin, stdout, stderr = ssh.exec_command(
            "/tool bandwidth-test address="
            + self.__mikrotik_server
            + " direction=transmit duration=10s"
        )
        sleep(1)
        stats["transmitTx"] = float(re.findall("\d+", stdout.readlines()[-8])[0])

        logger.info("Performing Both test..")
        stdin, stdout, stderr = ssh.exec_command(
            "/tool bandwidth-test address="
            + self.__mikrotik_server
            + " direction=both duration=10s"
        )
        sleep(1)
        out = stdout.readlines()
        stats["bothLost"] = float(re.findall("\d+", out[-9])[0])
        stats["bothRx"] = float(re.findall("\d+", out[-10])[0])
        stats["bothTx"] = float(re.findall("\d+", out[-13])[0])

        logger.info("Stats Dump:\n" + json.dumps(stats, indent=2))

        ssh.close()

        self.__output["mikrotik_stats"] = stats

    def get_output(self):
        self.__scrape()
        return self.__output
