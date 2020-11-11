import paho.mqtt.client as mqtt
import sys
import os
import jsonify
import logging
import utils.settings
import time
import threading
import json
import API.measurement
import API.authentication as auth
import API.identity

logger = logging.getLogger('Operation Listener')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.info('Logger on MQTT for DeviceControl was initialised')

def event(topic, payload):
    try:
        message = json.loads(payload)
        if 'source' in str(message):
            message['source']['id'] = str(auth.get().internalID)
            logger.info('The following topic arrived %s', payload)
            API.measurement.createMeasurement(json.dumps(message))
        else:
            raise ValueError
    except ValueError as e:
        return logger.error('Not valid json or valid structure')


def on_message_msgs(mosq, obj, msg):
    #print("Withing Callback")
    # This callback will only be called for messages with topics that matchs the assigned topics
    logger.debug('Callback function was initiated')
    logger.info('The following topic triggered a callback function: %s', msg.topic)
    logger.info('The following payload arrived: %s', msg.payload)
    logger.debug('Object with Event-Class will be created')
    threadEvent = threading.Thread(target=event, kwargs=dict(topic=msg.topic,payload=msg.payload), daemon=True)
    threadEvent.start()


def main():
    try:
        logger.debug('Setting prefix within MQTT broker for machine from config file')
        mqttSettings = utils.settings.mqtt()
        logger.debug('Initialising MQTT client with loaded credentials for listener')
        client = mqtt.Client(str(utils.settings.basic['deviceID']))
        logger.info('MQTT client with loaded credentials was initialised')
        client.username_pw_set(username=auth.get().MqttUser,password=auth.get().MqttPwd)
        operationsTopic = 's/ds'
        logger.info('Listening for callback on s/ds')
        client.message_callback_add(str(operationsTopic), on_message_msgs)
        logger.info('Connecting to MQTT Broker')
        client.tls_set()
        client.connect(auth.get().tenant, 1883, 60)
        client.subscribe("#", 0)
        logger.info('Start Loop forever and listening')
        client.loop_forever()
    except Exception as e:
        logger.error('The following error occured: ' + str(e))
        client.stop_loop()
        logger.warning('Loop forever stopped, disconnecting')
        client.disconnect()
        logger.debug('disconnected')

def start():
    try:
        while True:
            main()
            logger.error('Main loop left')
            time.sleep(10)
        logger.error('Main loop left')
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logger.error('The following error occured: ' + str(e))
        pass

def stop():
    print("Stopping")