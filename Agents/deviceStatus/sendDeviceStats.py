# coding=utf-8
import paho.mqtt.client as mqtt
import sys
import os
import subprocess
import jsonify
import logging
import utils.settings
import time
import threading
import json
import API.measurement
import API.authentication as auth
import API.identity
import API.inventory
import psutil
import json
import datetime

logger = logging.getLogger('Device Status updater')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('Logger for sending Docker Status to Platform')

def getMemoryStats():
    payload = {}
    try:
        payload['source'] = {"id": str(auth.get().internalID)}
        payload['type'] = "c8y_ThinEdge_Device_Stats"
        payload['time'] = datetime.datetime.strptime(
            str(datetime.datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f').isoformat() + "Z"
        memory = {}
        memory['free'] = {"value": psutil.virtual_memory().free}
        memory['used'] = {"value": psutil.virtual_memory().used}
        memory['total'] = {"value": psutil.virtual_memory().total}
        memory['percent'] = {"value": psutil.virtual_memory().percent}
        payload['Virtual Memory'] = memory
        return payload
    except Exception as e:
        logger.error('The following error occured: %s' % (str(e)))
        return payload

def getCPUStats():
    payload = {}
    try:
        payload['source'] = {"id": str(auth.get().internalID)}
        payload['type'] = "c8y_ThinEdge_Device_Stats"
        payload['time'] = datetime.datetime.strptime(
            str(datetime.datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f').isoformat() + "Z"
        cpu = {}
        cpu['load'] = {'value': psutil.cpu_percent(0)}
        payload['CPU'] = cpu
        return payload
    except Exception as e:
        logger.error('The following error occured: %s' % (str(e)))
        return payload

def getDiskStats():
    payload = {}
    try:
        payload['source'] = {"id": str(auth.get().internalID)}
        payload['type'] = "c8y_ThinEdge_Device_Stats"
        payload['time'] = datetime.datetime.strptime(
            str(datetime.datetime.utcnow()), '%Y-%m-%d %H:%M:%S.%f').isoformat() + "Z"
        disk = {}
        disk['total'] = {'value': psutil.disk_usage('/').total}
        disk['used'] = {'value': psutil.disk_usage('/').used}
        disk['free'] = {'value': psutil.disk_usage('/').free}
        disk['percent'] = {'value': psutil.disk_usage('/').percent}
        payload['Disk'] = disk
        return payload
    except Exception as e:
        logger.error('The following error occured: %s' % (str(e)))
        return payload


def main():
    try:
        logger.info('Sending new device stats')
        API.measurement.createMeasurement(json.dumps(getMemoryStats()))
        API.measurement.createMeasurement(json.dumps(getCPUStats()))
        API.measurement.createMeasurement(json.dumps(getDiskStats()))
        try:
            logger.debug(
                'Requesting sleep value from configuration of manage object')
            time.sleep(int(utils.settings.device()['c8y.device.status.update']))
        except:
            logger.warning('Configurated device update intervall not valid, using 10s instead.')
            time.sleep(10)
    except Exception as e:
        logger.error('The following error occured: %s' % (str(e)))

def start():
    try:
        while True:
            main()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error('The following error occured: ' + str(e))
        pass
