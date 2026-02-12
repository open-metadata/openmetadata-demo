/**
 * SDK 2.0 – Entity Relationships
 * ================================
 *
 * Owners, followers, tags, domains, and entity references.
 *
 * Prerequisite: run BasicCrud.java first to create the demo entities.
 *
 * Source: openmetadata-sdk/.../EntityReferences.java
 *         openmetadata-sdk/.../fluent/wrappers/FluentTable.java
 */
package org.openmetadata.sdk.examples;

import java.util.List;

import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.schema.entity.teams.User;
import org.openmetadata.schema.type.EntityReference;
import org.openmetadata.sdk.EntityReferences;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.fluent.Tables;
import org.openmetadata.sdk.fluent.wrappers.FluentTable;

public class EntityRelationships {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Tables.setDefaultClient(client);

        // ---------------------------------------------------------- //
        // 1. EntityReferences — convert entities to references
        // ---------------------------------------------------------- //
        User user = client.users().getByName("admin");

        // from() extracts id, type, name, fullyQualifiedName
        EntityReference userRef = EntityReferences.from(user);

        // Direct creation (when you only have an ID)
        // EntityReference ref = EntityReferences.of(someUuid, "table");
        // EntityReference ref = EntityReferences.of(someUuid, "user", "john.doe");

        // ---------------------------------------------------------- //
        // 2. Set owners
        // ---------------------------------------------------------- //
        Table table = client.tables().getByName(BasicCrud.CUSTOMERS_FQN, "owners");
        table.setOwners(List.of(userRef));
        Table updated = client.tables().update(
                table.getId().toString(), table);
        System.out.println("Owners: " + updated.getOwners());

        // ---------------------------------------------------------- //
        // 3. Add / remove tags via fluent wrapper
        // ---------------------------------------------------------- //
        Table tagTable = client.tables().getByName(BasicCrud.CUSTOMERS_FQN, "tags,columns");
        FluentTable fluent = new FluentTable(tagTable, client);

        updated = fluent
                .addTag("PII.Sensitive")
                .addTag("Tier.Tier1")
                .save();
        System.out.println("Tags: " + updated.getTags());

        // ---------------------------------------------------------- //
        // 4. Column-level tags
        // ---------------------------------------------------------- //
        updated = fluent
                .addColumnTag("email", "PII.Sensitive")
                .updateColumnDescription("email", "Contact email (PII)")
                .save();

        // ---------------------------------------------------------- //
        // 5. Set domain (if one exists)
        // ---------------------------------------------------------- //
        // EntityReference domainRef = EntityReferences.from(
        //     client.domains().getByName("Marketing"));
        // table.setDomain(domainRef);
        // client.tables().update(table.getId().toString(), table);

        // ---------------------------------------------------------- //
        // 6. Set data products
        // ---------------------------------------------------------- //
        // table.setDataProducts(List.of(
        //     EntityReferences.from(dataProduct)
        // ));
        // client.tables().update(table.getId().toString(), table);
    }
}
