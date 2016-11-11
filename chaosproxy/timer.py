import logging
import threading
import time

from datetime import datetime, timedelta


class Timer(threading.Thread):
    def __init__(self, stable_interval, unstable_interval):
        super(Timer, self).__init__()
        self.stable_interval = stable_interval if stable_interval else 0
        self.unstable_interval = unstable_interval if unstable_interval else 0
        self.timer_start = time.time()
        self.stable = True
        self.daemon = True
        self.start()

    def run(self):
        if self.stable_interval == self.unstable_interval == 0:
            logging.info(
                'stableInterval and unstableInterval on connections were not defined... Running Unstable mode forever'
            )
            self.stable = False
            return
        self.__log_mode(self.stable_interval)
        while True:
            end = time.time()
            if self.stable:
                stable = (end - self.timer_start) >= self.stable_interval
                if self.stable == stable:
                    self.stable = not self.stable
                    self.timer_start = time.time()
                    self.__log_mode(self.unstable_interval)
            else:
                stable = (end - self.timer_start) >= self.unstable_interval
                if self.stable != stable:
                    self.stable = not self.stable
                    self.timer_start = time.time()
                    self.__log_mode(self.stable_interval)
            time.sleep(1)

    def __log_mode(self, interval):
        date = (datetime.fromtimestamp(self.timer_start) + timedelta(seconds=interval)).strftime("%H:%M:%S")
        logging.info('Running %s mode for %ss until %s',
                     'stable' if self.stable else 'unstable', str(interval), str(date))

    def is_stable_period(self):
        return self.stable
