from confluent_kafka import Consumer, KafkaError
import psycopg2
import datetime

def process_existing_messages():
    c = Consumer({
        'bootstrap.servers': 'kafka1:19091',
        'group.id': 'django-consumer',
        'auto.offset.reset': 'earliest'
    })

    c.subscribe(['Gateway', 'Frontend', 'Rating', 'Library', 'Reservation'])

    conn = psycopg2.connect(
        dbname='stats',
        user='postgres',
        password='postgres',
        host='postgres',
        port='5432'
    )
    cursor = conn.cursor()

    while True:
        msg = c.poll(0.1)
        if msg is None:
            break 
        elif not msg.error():
            try:
                topic = msg.topic()
                message_value = msg.value().decode('utf-8')
                header = {key: value.decode('utf-8') for key, value in msg.headers()}
                key = msg.key().decode('utf-8')
                timestamp = datetime.datetime.fromtimestamp(int(msg.timestamp()[1]) // 1000)

                insert_query = """
                    INSERT into stats
                    (topic, message_value, username, key, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (topic, message_value, header["username"], key, timestamp))
                conn.commit()
                raise Exception("Success!")
                print("Success!")

            except Exception as ex:
                print("Unable to write to the DB:", str(ex))

        elif msg.error().code() == KafkaError._PARTITION_EOF:
            break
        else:
            print("Error")