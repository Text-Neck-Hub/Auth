import json
from django.core.cache import cache
import logging

logger = logging.getLogger("prod")


class CacheAside:
    @staticmethod
    def get(key: str):
        try:
            raw = cache.get(key)
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.error(f"캐시 조회 실패 ({key}): {e}")
            return None

    @staticmethod
    def set(key: str, value: dict | list, timeout: int = 3600):
        try:
            cache.set(key, json.dumps(value), timeout=timeout)
            logger.info(f"캐시 저장 완료 ({key})")
        except Exception as e:
            logger.error(f"캐시 저장 실패 ({key}): {e}")

    @staticmethod
    def delete(key: str):
        try:
            cache.delete(key)
            logger.info(f"캐시 삭제 완료 ({key})")
        except Exception as e:
            logger.error(f"캐시 삭제 실패 ({key}): {e}")
