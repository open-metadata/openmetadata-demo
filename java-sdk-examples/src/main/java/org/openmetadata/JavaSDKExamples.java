package org.openmetadata;

import feign.FeignException;
import org.jetbrains.annotations.NotNull;
import org.openmetadata.client.api.ClassificationApi;
import org.openmetadata.client.api.DatabaseSchemasApi;
import org.openmetadata.client.api.DatabaseServicesApi;
import org.openmetadata.client.api.DatabasesApi;
import org.openmetadata.client.api.GlossariesApi;
import org.openmetadata.client.api.GlossaryTermApi;
import org.openmetadata.client.api.MetadataApi;
import org.openmetadata.client.api.TablesApi;
import org.openmetadata.client.api.UsersApi;
import org.openmetadata.client.gateway.OpenMetadata;
import org.openmetadata.client.model.Classification;
import org.openmetadata.client.model.Column;
import org.openmetadata.client.model.CreateClassification;
import org.openmetadata.client.model.CreateDatabase;
import org.openmetadata.client.model.CreateDatabaseSchema;
import org.openmetadata.client.model.CreateDatabaseService;
import org.openmetadata.client.model.CreateGlossary;
import org.openmetadata.client.model.CreateGlossaryTerm;
import org.openmetadata.client.model.CreateTable;
import org.openmetadata.client.model.CreateTag;
import org.openmetadata.client.model.CreateUser;
import org.openmetadata.client.model.CustomProperty;
import org.openmetadata.client.model.Database;
import org.openmetadata.client.model.DatabaseConnection;
import org.openmetadata.client.model.DatabaseSchema;
import org.openmetadata.client.model.DatabaseService;
import org.openmetadata.client.model.EntityReference;
import org.openmetadata.client.model.Glossary;
import org.openmetadata.client.model.GlossaryTerm;
import org.openmetadata.client.model.Table;
import org.openmetadata.client.model.Tag;
import org.openmetadata.client.model.Type;
import org.openmetadata.client.model.User;
import org.openmetadata.schema.security.client.OpenMetadataJWTClientConfig;
import org.openmetadata.schema.services.connections.database.MysqlConnection;
import org.openmetadata.schema.services.connections.metadata.OpenMetadataConnection;
import org.openmetadata.schema.type.TagLabel;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Different examples of common actions that can be achieved by using the OpenMetadata Java SDK
 */
public class JavaSDKExamples {

