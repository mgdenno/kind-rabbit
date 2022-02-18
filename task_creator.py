import sys
import json
import pika

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

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        credentials=pika.PlainCredentials("admin", "queue")
    )
)
channel = connection.channel()

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

connection.close()

