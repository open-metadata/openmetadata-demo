/**
 * SDK 2.0 – Fluent Entity Updates
 * =================================
 *
 * Use FluentTable (and other Fluent* wrappers) to chain mutations
 * and persist them in a single save() call.
 *
 * Prerequisite: run BasicCrud.java first to create the demo entities.
 *
 * Source: openmetadata-sdk/.../fluent/wrappers/FluentTable.java
 *         openmetadata-sdk/.../fluent/Tables.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.schema.type.Column;
import org.openmetadata.schema.type.ColumnDataType;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.fluent.Tables;
import org.openmetadata.sdk.fluent.wrappers.FluentTable;

public class FluentUpdates {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Tables.setDefaultClient(client);

        // ---------------------------------------------------------- //
        // 1. Fetch as FluentTable
        // ---------------------------------------------------------- //
        Table table = client.tables().getByName(
                BasicCrud.CUSTOMERS_FQN, "columns,tags,owners");
        FluentTable fluent = new FluentTable(table, client);

        // ---------------------------------------------------------- //
        // 2. Chain mutations and save
        // ---------------------------------------------------------- //
        Table updated = fluent
                .withDescription("Customer dimension — updated via SDK 2.0")
                .withDisplayName("Customers")
                .addTag("PII.Sensitive")
                .addTags("Tier.Tier1", "PersonalData.Personal")
                .updateColumnDescription("email", "Primary contact email")
                .addColumnTag("email", "PII.Sensitive")
                .save();

        System.out.println("Updated: " + updated.getFullyQualifiedName());

        // ---------------------------------------------------------- //
        // 3. Add a new column
        // ---------------------------------------------------------- //
        Column newCol = new Column()
                .withName("loyalty_tier")
                .withDataType(ColumnDataType.VARCHAR)
                .withDataLength(50)
                .withDescription("Customer loyalty tier");

        updated = fluent
                .addColumn(newCol)
                .save();

        // ---------------------------------------------------------- //
        // 4. Set owners via EntityReferences
        // ---------------------------------------------------------- //
        // EntityReferences.from() converts any entity into an
        // EntityReference suitable for owner/domain fields.

        // User user = client.users().getByName("admin");
        //
        // updated = fluent.get();
        // updated.setOwners(List.of(EntityReferences.from(user)));
        // client.tables().update(updated.getId().toString(), updated);

        // ---------------------------------------------------------- //
        // 5. Custom properties (extension)
        // ---------------------------------------------------------- //
        // updated = fluent
        //     .withExtension(Map.of("department", "Engineering"))
        //     .save();

        // ---------------------------------------------------------- //
        // 6. Conditional updates with applyIf
        // ---------------------------------------------------------- //
        // applyIf takes a Consumer<Table> for low-level mutations
        boolean addPii = true;
        updated = fluent
                .applyIf(addPii, t -> t.setDescription("PII-flagged table"))
                .save();

        // ---------------------------------------------------------- //
        // 7. Delete via fluent
        // ---------------------------------------------------------- //
        // Tables.find(tableId)
        //     .delete()
        //     .recursively()
        //     .permanently()
        //     .confirm();
    }
}