  public static void main(String[] args) {
    OpenMetadataConnection openMetadataConnection;
    // OpenMetadata JWT Client Config
    OpenMetadataJWTClientConfig openMetadataJWTClientConfig;
    openMetadataJWTClientConfig = new OpenMetadataJWTClientConfig();
    openMetadataJWTClientConfig.setJwtToken(
        "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhZG1pbiIsImlzQm90IjpmYWxzZSwiaXNzIjoib3Blbi1tZXRhZGF0YS5vcmciLCJpYXQiOjE2NjM5Mzg0NjIsImVtYWlsIjoiYWRtaW5Ab3Blbm1ldGFkYXRhLm9yZyJ9.tS8um_5DKu7HgzGBzS1VTA5uUjKWOCU0B_j08WXBiEC0mr0zNREkqVfwFDD-d24HlNEbrqioLsBuFRiwIWKc1m_ZlVQbG7P36RUxhuv2vbSp80FKyNM-Tj93FDzq91jsyNmsQhyNv_fNr3TXfzzSPjHt8Go0FMMP66weoKMgW2PbXlhVKwEuXUHyakLLzewm9UMeQaEiRzhiTMU3UkLXcKbYEJJvfNFcLwSl9W8JCO_l0Yj3ud-qt_nQYEZwqW6u5nfdQllN133iikV4fM5QZsMCnm8Rq1mvLR0y9bmJiD7fwM1tmJ791TUWqmKaTnP49U493VanKpUAfzIiOiIbhg");
    // OpenMetadata Connection Config
    openMetadataConnection = new OpenMetadataConnection();
    openMetadataConnection.setHostPort("http://localhost:8585/api");
    openMetadataConnection.setAuthProvider(OpenMetadataConnection.AuthProvider.OPENMETADATA);
    openMetadataConnection.setSecurityConfig(openMetadataJWTClientConfig);
    // Create OpenMetadata Gateway
    OpenMetadata openMetadataGateway = new OpenMetadata(openMetadataConnection);
    // Print version
    printClientVersion(openMetadataGateway);
    // Create a Mysql database service
    DatabaseService databaseService = createMysqlDatabaseService(openMetadataGateway);
    // Create Database on a given database service
    Database database = createDatabase(openMetadataGateway, databaseService, "mydb", "My db description.");
    // Create Schema
    DatabaseSchema databaseSchema = createDatabaseSchema(openMetadataGateway, database, "myschema", "The schema description.");
    // Create Table with columns
    Column column1 = createColumn("id", "User id", Column.DataTypeEnum.NUMBER, Column.ConstraintEnum.PRIMARY_KEY);
    Column column2 = createColumn("name", "User name", Column.DataTypeEnum.NUMBER, Column.ConstraintEnum.NOT_NULL);
    Table table = createTable(openMetadataGateway, databaseSchema, List.of(column1, column2), "users", "Users table.");
    // Create User
    User user = createUser(openMetadataGateway, "user", "user@open-metadata.org");
    // Add user as table owner
    addUserAsOwnerToTable(openMetadataGateway, table, user);
    // Create Classification
    Classification classification = createClassification(openMetadataGateway, "My custom classification", "My classification description.");
    // Create Tag
    Tag tag = createTag(openMetadataGateway, classification, "Tag", "My tag description.");
    // Add Tag to Table
    addIfNotExistsTagToTable(openMetadataGateway, table, tag);
    // Add Tag to Column
    addIfNotExistsTagLabelToColumn(openMetadataGateway, table, column2, tag.getFullyQualifiedName(), TagLabel.TagSource.TAG);
    // Create custom property
    CustomProperty customProperty = createCustomTableStringProperty(openMetadataGateway, "random_property", "Random description");
    // Add custom property to Table
    addCustomPropertyToTable(openMetadataGateway, table, customProperty, "random-value");
    // Create a Glossary
    Glossary glossary = createGlossary(openMetadataGateway, "my-glossary", "My glossary description.");
    // Create a Glossary term
    GlossaryTerm glossaryTerm = createGlossaryTerm(openMetadataGateway, glossary, "Glossary term", "My glossary description");
    // Create a Glossary term
    addIfNotExistsTagLabelToColumn(openMetadataGateway, table, column2, glossaryTerm.getFullyQualifiedName(), TagLabel.TagSource.GLOSSARY);
    System.out.println("Done!");
  }

  private static void printClientVersion(OpenMetadata openMetadataGateway) {
    System.out.println("OpenMetadata version: " + String.join(".", openMetadataGateway.getClientVersion()));
  }

  private static DatabaseService createMysqlDatabaseService(OpenMetadata openMetadataGateway) {
    // Create service request
    CreateDatabaseService createDatabaseService = new CreateDatabaseService();
    // Connection type definition
    DatabaseConnection databaseConnection = new DatabaseConnection();
    // Create MysqlConnection
    MysqlConnection databaseConnectionConfig = new MysqlConnection();
    databaseConnectionConfig.setScheme(MysqlConnection.MySQLScheme.MYSQL_PYMYSQL);
    databaseConnectionConfig.setHostPort("localhost:3306");
    databaseConnectionConfig.setUsername("openmetadata_user");
    databaseConnectionConfig.setPassword("openmetadata_password");
    databaseConnectionConfig.setDatabaseSchema("openmetadata_db");
    databaseConnection.setConfig(databaseConnectionConfig);
    // Update create service request fields
    createDatabaseService.setConnection(databaseConnection);
    createDatabaseService.setName("mysql-test");
    createDatabaseService.setDescription("Mysql test connection.");
    createDatabaseService.setServiceType(CreateDatabaseService.ServiceTypeEnum.MYSQL);
    // Call API
    DatabaseServicesApi databaseServicesApi = openMetadataGateway.buildClient(DatabaseServicesApi.class);
    return databaseServicesApi.createOrUpdateDatabaseService(createDatabaseService);
  }

  private static Database createDatabase(OpenMetadata openMetadataGateway, DatabaseService service, String dbName, String desc) {
    CreateDatabase createdatabase = new CreateDatabase();
    createdatabase.name(dbName);
    createdatabase.description(desc);
    createdatabase.displayName(dbName);
    createdatabase.setService(buildEntityReference("databaseService", service.getId(), service.getName()));
    // Call API
    DatabasesApi databasesApi = openMetadataGateway.buildClient(DatabasesApi.class);
    return databasesApi.createOrUpdateDatabase(createdatabase);
  }

