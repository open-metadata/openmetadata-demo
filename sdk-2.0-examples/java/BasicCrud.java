/**
 * SDK 2.0 – Basic CRUD Operations
 * =================================
 *
 * Create the full entity hierarchy (Service → Database → Schema → Table),
 * then retrieve, update and delete using the fluent API and service layer.
 *
 * Source: openmetadata-sdk/.../fluent/Tables.java
 *         openmetadata-sdk/.../fluent/DatabaseServices.java
 *         openmetadata-sdk/.../fluent/builders/DatabaseServiceBuilder.java
 *         openmetadata-sdk/.../services/EntityServiceBase.java
 */
package org.openmetadata.sdk.examples;

import java.util.ArrayList;
import java.util.List;

import org.openmetadata.schema.api.data.CreateDatabase;
import org.openmetadata.schema.api.data.CreateDatabaseSchema;
import org.openmetadata.schema.api.data.CreateTable;
import org.openmetadata.schema.api.services.CreateDatabaseService;
import org.openmetadata.schema.entity.data.Database;
import org.openmetadata.schema.entity.data.DatabaseSchema;
import org.openmetadata.schema.entity.data.Table;
import org.openmetadata.schema.entity.services.DatabaseService;
import org.openmetadata.schema.type.Column;
import org.openmetadata.schema.type.ColumnDataType;
import org.openmetadata.sdk.client.OpenMetadataClient;
import org.openmetadata.sdk.config.OpenMetadataConfig;
import org.openmetadata.sdk.fluent.Tables;
import org.openmetadata.sdk.fluent.Databases;
import org.openmetadata.sdk.fluent.DatabaseServices;
import org.openmetadata.sdk.fluent.builders.DatabaseServiceBuilder;
public class BasicCrud {

    // FQN constants used by all other examples
    static final String SERVICE_FQN  = "sdk_demo_mysql";
    static final String DATABASE_FQN = "sdk_demo_mysql.sdk_demo_db";
    static final String SCHEMA_FQN   = "sdk_demo_mysql.sdk_demo_db.demo_schema";
    static final String CUSTOMERS_FQN = SCHEMA_FQN + ".customers";
    static final String ORDERS_FQN    = SCHEMA_FQN + ".orders";

