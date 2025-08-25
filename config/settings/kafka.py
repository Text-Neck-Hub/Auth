import os
KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_DEFAULT_TOPIC = os.getenv("KAFKA_DEFAULT_TOPIC", "user-profile")

KAFKA_PRODUCER_CONFIG = {
    "linger.ms": 10,
    "batch.size": 131072,
    "compression.type": "lz4",
    "acks": "all",
    "enable.idempotence": True
}
