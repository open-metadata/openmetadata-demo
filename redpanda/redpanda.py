"""
Simple toy script to prepare Redpanda data
"""
import json
import sys

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic

bootstrap_servers = "redpanda:29092"

# Define topic name from where the message will receive
topicName = "create-user-request-{num}"

# Create topic
admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="test")

topic_list = [
    NewTopic(name=topicName.format(num="0"), num_partitions=1, replication_factor=1),
    NewTopic(name=topicName.format(num="1"), num_partitions=1, replication_factor=1),
    NewTopic(name=topicName.format(num="2"), num_partitions=1, replication_factor=1),
    NewTopic(name=topicName.format(num="3"), num_partitions=1, replication_factor=1)
]

admin_client.create_topics(new_topics=topic_list, validate_only=False)

# Produce data
producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    client_id="test",
)

for num in range(100):
    print("Sending..")
    producer.send(
        topicName.format(num=num % 4),
        {
            "firstName": f"firstName{num}",
            "lastName": f"lastName{num}",
            "email": f"fakeEmail{num}@test.com",
        },
    )

# Terminate the script
sys.exit()
