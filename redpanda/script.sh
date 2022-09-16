#!/bin/bash
apt-get update
apt-get install -y python3 pip curl
curl -1sLf 'https://packages.vectorized.io/nzc4ZYQK3WRGd9sy/redpanda/cfg/setup/bash.deb.sh' | bash && apt install redpanda -y
rpk version
curl -s -X POST "http://redpanda:8081/subjects/create-user-request-0-value/versions" -H "Content-Type: application/vnd.schemaregistry.v1+json" -d '{"schema": "{\"type\":\"record\",\"name\":\"user\",\"fields\":[{\"name\":\"firstName\",\"type\":\"string\"},{\"name\":\"lastName\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"}]}" }'
curl -s -X POST "http://redpanda:8081/subjects/create-user-request-1-value/versions" -H "Content-Type: application/vnd.schemaregistry.v1+json" -d '{"schema": "{\"type\":\"record\",\"name\":\"user\",\"fields\":[{\"name\":\"firstName\",\"type\":\"string\"},{\"name\":\"lastName\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"}]}" }'
curl -s -X POST "http://redpanda:8081/subjects/create-user-request-2-value/versions" -H "Content-Type: application/vnd.schemaregistry.v1+json" -d '{"schema": "{\"type\":\"record\",\"name\":\"user\",\"fields\":[{\"name\":\"firstName\",\"type\":\"string\"},{\"name\":\"lastName\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"}]}" }'
curl -s -X POST "http://redpanda:8081/subjects/create-user-request-3-value/versions" -H "Content-Type: application/vnd.schemaregistry.v1+json" -d '{"schema": "{\"type\":\"record\",\"name\":\"user\",\"fields\":[{\"name\":\"firstName\",\"type\":\"string\"},{\"name\":\"lastName\",\"type\":\"string\"},{\"name\":\"email\",\"type\":\"string\"}]}" }'
echo ""
echo "Added schema:"
curl -s -X GET "http://redpanda:8081/schemas/ids/1"
pip install -r /test/requirements.txt
python3 /test/redpanda.py
echo "End"