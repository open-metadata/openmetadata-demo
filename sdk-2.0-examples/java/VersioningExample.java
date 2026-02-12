/**
 * SDK 2.0 – Entity Versioning
 * =============================
 *
 * Every mutation in OpenMetadata is tracked. Retrieve the full
 * version history or a specific snapshot.
 *
 * Prerequisite: run BasicCrud.java first (it creates the table and
 * updates its description, producing at least two versions).
 *
 * Source: openmetadata-sdk/.../services/EntityServiceBase.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.schema.type.EntityHistory;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;

public class VersioningExample {

    public static void main(String[] args) throws Exception {

        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);

        // ---------------------------------------------------------- //
        // 1. Get current version
        // ---------------------------------------------------------- //
        Table table = client.tables().getByName(BasicCrud.CUSTOMERS_FQN);
        System.out.printf("Current version: %.1f%n", table.getVersion());

        // ---------------------------------------------------------- //
        // 2. List all versions
        // ---------------------------------------------------------- //
        EntityHistory history = client.tables()
                .getVersionList(table.getId());

        System.out.println("Version history:");
        // history.getVersions() contains the list of snapshots

        // ---------------------------------------------------------- //
        // 3. Retrieve a specific version
        // ---------------------------------------------------------- //
        Table v01 = client.tables().getVersion(
                table.getId().toString(), 0.1);
        System.out.printf("v0.1 description: %s%n", v01.getDescription());

        // ---------------------------------------------------------- //
        // 4. Compare first and current version
        // ---------------------------------------------------------- //
        double currentVersion = table.getVersion();
        if (currentVersion > 0.1) {
            Table vCurrent = client.tables().getVersion(
                    table.getId().toString(), currentVersion);
            System.out.printf("Description changed between v0.1 and v%.1f%n",
                    currentVersion);
            System.out.println("  v0.1:     " + v01.getDescription());
            System.out.printf("  v%.1f: %s%n", currentVersion,
                    vCurrent.getDescription());
        }
    }
}
