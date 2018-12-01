from asyncio import sleep, CancelledError, get_event_loop
from webthing import (Action, Event, MultipleThings, Property, Thing, Value,
                      WebThingServer)
import logging
import random
import time
import uuid
import subprocess
import psutil
import socket


class CPUTempSensor(Thing):
    """A CPU temperature sensor which updates its measurement every few seconds."""

    def __init__(self):
        Thing.__init__(self,
                       'CPU Temp ' + socket.gethostname(), 
                       ['MultiLevelSensor'],
                       'A web connected CPU temp sensor')

        self.level = Value(0.0)
        self.add_property(
            Property(self,
                     'level',
                     self.level,
                     metadata={
                         '@type': 'LevelProperty',
                         'label': 'Temperature',
                         'type': 'number',
                         'description': 'The current temperature in degrees Celsius',
                         'unit': '°C',
                         'readOnly': True,
                     }))

        logging.debug('starting the sensor update looping task')
        self.sensor_update_task = \
            get_event_loop().create_task(self.update_level())

    async def update_level(self):
        try:
            while True:
                await sleep(60)
                new_level = self.get_temperature()
                logging.debug('setting new CPU temperature: %s', new_level)
                self.level.notify_of_external_update(new_level)
        except CancelledError:
            # We have no cleanup to do on cancellation so we can just halt the
            # propagation of the cancellation exception and let the method end.
            pass

    def cancel_update_level_task(self):
        self.sensor_update_task.cancel()
        get_event_loop().run_until_complete(self.sensor_update_task)

    @staticmethod
    def get_temperature():
        temps = psutil.sensors_temperatures()
        if not temps:
            sys.exit("can't read any temperature")
        for name, entries in temps.items():
            sum=0
            count=0
            for entry in entries:
               # print("    %-20s %s °C (high = %s °C, critical = %s °C)" % ( entry.label or name, entry.current, entry.high, entry.critical))
               sum=sum+entry.current 
               count=count+1
            average = sum / count
            #print("%s" % average)
        return average


def run_server():
    # Create a thing that represents a humidity sensor
    sensor = CPUTempSensor()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(MultipleThings([sensor], 'CPUTempSensor'), port=8886)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.debug('canceling the sensor update looping task')
        sensor.cancel_update_level_task()
        logging.info('stopping the server')
        server.stop()
        logging.info('done')


if __name__ == '__main__':
    if not hasattr(psutil, "sensors_temperatures"):
        sys.exit("platform not supported")
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )
    run_server()