  private static DatabaseSchema createDatabaseSchema(OpenMetadata openMetadataGateway, Database database, String name, String description) {
    CreateDatabaseSchema createschema = new CreateDatabaseSchema();
    createschema.setName(name);
    createschema.setDescription(description);
    createschema.setDisplayName(name);
    createschema.setDatabase(buildEntityReference("database", database.getId(), database.getName()));
    DatabaseSchemasApi databaseSchemasApi = openMetadataGateway.buildClient(DatabaseSchemasApi.class);
    return databaseSchemasApi.createOrUpdateDBSchema(createschema);
  }

  private static Table createTable(OpenMetadata openMetadataGateway, DatabaseSchema databaseSchema, List<Column> columns, String name, String description) {
    CreateTable createTable = new CreateTable();
    createTable.setName(name);
    createTable.setDescription(description);
    createTable.columns(columns);
    createTable.setTableType(CreateTable.TableTypeEnum.REGULAR);
    createTable.setDatabaseSchema(buildEntityReference("databaseSchema", databaseSchema.getId(), databaseSchema.getName()));
    TablesApi tablesApi = openMetadataGateway.buildClient(TablesApi.class);
    Table table = tablesApi.createOrUpdateTable(createTable);
    return tablesApi.getTableByID(table.getId(), "*", "all");
  }

  private static User createUser(OpenMetadata openMetadataGateway, String name, String email) {
    UsersApi usersApi = openMetadataGateway.buildClient(UsersApi.class);
    User user = usersApi.getUserByFQN(name, new HashMap<>());
    if (user == null) {
      CreateUser createUser = new CreateUser();
      createUser.setName(name);
      createUser.setEmail(email);
      createUser.setDisplayName(name);
      createUser.setPassword("asdf1234");
      createUser.setConfirmPassword("asdf1234");
      return usersApi.createUser(createUser);
    }
    return user;
  }

  private static void addUserAsOwnerToTable(OpenMetadata openMetadataGateway, Table table, User user) {
    TablesApi tablesApi = openMetadataGateway.buildClient(TablesApi.class);
    tablesApi.patchTable(table.getId(), List.of(buildPatch("add", "/owner", buildEntityReference("user", user.getId(), user.getName()))));
  }

  private static Classification createClassification(OpenMetadata openMetadataGateway, String name, String description) {
    ClassificationApi classificationApi = openMetadataGateway.buildClient(ClassificationApi.class);
    try {
      Classification classification = classificationApi.getClassificationByName(name, new HashMap<>());
      return classification;
    } catch (FeignException.NotFound ignore) { }
    CreateClassification createClassification = new CreateClassification();
    createClassification.setName(name);
    createClassification.setDescription(description);
    createClassification.setDisplayName(name);
    return classificationApi.createClassification(createClassification);
  }

  private static Tag createTag(OpenMetadata openMetadataGateway, Classification classification, String name, String description) {
    CreateTag createTag = new CreateTag();
    createTag.setName(name);
    createTag.setDescription(description);
    createTag.setDisplayName(name);
    createTag.setClassification(classification.getName());
    ClassificationApi  classificationApi = openMetadataGateway.buildClient(ClassificationApi.class);
    return classificationApi.createOrUpdateTag(createTag);
  }

  private static void addIfNotExistsTagToTable(OpenMetadata openMetadataGateway, Table table, Tag tag) {
    TablesApi tablesApi = openMetadataGateway.buildClient(TablesApi.class);
    int indexOfTag = table.getTags().stream().map(org.openmetadata.client.model.TagLabel::getTagFQN).collect(Collectors.toList()).indexOf(tag.getFullyQualifiedName());
    if (indexOfTag >= 0) {
      tablesApi.patchTable(table.getId(), List.of(buildPatch("replace", "/tags/" + indexOfTag + "/tagFQN", tag.getFullyQualifiedName())));
    } else {
      tablesApi.patchTable(table.getId(), List.of(buildPatch("add", "/tags/" + table.getTags().size() + "/tagFQN", tag.getFullyQualifiedName())));
    }
  }

