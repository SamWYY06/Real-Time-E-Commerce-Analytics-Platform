import json
import time
from kafka import KafkaProducer
from ingestion.data_generator import generate_event

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda x: json.dumps(x).encode("utf-8")
)

print("🚀 Streaming started...")

while True:
    event = generate_event(messy=True)

    producer.send("ecommerce-events", event) # This is what makes this stream_generator.py file a kafka producer

    print("Sent:", event)

    time.sleep(1)