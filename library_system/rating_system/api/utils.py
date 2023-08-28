from confluent_kafka import Producer

producer_config = {
    'bootstrap.servers': 'kafka1:19091',
    'message.timeout.ms': 1000
}
topic = "Rating"
producer = Producer(producer_config)

def send_message(username, message):
    headers = [("username", username.encode("utf-8"))]
    producer.produce(
        topic, key="-", 
        value=message.encode("utf-8"), 
        headers=headers
    )
    producer.flush()