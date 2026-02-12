"""
SDK 2.0 - Search API
=====================

Full-text search, suggestions, aggregations and the builder pattern.

Prerequisite: run 02_basic_crud.py first to create the demo entities.

Source: ingestion/src/metadata/sdk/api/search.py
"""

from metadata.sdk import configure, Tables
from metadata.sdk.api.search import Search

configure(host="http://localhost:8585/api", jwt_token="<token>")

# ================================================================== #
# 1. Simple search — find our demo tables
# ================================================================== #
results = Search.search("customers", size=10)
print(f"Hits: {results}")

# ================================================================== #
# 2. Scoped search — target a specific index
# ================================================================== #
# Available indices include:
#   table_search_index, dashboard_search_index, topic_search_index,
#   pipeline_search_index, user_search_index, glossary_term_search_index, ...

results = Search.search(
    query="customers",
    index="table_search_index",
    size=20,
    sort_field="name",
    sort_order="asc",
)

# ================================================================== #
# 3. Filtered search — only our demo service
# ================================================================== #
# Field-level filtering requires Elasticsearch query DSL via search_advanced
results = Search.search_advanced({
    "query": {
        "bool": {
            "must": [{"match_all": {}}],
            "filter": [{"term": {"service.name": "sdk_demo_mysql"}}],
        }
    }
})

# ================================================================== #
# 4. Suggestions / autocomplete
# ================================================================== #
suggestions = Search.suggest("cust", field="name", size=5)
print(f"Suggestions: {suggestions}")

# ================================================================== #
# 5. Aggregations
# ================================================================== #
aggs = Search.aggregate(
    query="*",
    index="table_search_index",
    field="service.name",
)
print(f"Aggregations: {aggs}")

# ================================================================== #
# 6. Builder pattern — composable queries
# ================================================================== #
results = (
    Search.builder()
    .query("orders")
    .index("table_search_index")
    .size(50)
    .sort_field("name")
    .include_aggregations(True)
    .execute()
)
print(f"Builder results: {results}")

# ================================================================== #
# 7. Advanced search — pass a raw ES query body
# ================================================================== #
raw_query = {
    "query": {
        "bool": {
            "must": [{"match": {"name": "customers"}}],
            "filter": [{"term": {"service.name": "sdk_demo_mysql"}}],
        }
    }
}
results = Search.search_advanced(raw_query)

# ================================================================== #
# 8. Entity-level search shortcut
# ================================================================== #
# Every entity facade also exposes a .search() method that returns
# typed entities directly.

matching_tables = Tables.search("customers", size=10)
for t in matching_tables:
    print(f"  {t.fullyQualifiedName}")

# ================================================================== #
# 9. Async search (for async applications)
# ================================================================== #
# import asyncio
# results = asyncio.run(Search.search_async("customers", size=10))
