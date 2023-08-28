from confluent_kafka import Consumer, KafkaError
import psycopg2
import datetime
import threading

def receiver():
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

    print("conn success!")

    while True:
        msg = c.poll(0.1)
        if msg is None:
            continue
        elif not msg.error():
            try:
                topic = msg.topic()
                message_value = msg.value().decode('utf-8')
                header = {key: value.decode('utf-8') for key, value in msg.headers()}
                key = msg.key().decode('utf-8')
                timestamp = datetime.datetime.fromtimestamp(int(msg.timestamp()[1]) // 1000)


                print(topic)
                print(message_value)
                print(header)
                print(key)
                print(timestamp)

                
                insert_query = """
                    INSERT into stats
                    (topic, message_value, username, key, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (topic, message_value, header["username"], key, timestamp))
                conn.commit()
                print("Success!")
            except Exception as ex:
                print("Unable to write to the DB: " + str(ex))

        elif msg.error().code() == KafkaError._PARTITION_EOF:
            print("End of partition reached")
        else:
            print("Error")

def start_kafka_processing():
    kafka_thread = threading.Thread(target=receiver)
    kafka_thread.start()