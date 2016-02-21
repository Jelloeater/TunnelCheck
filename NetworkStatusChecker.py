import logging
import network

__author__ = 'Jesse'

LOCAL_ROUTER = '192.168.11.1'  # RED_LIGHT
WAN_ROUTER = '8.8.8.8'  # YELLOW_LIGHT
FAR_SIDE_ROUTER = '192.168.1.1'  # GREEN_LIGHT
TIMEOUT = 10


class Check(object):  # Uses new style classes
    def __init__(self, hostname):
        self.host_timeout = 10
        self.sl_host = hostname

    def ping(self):
        """ Picks either TCP, Ping host, or check web, depending on args """

        up_down_flag = network.MonitorHost(host=self.sl_host, timeout=self.host_timeout).run_test()
        if up_down_flag:
            logging.info(self.sl_host + ' -  ' + ' is UP')
            return True
        else:
            logging.info(self.sl_host + ' -  ' + ' is DOWN')
            return False


def main():
    logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                        level=logging.DEBUG)

    if network.MonitorHost(host=LOCAL_ROUTER, timeout=TIMEOUT).run_test():
        pass
    # Turn Red on

    if network.MonitorHost(host=WAN_ROUTER, timeout=TIMEOUT).run_test():
        pass
    # Turn Yellow on

    if network.MonitorHost(host=FAR_SIDE_ROUTER, timeout=TIMEOUT).run_test():
        pass
        # Turn Green on


main()