    public static void main(String[] args) throws Exception {

        // -- Setup (see Configuration.java) --
        OpenMetadataConfig config = OpenMetadataConfig.builder()
                .serverUrl("http://localhost:8585/api")
                .accessToken("<token>")
                .build();
        OpenMetadataClient client = new OpenMetadataClient(config);
        Tables.setDefaultClient(client);
        Databases.setDefaultClient(client);
        DatabaseServices.setDefaultClient(client);

        // ---------------------------------------------------------- //
        // 1. CREATE — full hierarchy: Service → Database → Schema → Table
        // ---------------------------------------------------------- //

        // Database service (top-level container)
        CreateDatabaseService svcReq = new DatabaseServiceBuilder(client)
                .name("sdk_demo_mysql")
                .connection(
                    DatabaseServices.mysqlConnection()
                        .hostPort("localhost:3306")
                        .username("demo_user")
                        .build())
                .description("MySQL service created via SDK 2.0")
                .build();

        DatabaseService service = client.databaseServices().create(svcReq);
        String serviceFqn = service.getFullyQualifiedName() != null
                ? service.getFullyQualifiedName() : service.getName();
        System.out.println("Created service: " + serviceFqn);

        // Database
        Database db = Databases.create()
                .name("sdk_demo_db")
                .in(serviceFqn)
                .withDescription("Database created via SDK 2.0")
                .execute();
        String databaseFqn = db.getFullyQualifiedName() != null
                ? db.getFullyQualifiedName() : db.getName();
        System.out.println("Created database: " + databaseFqn);

        // Schema
        CreateDatabaseSchema schemaReq = new CreateDatabaseSchema()
                .withName("demo_schema")
                .withDatabase(databaseFqn)
                .withDescription("Schema created via SDK 2.0");
        DatabaseSchema schema = client.databaseSchemas().create(schemaReq);
        String schemaFqn = schema.getFullyQualifiedName() != null
                ? schema.getFullyQualifiedName() : schema.getName();
        System.out.println("Created schema: " + schemaFqn);

        // Customers table
        List<Column> customerCols = new ArrayList<>();
        customerCols.add(new Column()
                .withName("id").withDataType(ColumnDataType.BIGINT)
                .withDescription("Primary key"));
        customerCols.add(new Column()
                .withName("name").withDataType(ColumnDataType.VARCHAR)
                .withDataLength(255));
        customerCols.add(new Column()
                .withName("email").withDataType(ColumnDataType.VARCHAR)
                .withDataLength(320).withDescription("Contact email"));
        customerCols.add(new Column()
                .withName("created_at").withDataType(ColumnDataType.TIMESTAMP));

        Table customers = Tables.create()
                .name("customers")
                .inSchema(schemaFqn)
                .withDescription("Customer master data")
                .withColumns(customerCols)
                .execute();
        System.out.println("Created table: " + customers.getFullyQualifiedName());

        // Orders table (used by LineageExample)
        List<Column> orderCols = new ArrayList<>();
        orderCols.add(new Column()
                .withName("id").withDataType(ColumnDataType.BIGINT)
                .withDescription("Primary key"));
        orderCols.add(new Column()
                .withName("customer_id").withDataType(ColumnDataType.BIGINT)
                .withDescription("FK to customers.id"));
        orderCols.add(new Column()
                .withName("amount").withDataType(ColumnDataType.DECIMAL));
        orderCols.add(new Column()
                .withName("order_date").withDataType(ColumnDataType.DATE));

        Table orders = Tables.create()
                .name("orders")
                .inSchema(schemaFqn)
                .withDescription("Order transactions")
                .withColumns(orderCols)
                .execute();
        System.out.println("Created table: " + orders.getFullyQualifiedName());

        // ---------------------------------------------------------- //
        // 2. RETRIEVE — by ID
        // ---------------------------------------------------------- //
        var fetched = Tables.find(customers.getId().toString())
                .includeOwners()
                .includeTags()
                .fetch();
        System.out.println("Fetched: " + fetched.get().getFullyQualifiedName());

        // ---------------------------------------------------------- //
        // 3. RETRIEVE — by Fully Qualified Name
        // ---------------------------------------------------------- //
        var byName = Tables.findByName(CUSTOMERS_FQN)
                .includeAll()
                .fetch();
        System.out.println("By name: " + byName.get().getFullyQualifiedName());

        // ---------------------------------------------------------- //
        // 4. UPDATE — fluent chaining on FluentTable wrapper
        // ---------------------------------------------------------- //
        fetched.withDescription("Customer master data (updated via SDK 2.0)")
                .withDisplayName("Customers")
                .save();
        System.out.println("Updated description: " + fetched.get().getDescription());

        // ---------------------------------------------------------- //
        // 5. DELETE (run after all other examples)
        // ---------------------------------------------------------- //
        // The remaining examples reference the entities created above.
        // Uncomment this cleanup section only after the full demo.

        // // Soft delete (recoverable)
        // client.tables().delete(customers.getId().toString());
        // System.out.println("Soft-deleted");
        //
        // // Restore
        // Table restored = client.tables().restore(customers.getId().toString());
        // System.out.println("Restored: " + restored.getFullyQualifiedName());
        //
        // // Hard delete (permanent)
        // client.tables().delete(customers.getId().toString(),
        //         Map.of("hardDelete", "true", "recursive", "false"));
        // System.out.println("Hard-deleted");
        //
        // // Recursive delete — removes the service and everything under it
        // client.databaseServices().delete(service.getId().toString(),
        //         Map.of("hardDelete", "true", "recursive", "true"));
        // System.out.println("Full hierarchy deleted");
    }
}
