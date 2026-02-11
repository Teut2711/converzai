"""
Elasticsearch connection management
"""

from typing import Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, TransportError

from app.config.settings import settings

_es_client: Optional[AsyncElasticsearch] = None


async def init_es() -> None:
    global _es_client

    if _es_client is not None:
        return

    es = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        timeout=settings.elasticsearch_timeout,
        max_retries=3,
        retry_on_timeout=True,
    )

    try:
        await es.ping()
        _es_client = es
    except ConnectionError:
        await es.close()
        raise


async def close_es() -> None:
    global _es_client

    if _es_client is None:
        return

    try:
        await _es_client.close()
    except (ConnectionError, TransportError):
        pass
    finally:
        _es_client = None


async def get_es() -> Optional[AsyncElasticsearch]:
    return _es_client


