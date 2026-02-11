"""
Elasticsearch connection management
"""

from typing import Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ElasticsearchException

from app.config.settings import settings

_es_client: Optional[AsyncElasticsearch] = None


async def init_es() -> None:
    global _es_client

    if _es_client is not None:
        return

    es = AsyncElasticsearch(
        hosts=[settings.elasticsearch_url],
        request_timeout=settings.elasticsearch_timeout,
        retry_on_timeout=True,
        max_retries=3,
    )

    try:
        await es.info()  # fail fast
    except ElasticsearchException:
        await es.close()
        raise

    _es_client = es


async def close_es() -> None:
    global _es_client

    if _es_client and not _es_client.closed:
        await _es_client.close()

    _es_client = None


def get_es() -> AsyncElasticsearch:
    if _es_client is None:
        raise RuntimeError("Elasticsearch client is not initialized")
    return _es_client


