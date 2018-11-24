
# -*- coding: utf-8 -*-

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

from webthing import (Action, Event, Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import time
import uuid
import subprocess
import psutil

def get_temp():
    if not hasattr(psutil, "sensors_temperatures"):
        sys.exit("platform not supported")
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
        print("%s" % average)
    return average

def make_thing():
    thing = Thing('CPU Temp Sensor', ['MultiLevelSensor'], 'A web connected temperature sensor')

    thing.add_property(
        Property(thing,
                 'temperature',
                 Value(get_temp()),
                 metadata={
                     '@type': 'LevelProperty',
                     'label': 'Temperature',
                     'type': 'number',
                     'description': 'The CPU temperature in degrees Celcius',
                     'unit': 'degrees Celcius',
                 }))

    return thing


def run_server():
    thing = make_thing()

    # If adding more than one thing, use MultipleThings() with a name.
    # In the single thing case, the thing's name will be broadcast.
    server = WebThingServer(SingleThing(thing), port=8888)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')

if __name__ == '__main__':
    logging.basicConfig(
        level=10,
        format="%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s"
    )

    run_server()
