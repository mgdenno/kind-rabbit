import json
import os
import pika
import requests
import time
from datetime import datetime
import socket

def callback(ch, method, properties, body):
        message = json.loads(body)
        print(f"[x] Received simulationId: {message['simulationId']}")
        # Do stuff here
        time.sleep(message["runTimeMs"]/1000)
        print(f"[x] {message['simulationId']} Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)

qusr = os.getenv('RABBITMQ_DEFAULT_USER', 'admin')
qpwd = os.getenv('RABBITMQ_DEFAULT_PASS', 'queue')
credentials = pika.PlainCredentials(qusr, qpwd)

while(True):
    try:
        params = pika.ConnectionParameters(host='rabbit-queue', port=5672, credentials=credentials)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=callback)
        channel.start_consuming()
    except socket.gaierror:
        time.sleep(10)
        continue
    except pika.exceptions.ConnectionClosedByBroker:
        time.sleep(10)
        continue
    except pika.exceptions.AMQPChannelError as err:
        print("Caught a channel error: {}, stopping...".format(err))
        break
    except pika.exceptions.AMQPConnectionError:
        print("Retrying connection...")
        time.sleep(10)
        continue