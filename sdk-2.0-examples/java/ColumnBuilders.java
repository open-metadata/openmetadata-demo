/**
 * SDK 2.0 – Column Builders
 * ==========================
 *
 * ColumnBuilder provides a fluent, type-safe way to create columns
 * with common data types, constraints and tags.
 *
 * Prerequisite: run BasicCrud.java first if you want to use
 * Tables.create() at the end.
 *
 * Source: openmetadata-sdk/.../fluent/builders/ColumnBuilder.java
 */
package org.openmetadata.sdk.examples;

import java.util.List;

import org.openmetadata.schema.type.Column;
import org.openmetadata.sdk.fluent.builders.ColumnBuilder;

public class ColumnBuilders {

    public static void main(String[] args) {

        // ---------------------------------------------------------- //
        // 1. Common data types — convenience static methods
        // ---------------------------------------------------------- //
        Column id = ColumnBuilder.bigint("id")
                .primaryKey()
                .notNull()
                .description("Auto-incrementing primary key")
                .build();

        Column name = ColumnBuilder.varchar("name", 255)
                .notNull()
                .description("Full name")
                .build();

        Column email = ColumnBuilder.varchar("email", 320)
                .unique()
                .notNull()
                .tag("PII.Sensitive")
                .description("Contact email")
                .build();

        Column price = ColumnBuilder.decimal("unit_price", 10, 2)
                .description("Unit price in USD")
                .build();

        Column createdAt = ColumnBuilder.timestamp("created_at")
                .description("Record creation timestamp")
                .build();

        Column metadata = ColumnBuilder.json("metadata")
                .description("Free-form JSON metadata")
                .build();

        Column tags = ColumnBuilder.array("tags", "VARCHAR")
                .description("User-assigned tags")
                .build();

        // ---------------------------------------------------------- //
        // 2. Build a full column list
        // ---------------------------------------------------------- //
        List<Column> columns = List.of(
                id, name, email, price, createdAt, metadata, tags
        );

        System.out.println("Built " + columns.size() + " columns:");
        for (Column col : columns) {
            System.out.printf("  %-15s %-10s%n",
                    col.getName(), col.getDataType());
        }

        // ---------------------------------------------------------- //
        // 3. Use with Tables.create() — references our demo schema
        // ---------------------------------------------------------- //
        // Table table = Tables.create()
        //         .name("products")
        //         .inSchema(BasicCrud.SCHEMA_FQN)
        //         .withColumns(columns)
        //         .execute();
    }
}
