#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
import sys
import logging
import argparse
from Monitors import network

__author__ = "Jesse S"
__license__ = "GNU GPL v2.0"
__version__ = "1.5"
__email__ = "jelloeater@gmail.com"

LOG_FILENAME = "NetworkMonitor.log"


def main():
    """ Take arguments and direct program """
    parser = argparse.ArgumentParser(description="A Network Stats Database Report Generator"
                                                 " (http://github.com/Jelloeater/NetworkMonitor)",
                                     version=__version__,
                                     epilog="Please specify action")

    parser.add_argument("-d",
                        "--delay",
                        action="store",
                        type=int,
                        default=600,
                        help="Wait x second between checks (10 min)")

    parser.add_argument("-a",
                        "--alert_timeout",
                        action="store",
                        type=int,
                        default=60,
                        help="Wait x minutes between alerts (1 hr)")

    parser.add_argument("-t",
                        "--host_timeout",
                        action="store",
                        type=int,
                        default=10,
                        help="Wait x seconds for failure (10)")

    parser.add_argument("-m",
                        "--monitor",
                        action="store",
                        type=int,
                        default=10,
                        help="Wait x seconds for failure (10)")

    parser.add_argument("-s",
                        "--server",
                        action="store",
                        type=str,
                        default='google.com',
                        help="Wait x seconds for failure (10)")

    parser.add_argument("--debug",
                        action="store_true",
                        help="Debug Mode Logging")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                            level=logging.DEBUG)
        logging.debug(sys.path)
        logging.debug(args)
        logging.debug('Debug Mode Enabled')
    else:
        logging.basicConfig(filename=LOG_FILENAME,
                            format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                            level=logging.WARNING)

    s = CheckServer(sleep_delay=args.delay, alert_timeout=args.alert_timeout, host_timeout=args.host_timeout,
                    hostname=args.server)
    # Create new mode object for flow, I'll buy that :)

    if len(sys.argv) == 1:  # Displays help and lists servers (to help first time users)
        parser.print_help()
        sys.exit(1)

    # Magic starts here
    if args.server:
        s.ping_server()


class CheckServer(object):  # Uses new style classes
    def __init__(self, sleep_delay, alert_timeout, host_timeout, hostname):
        self.sleep_delay = sleep_delay
        self.alert_timeout = alert_timeout
        self.host_timeout = host_timeout
        self.sl_host = hostname

    def ping_server(self):
        """ Picks either TCP, Ping host, or check web, depending on args """

        logging.debug("Checking host: " + str(self.sl_host))
        up_down_flag = network.MonitorHost(host=self.sl_host, timeout=self.host_timeout).run_test()
        logging.debug("up_down_flag: " + str(up_down_flag))
        if up_down_flag is False:
            self.server_down_actions()
        else:
            logging.info(self.sl_host + ' -  ' + ' is UP')

    def server_down_actions(self):
        """ Core logic for driving program """
        print()


if __name__ == "__main__":
    main()
