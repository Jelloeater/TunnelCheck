import logging
from time import sleep
import network
import pibrella
import threading

__author__ = 'Jesse'

LOCAL_ROUTER = '192.168.11.1'  # RED_LIGHT
WAN_ROUTER = '8.8.8.8'  # YELLOW_LIGHT
FAR_SIDE_ROUTER = '192.168.1.1'  # GREEN_LIGHT
TIMEOUT = 1


class ButtonBackground(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    @staticmethod
    def run():
        """ Method that runs forever """
        def button_pressed(pin):
            print("You pressed the button!")
            pibrella.buzzer.buzz(88)
            sleep(.5)
            pibrella.buzzer.stop()

        while True:
            pibrella.button.pressed(button_pressed)
            sleep(.1)  #Sleep so we don't peg the CPU @ 100%


def main():
    LAN = False
    WAN = False
    VPN = False
    logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                        level=logging.DEBUG)

    if network.MonitorHost(host=LOCAL_ROUTER, timeout=TIMEOUT).run_test():
        pibrella.light.red.off()
    else:
        logging.error('Router Down')
        pibrella.light.red.pulse()
        LAN = True

    if network.MonitorHost(host=WAN_ROUTER, timeout=TIMEOUT).run_test():
        pibrella.light.yellow.off()
    else:
        logging.error('Internet Down')
        pibrella.light.yellow.pulse()
        WAN = True

    if network.MonitorHost(host=FAR_SIDE_ROUTER, timeout=TIMEOUT).run_test():
        pibrella.light.green.off()
    else:
        logging.error('VPN Down')
        pibrella.light.green.pulse()
        VPN = True

    if LAN and WAN and VPN is True:
        pibrella.buzzer.buzz(88)
        sleep(.5)
        pibrella.buzzer.stop()
    else:
        pass

# sleep(20)  # Wait for NIC to come up
ButtonBackground()
while True:
    main()
    sleep(5)
