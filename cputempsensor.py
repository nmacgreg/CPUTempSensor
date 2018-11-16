from webthing import (Action, Event, Property, SingleThing, Thing, Value,
                      WebThingServer)
import logging
import time
import uuid
import subprocess

def get_temp():
    #result = subprocess.run(["sensors | grep \"Core 0\" | cut -c 16-19"], shell=True, stdout=subprocess.PIPE)
    return 32.5

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
