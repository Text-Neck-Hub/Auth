import json
import atexit
import threading
import logging
from typing import Optional, Dict, Any, Iterable, Tuple

from confluent_kafka import Producer
from django.conf import settings

logger = logging.getLogger("prod")


class KafkaClient:
    _producer: Optional[Producer] = None
    _lock = threading.Lock()

    @staticmethod
    def _delivery(err, msg):
        if err:
            logger.error("[KAFKA][ERROR] %s topic=%s",
                         err, msg.topic() if msg else None)
        else:
            logger.info(
                "[KAFKA][OK] %s[%s]@%s key=%s",
                msg.topic(), msg.partition(), msg.offset(), msg.key()
            )

    @classmethod
    def get_producer(cls) -> Producer:
        if not getattr(settings, "KAFKA_ENABLED", True):
            raise RuntimeError(
                "Kafka disabled by settings.KAFKA_ENABLED=False")

        if cls._producer is None:
            with cls._lock:
                if cls._producer is None:
                    conf = {
                        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                        **getattr(settings, "KAFKA_PRODUCER_CONFIG", {}),
                    }
                    cls._producer = Producer(conf)
                    atexit.register(lambda: cls._producer.flush(5))
        return cls._producer

    @classmethod
    def send(
        cls,
        topic: str,
        key: Optional[str],
        value: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
    ):
        logger.debug("[KAFKA][SEND] topic=%s key=%s", topic, key)
        if not getattr(settings, "KAFKA_ENABLED", True):
            logger.debug("[KAFKA][SKIP] disabled. topic=%s key=%s", topic, key)
            return

        p = cls.get_producer()
        hdrs: Optional[Iterable[Tuple[str, bytes]]] = None
        if headers:
            hdrs = [(k, (v if isinstance(v, bytes) else str(v).encode("utf-8")))
                    for k, v in headers.items()]

        payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
        k = key.encode("utf-8") if isinstance(key, str) else key

        try:
            p.produce(
                topic=topic,
                key=k,
                value=payload,
                headers=hdrs,
                on_delivery=cls._delivery,
            )
        except BufferError:

            p.poll(0.5)
            p.produce(
                topic=topic,
                key=k,
                value=payload,
                headers=hdrs,
                on_delivery=cls._delivery,
            )

        p.poll(0)
