/**
 * SDK 2.0 – Field Selection
 * ==========================
 *
 * Control which fields are returned to minimize payload size.
 *
 * Prerequisite: run BasicCrud.java first to create the demo entities.
 *
 * Source: openmetadata-sdk/.../services/EntityServiceBase.java
 *         openmetadata-sdk/.../fluent/Tables.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.fluent.Tables;
import org.openmetadata.sdk.models.ListParams;
import org.openmetadata.sdk.models.ListResponse;

public class FieldSelection {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Tables.setDefaultClient(client);

        String tableFqn = BasicCrud.CUSTOMERS_FQN;

        // ---------------------------------------------------------- //
        // 1. Low-level service — pass fields as CSV string
        // ---------------------------------------------------------- //
        Table table = client.tables().getByName(tableFqn, "columns,tags,owners");

        System.out.println("Columns: " + table.getColumns().size());
        System.out.println("Tags:    " + table.getTags());
        System.out.println("Owners:  " + table.getOwners());

        // ---------------------------------------------------------- //
        // 2. Fluent API — named include methods
        // ---------------------------------------------------------- //
        var fluent = Tables.findByName(tableFqn)
                .includeOwners()    // adds "owners"
                .includeTags()      // adds "tags"
                .fetch();

        // includeAll() is a shortcut for owners + tags + followers +
        // domains + dataProducts
        var full = Tables.findByName(tableFqn)
                .includeAll()
                .fetch();

        // Custom fields
        var custom = Tables.findByName(tableFqn)
                .withFields("columns", "usageSummary", "profile")
                .fetch();

        // ---------------------------------------------------------- //
        // 3. Fields in list() calls
        // ---------------------------------------------------------- //
        ListParams params = new ListParams()
                .setLimit(50)
                .addFilter("database", BasicCrud.DATABASE_FQN)
                .setFields("id,name,description,owners,tags");

        ListResponse<Table> page = client.tables().list(params);
        for (Table t : page.getData()) {
            System.out.printf("  %-50s  owners=%s%n",
                    t.getFullyQualifiedName(), t.getOwners());
        }

        // ---------------------------------------------------------- //
        // Common field names
        // ---------------------------------------------------------- //
        // All entities : id, name, fullyQualifiedName, description,
        //                displayName, version, owners, tags, followers,
        //                domains, dataProducts, extension
        //
        // Tables only  : columns, tableConstraints, usageSummary,
        //                profile, joins, sampleData
        //
        // Users only   : teams, roles, personas
    }
}
