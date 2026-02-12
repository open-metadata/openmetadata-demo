/**
 * SDK 2.0 – Search API
 * =====================
 *
 * Full-text search, suggestions, aggregations and the builder.
 *
 * Prerequisite: run BasicCrud.java first to create the demo entities.
 *
 * Source: openmetadata-sdk/.../api/SearchAPI.java
 *         openmetadata-sdk/.../api/Search.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.api.Search;

public class SearchExample {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Search.setDefaultClient(client);

        // ---------------------------------------------------------- //
        // 1. Simple search — find our demo tables
        // ---------------------------------------------------------- //
        var results = Search.query("customers").execute();
        System.out.println("Simple search: " + results.getRaw());

        // ---------------------------------------------------------- //
        // 2. Scoped search — specific index, sorting, pagination
        // ---------------------------------------------------------- //
        results = Search.query("customers")
                .in("table_search_index")
                .from(0)
                .limit(20)
                .sortBy("name", Search.SortOrder.ASC)
                .execute();

        // ---------------------------------------------------------- //
        // 3. Suggestions / autocomplete
        // ---------------------------------------------------------- //
        var suggestions = Search.suggest("cust")
                .in("table_search_index")
                .limit(10)
                .execute();
        System.out.println("Suggestions: " + suggestions.getRaw());

        // ---------------------------------------------------------- //
        // 4. Aggregations
        // ---------------------------------------------------------- //
        var aggs = Search.aggregate()
                .query("*")
                .in("table_search_index")
                .aggregateBy("service.name")
                .execute();
        System.out.println("Aggregations: " + aggs.getRaw());

        // ---------------------------------------------------------- //
        // 5. Faceted search
        // ---------------------------------------------------------- //
        var faceted = Search.faceted()
                .query("customers")
                .facet("service.name", 10)
                .filter("service.name", BasicCrud.SERVICE_FQN)
                .execute();
        System.out.println("Faceted: " + faceted.getRaw());

        // ---------------------------------------------------------- //
        // 6. Reindexing
        // ---------------------------------------------------------- //
        // String reindexResult = Search.reindex().entity("table").execute();
        // String reindexAll    = Search.reindex().all();
    }
}
