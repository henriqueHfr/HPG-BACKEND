from confluent_kafka import Producer
import json
import os

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'email_topic'

producer_conf = {
    'bootstrap.servers': KAFKA_BROKER
}
producer = Producer(**producer_conf)

def enviaEmail(sender, recipients, body, subject):
    email_data = {
        'from': sender,
        'to': recipients,
        'subject': subject,
        'message': body
    }
    producer.produce(KAFKA_TOPIC, key='email', value=json.dumps(email_data))
    producer.flush()