#!/usr/bin/env python2.7
"""A python project for monitoring network resources
"""
import sys
import logging
import argparse
from Monitors import network

__author__ = "Jesse S"
__license__ = "GNU GPL v2.0"
__email__ = "jelloeater@gmail.com"

LOG_FILENAME = "TunnelCheck.log"


def main():
    """ Take arguments and direct program """
    parser = argparse.ArgumentParser(epilog="Please specify action")

    parser.add_argument("-t",
                        "--host_timeout",
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

    if len(sys.argv) == 1:  # Displays help and lists servers (to help first time users)
        parser.print_help()
        sys.exit(1)

    # Magic starts here
    if args.server:
        s = CheckServer(host_timeout=args.host_timeout, hostname=args.server)
        s.ping_server()


class CheckServer(object):  # Uses new style classes
    def __init__(self, host_timeout, hostname):
        self.host_timeout = host_timeout
        self.sl_host = hostname

    def ping_server(self):
        """ Picks either TCP, Ping host, or check web, depending on args """

        logging.debug("Checking host: " + str(self.sl_host))
        up_down_flag = network.MonitorHost(host=self.sl_host, timeout=self.host_timeout).run_test()
        logging.debug("up_down_flag: " + str(up_down_flag))
        if up_down_flag:
            logging.info(self.sl_host + ' -  ' + ' is UP')
            return True
        else:
            logging.info(self.sl_host + ' -  ' + ' is DOWN')
            return False


if __name__ == "__main__":
    main()
