/**
 * SDK 2.0 – Pagination
 * =====================
 *
 * Cursor-based forward/backward pagination using ListParams
 * and ListResponse.
 *
 * Prerequisite: run BasicCrud.java first to create the demo entities.
 *
 * Source: openmetadata-sdk/.../models/ListParams.java
 *         openmetadata-sdk/.../models/ListResponse.java
 *         openmetadata-sdk/.../services/EntityServiceBase.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.schema.entity.teams.User;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.fluent.Tables;
import org.openmetadata.sdk.models.ListParams;
import org.openmetadata.sdk.models.ListResponse;

public class Pagination {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Tables.setDefaultClient(client);

        // ---------------------------------------------------------- //
        // 1. Manual cursor pagination (forward)
        // ---------------------------------------------------------- //
        System.out.println("=== Manual pagination ===");
        ListParams params = new ListParams()
                .setLimit(10)
                .setFields("id,name,description");

        int pageNum = 0;
        while (true) {
            ListResponse<Table> page = client.tables().list(params);
            pageNum++;
            System.out.printf("Page %d: %d tables%n",
                    pageNum, page.getData().size());

            for (Table t : page.getData()) {
                System.out.println("  - " + t.getFullyQualifiedName());
            }

            if (!page.hasNextPage()) break;
            params.setAfter(page.getPaging().getAfter());
        }
        System.out.println("Total pages: " + pageNum);

        // ---------------------------------------------------------- //
        // 2. Backward pagination
        // ---------------------------------------------------------- //
        // ListParams backParams = new ListParams()
        //         .setLimit(10)
        //         .setBefore(someBeforeCursor);
        // ListResponse<Table> prevPage = client.tables().list(backParams);

        // ---------------------------------------------------------- //
        // 3. Fluent list with forEach (auto-handles pages)
        // ---------------------------------------------------------- //
        System.out.println("\n=== Fluent forEach ===");
        Tables.list()
                .limit(50)
                .forEach(fluentTable -> {
                    System.out.println("  " + fluentTable.get().getName());
                });

        // ---------------------------------------------------------- //
        // 4. Filtered pagination — only our demo database
        // ---------------------------------------------------------- //
        System.out.println("\n=== Filtered ===");
        ListParams filtered = new ListParams()
                .setLimit(50)
                .addFilter("database", BasicCrud.DATABASE_FQN)
                .setFields("id,name");

        ListResponse<Table> filteredPage = client.tables().list(filtered);
        System.out.printf("Tables in sdk_demo_db: %d (total: %d)%n",
                filteredPage.getData().size(),
                filteredPage.getTotal());
        for (Table t : filteredPage.getData()) {
            System.out.println("  - " + t.getFullyQualifiedName());
        }

        // ---------------------------------------------------------- //
        // 5. Pagination on other entities (same API)
        // ---------------------------------------------------------- //
        System.out.println("\n=== Users ===");
        ListParams userParams = new ListParams().setLimit(5);
        ListResponse<User> users = client.users().list(userParams);
        for (User u : users.getData()) {
            System.out.printf("  %s (%s)%n", u.getName(), u.getEmail());
        }
    }
}
