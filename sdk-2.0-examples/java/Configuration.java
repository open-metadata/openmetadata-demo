/**
 * SDK 2.0 – Configuration
 * ========================
 *
 * Build an OpenMetadataConfig, create a client, and optionally
 * register it globally for the fluent static API.
 *
 * Source: openmetadata-sdk/.../config/OpenMetadataConfig.java
 *         openmetadata-sdk/.../client/OpenMetadataClient.java
 *         openmetadata-sdk/.../client/OpenMetadata.java
 */
package org.openmetadata.sdk.examples;

import org.openmetadata.sdk.client.OpenMetadata;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.fluent.Tables;
import org.openmetadata.sdk.fluent.Databases;
import org.openmetadata.sdk.fluent.Users;
import org.openmetadata.sdk.fluent.Teams;

public class Configuration {

    public static void main(String[] args) {

        // ---------------------------------------------------------- //
        // 1. Build configuration with the builder pattern
        // ---------------------------------------------------------- //
        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<your-jwt-token>")
                .connectTimeout(30_000)   // ms
                .readTimeout(60_000)      // ms
                .writeTimeout(60_000)     // ms
                // .header("X-Custom", "value")  // optional extra headers
                // .debug(true)                   // verbose HTTP logging
                .build();

        // ---------------------------------------------------------- //
        // 2. Create the client
        // ---------------------------------------------------------- //
        OpenMetadataClient client = new OpenMetadataClient(config);

        // ---------------------------------------------------------- //
        // 3. Register globally (singleton) for fluent static APIs
        // ---------------------------------------------------------- //
        OpenMetadata.initialize(config);

        // After this, you can use the static facades anywhere:
        // Tables.find(...), Databases.create(...), etc.

        // Or register per-facade explicitly:
        Tables.setDefaultClient(client);
        Databases.setDefaultClient(client);
        Users.setDefaultClient(client);
        Teams.setDefaultClient(client);

        // ---------------------------------------------------------- //
        // 4. Retrieve the global client later
        // ---------------------------------------------------------- //
        OpenMetadataClient sameClient = OpenMetadata.client();
        System.out.println("Client ready: " + (sameClient != null));
    }
}
