/**
 * SDK 2.0 – Lineage API
 * ======================
 *
 * Query, add and delete lineage edges between entities.
 *
 * Prerequisite: run BasicCrud.java first to create the demo tables
 * (customers and orders).
 *
 * Source: openmetadata-sdk/.../api/LineageAPI.java
 *         openmetadata-sdk/.../api/Lineage.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.api.Lineage;
import org.openmetadata.sdk.fluent.Tables;

public class LineageExample {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Tables.setDefaultClient(client);
        Lineage.setDefaultClient(client);

        // Retrieve the two demo tables
        Table customers = client.tables().getByName(BasicCrud.CUSTOMERS_FQN);
        Table orders    = client.tables().getByName(BasicCrud.ORDERS_FQN);

        String customersId = customers.getId().toString();
        String ordersId    = orders.getId().toString();

        // ---------------------------------------------------------- //
        // 1. Add a lineage edge (orders → customers)
        // ---------------------------------------------------------- //
        Lineage.connect()
                .from("table", ordersId)
                .to("table", customersId)
                .withDescription("ETL: orders → customers join")
                .execute();
        System.out.println("Created lineage edge");

        // ---------------------------------------------------------- //
        // 2. Get lineage by entity type + ID
        // ---------------------------------------------------------- //
        Lineage.LineageGraph graph = Lineage.of("table", customersId)
                .upstream(3)
                .downstream(2)
                .includeDeleted(false)
                .fetch();
        System.out.println("Lineage: " + graph.getRaw());

        // ---------------------------------------------------------- //
        // 3. Delete a lineage edge
        // ---------------------------------------------------------- //
        Lineage.disconnect()
                .from("table", ordersId)
                .to("table", customersId)
                .confirm();
        System.out.println("Edge deleted");
    }
}
