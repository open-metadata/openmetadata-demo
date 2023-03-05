# Java SDK Examples

In this directory you will find a set of different Java SDK methods and how to use them:

- Create:
  - a database service
  - a database associated to a service
  - a database schema associated to a database
  - a table associated to a database schema
  - a user
  - a classification
  - a tag associated to a classification
  - a glossary
  - a glossary tern associated to a glossary
  - a custom property
- Add:
  - a user as table owner
  - a tag to a table
  - a tag to a table column
  - a glossary term to a table column
  - a custom property to a table
- Print OpenMetadata version

**Note**: this demo is based on OpenMetadata version 0.13.2. If playing locally with the `openmetadata-ingestion`
package, make sure to install `openmetadata-ingestion==0.13.2`

## Requirements

### Docker Compose

Docker compose v2 installed on your machine. You can install it following the official [docs](https://docs.docker.com/compose/install/).

```bash
❯ docker compose version
Docker Compose version v2.2.3
```

### Python 3

OpenMetadata supports Python 3.7+. This demo has been built and tested using Python 3.9:

```bash
❯ python -V
Python 3.9.13
```

It is recommended to use python within a virtual environment for isolation:

```bash
python -m venv venv
source venv/bin/activate
```

You can now validate that you are using the right python executable with:

```bash
❯ which python
~/openmetadata-demo/java-sdk-examples/venv/bin/python
```

## What you'll find here

A Maven project with a class called `JavaSDKExamples.java` with all the examples divided per method.

## How to run?

1. First, build the maven project with `mvn clean install`
2. Secondly, install the OpenMetadata Python package:

```bash
❯ pip install "openmetadata-ingestion[docker]==0.13.2"
```

3. Then, start OpenMetadata with:

```bash
❯ metadata docker --start
```

4. Finally, use the following command to run the main class:

```bash
❯ mvn compile exec:java -Dexec.mainClass="org.openmetadata.JavaSDKExamples" -Dexec.cleanupDaemonThreads=fals
```

After following all the steps, you can check the entities created in [http://localhost:8585/](http://localhost:8585/).

## Contribute

Feel free to request more examples by opening an issue. If you want to contribute adding extra examples, we ❤️ all 
contributions, big and small!

Join our [Slack Community](https://slack.open-metadata.org/) to get in touch with us, want to chat or need help.