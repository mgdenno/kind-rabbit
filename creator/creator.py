import sys
import json
import pika
import os
import time
import socket

def send_messages_to_queue():

    messages = [
        {
            "simulationId": 1,
            "runTimeMs": 1000
        },
        {
            "simulationId": 2,
            "runTimeMs": 1000
        },
        {
            "simulationId": 3,
            "runTimeMs": 10000
        },
        {
            "simulationId": 4,
            "runTimeMs": 10000
        },
        {
            "simulationId": 5,
            "runTimeMs": 5000
        },
        {
            "simulationId": 6,
            "runTimeMs": 5000
        },
        {
            "simulationId": 7,
            "runTimeMs": 1000
        },
        {
            "simulationId": 8,
            "runTimeMs": 1000
        }
    ]

    for message in messages:
        channel.queue_declare(queue='task_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ))
        print(f"[x] Sent simulationId: {message['simulationId']}")


qusr = os.getenv('RABBITMQ_DEFAULT_USER', 'admin')
qpwd = os.getenv('RABBITMQ_DEFAULT_PASS', 'queue')
credentials = pika.PlainCredentials(qusr, qpwd)

while(True):
    print("starting creator")
    try:
        print("trying to creator messages")
        # If running in the cluster, host=rabbit-queue, if running locally with port 5672 forwarded to localhost, 
        # then host=localhost
        params = pika.ConnectionParameters(host='rabbit-queue', port=5672, credentials=credentials)
        # params = pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        send_messages_to_queue()
        channel.connection.close()
        exit()
    except socket.gaierror as e:
        print(f"socket error: {e}")
        time.sleep(10)
        continue
    except pika.exceptions.ConnectionClosedByBroker:
        print("pika connection closed")
        time.sleep(10)
        continue
    except pika.exceptions.AMQPChannelError as err:
        print("Caught a channel error: {}, stopping...".format(err))
        break
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Retrying connection...{e}")
        time.sleep(10)
        continue