  private static CustomProperty createCustomTableStringProperty(OpenMetadata openMetadataGateway, String name, String description) {
    MetadataApi metadataApi = openMetadataGateway.buildClient(MetadataApi.class);
    Type tableType = metadataApi.getTypeByName("table", new HashMap<>());
    Type stringFieldType = metadataApi.listTypes("field", null, null, null).getData().stream().filter(type -> type.getName().equals("string")).findFirst().orElseThrow(() ->new RuntimeException("String field not found"));
    CustomProperty customProperty = new CustomProperty();
    customProperty.setName(name);
    customProperty.setDescription(description);
    customProperty.setPropertyType(buildEntityReference("type", stringFieldType.getId(), stringFieldType.getName()));
    metadataApi.addProperty(tableType.getId().toString(), customProperty);
    return customProperty;
  }

  private static void addCustomPropertyToTable(OpenMetadata openMetadataGateway, Table table, CustomProperty customProperty, String value) {
    TablesApi tablesApi = openMetadataGateway.buildClient(TablesApi.class);
    tablesApi.patchTable(table.getId(), List.of(buildPatch("add", "/extension", new HashMap<>() {{
      put(customProperty.getName(), value);
    }})));
  }

  private static Glossary createGlossary(OpenMetadata openMetadataGateway, String name, String description) {
    CreateGlossary createGlossary = new CreateGlossary();
    createGlossary.setName(name);
    createGlossary.setDescription(description);
    createGlossary.setDescription(name);
    GlossariesApi glossariesApi = openMetadataGateway.buildClient(GlossariesApi.class);
    return glossariesApi.createOrUpdateGlossary(createGlossary);
  }

  private static GlossaryTerm createGlossaryTerm(OpenMetadata openMetadataGateway, Glossary glossary, String name, String description) {
    CreateGlossaryTerm createGlossaryTerm = new CreateGlossaryTerm();
    createGlossaryTerm.setName(name);
    createGlossaryTerm.setDescription(description);
    createGlossaryTerm.setDisplayName(name);
    createGlossaryTerm.setGlossary(buildEntityReference("glossary", glossary.getId(), glossary.getName()));
    GlossaryTermApi glossaryTermApi = openMetadataGateway.buildClient(GlossaryTermApi.class);
    return glossaryTermApi.createOrUpdateGlossaryTerm(createGlossaryTerm);
  }

  private static void addIfNotExistsTagLabelToColumn(OpenMetadata openMetadataGateway, Table table, Column column, String tagLabelFQN, TagLabel.TagSource source) {
    TablesApi tablesApi = openMetadataGateway.buildClient(TablesApi.class);
    int indexOfColumn = table.getColumns().stream().map(Column::getName).collect(Collectors.toList()).indexOf(column.getName());
    int indexOfTag = table.getColumns().get(indexOfColumn).getTags().stream().map(org.openmetadata.client.model.TagLabel::getTagFQN).collect(Collectors.toList()).indexOf(tagLabelFQN);
    if (indexOfTag >= 0) {
      tablesApi.patchTable(table.getId(), List.of(buildPatch("replace", "/columns/" + indexOfColumn + "/tags/" + indexOfTag, buildTagLabel(tagLabelFQN, source))));
    } else {
      tablesApi.patchTable(table.getId(), List.of(buildPatch("add", "/columns/" + indexOfColumn + "/tags/" + table.getTags().size(), buildTagLabel(tagLabelFQN, source))));
    }
  }

  @NotNull
  private static Column createColumn(
      String colName,
      String colDesc,
      Column.DataTypeEnum dataType,
      Column.ConstraintEnum constraint) {
    Column column = new Column();
    column.setName(colName);
    column.setDescription(colDesc);
    column.setDisplayName(colName);
    column.setDataType(dataType);
    if (constraint != null) {
      column.constraint(constraint);
    }
    return column;
  }

  private static Object buildPatch(String op, String path, Object value) {
    return new HashMap<>() {{
      put("op", op);
      put("path", path);
      put("value", value);
    }};
  }

  private static TagLabel buildTagLabel(String tagFQN, TagLabel.TagSource source) {
    TagLabel tagLabel = new TagLabel();
    tagLabel.setLabelType(TagLabel.LabelType.MANUAL);
    tagLabel.setSource(source);
    tagLabel.setState(TagLabel.State.CONFIRMED);
    tagLabel.setTagFQN(tagFQN);
    return tagLabel;
  }

  private static EntityReference buildEntityReference(String type, UUID id, String name) {
    EntityReference entityReference = new EntityReference();
    entityReference.setId(id);
    entityReference.setName(name);
    entityReference.setType(type);
    return entityReference;
  }
}
