# READS EVENTS (TEMPORARY RECEIVE EVENTS FROM KAFKA, LATER THIS WILL BE REPLACED WITH ETL TO LOAD INTO DB)
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "ecommerce-events",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("📥 Listening to Kafka topic...")

for message in consumer:
    event = message.value

