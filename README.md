# THE FLOW (TBC):
1. Data Generator (data_generator.py) => Generates synthetic data, able to generate messy data
2. Batch Generator (batch_generator.py) => Generates 10,000+ of data, and saves into a csv file
3. Stream Generator (stream_generator.py) => Generates synthetic data of "real-time" events to Kafka
4. ETL Cleaning