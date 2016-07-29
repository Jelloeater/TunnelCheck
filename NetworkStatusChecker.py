import logging
from time import sleep
import pibrella
import threading
import logging
import urllib2
from nmap import PortScanner

__author__ = 'Jesse'


class GlobalVars(object):
    LOCAL_ROUTER = '192.168.11.1'  # RED_LIGHT
    WAN_ROUTER = '8.8.8.8'  # YELLOW_LIGHT
    FAR_SIDE_ROUTER = '192.168.1.1'  # GREEN_LIGHT
    TIMEOUT = 1
    BUZZER_ALLOW = True
    RESET_ALARM_COUNT_LIMIT = 360  # 5 seconds * 360 cycles = 30 mins
    ALARM_COUNTER = 0


class MonitorHost():
    """Ping a host to make sure it's up"""

    def __init__(self, host, timeout):
        self.host = host
        self.timeout = timeout
        if host == "":
            raise RuntimeError("missing hostname")

    def run_test(self):
        scan = PortScanner().scan(hosts=self.host, arguments='-sn --host-timeout ' + str(self.timeout) + 's')
        try:
            if scan['scan'][str(self.host)]['status']['state'] == 'up':
                return True
        except KeyError:  # If we cannot find the info in the key for the status, this means the host is down
            return False


class GetPRTGStatus():
    def __init__(self):
        import requests
        import xmltodict
        r = requests.get('http://probe/api/gettreenodestats.xml',
                         params={'username': 'prtgadmin', 'password': 'prtgadmin'})
        self.data = xmltodict.parse(r.text)

    def is_sensor_down(self):
        if self.data['data']['downsens'] > 0 or self.data['data']['downsens'] is not None:
            return True
        else:
            return False

    def is_sensor_warn(self):
        if self.data['data']['warnsens'] > 0 or self.data['data']['warnsens'] is not None:
            return True
        else:
            return False


class ButtonBackground(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    @staticmethod
    def run():
        """ Method that runs forever """

        def button_pressed(pin):  # Changes global bool flag for buzzer
            if GlobalVars.BUZZER_ALLOW:
                GlobalVars.BUZZER_ALLOW = False
                pibrella.buzzer.buzz(500)
                sleep(.50)
                pibrella.buzzer.stop()
            else:
                GlobalVars.BUZZER_ALLOW = True
                pibrella.buzzer.buzz(2000)
                sleep(.50)
                pibrella.buzzer.stop()

        while True:
            pibrella.button.pressed(button_pressed)
            sleep(.1)  # Sleep so we don't peg the CPU @ 100%


def main():
    VPN = False
    logging.basicConfig(format="[%(asctime)s] [%(levelname)8s] --- %(message)s (%(filename)s:%(lineno)s)",
                        level=logging.DEBUG)

    if MonitorHost(host=GlobalVars.FAR_SIDE_ROUTER, timeout=GlobalVars.TIMEOUT).run_test():
        # Is VPN UP?
        pibrella.light.green.off()
        status = GetPRTGStatus()

        # Double check to make sure alarm is really down, and not a false positive
        if status.is_sensor_down() or status.is_sensor_warn():
            i = 0  # Ugly FOR loop, because I'm lazy
            while i < 8:
                status = GetPRTGStatus()
                if status.is_sensor_down() or status.is_sensor_warn():
                    sleep(2)
                    i = i + 1
                else:
                    break


        if not status.is_sensor_down():
            pibrella.light.red.off()
        else:
            pibrella.light.red.pulse()

        if not status.is_sensor_warn():
            pibrella.light.yellow.off()
        else:
            if not GlobalVars.BUZZER_ALLOW:
                pibrella.light.yellow.off()
            else:
                pibrella.light.yellow.pulse()

    # Is VPN DOWN?
    else:
        pibrella.light.green.pulse()
        pibrella.light.red.pulse()
        pibrella.light.yellow.pulse()
        VPN = True

    if VPN and GlobalVars.BUZZER_ALLOW is True:
        pibrella.buzzer.buzz(88)
        sleep(.5)
        pibrella.buzzer.stop()

    # Timeout check to re-arm alarm
    if GlobalVars.BUZZER_ALLOW is False:
        if GlobalVars.ALARM_COUNTER < GlobalVars.RESET_ALARM_COUNT_LIMIT:
            GlobalVars.ALARM_COUNTER = GlobalVars.ALARM_COUNTER + 1
        else:
            GlobalVars.ALARM_COUNTER = 0
            GlobalVars.BUZZER_ALLOW = True


sleep(20)  # Wait for NIC to come up
ButtonBackground()
while True:
    main()
    sleep(5)
