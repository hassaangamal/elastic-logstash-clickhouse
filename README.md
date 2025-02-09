# Elasticsearch → Logstash → ClickHouse Pipeline

This project sets up a data pipeline to transfer data from **Elasticsearch** to **ClickHouse** using **Logstash**. The pipeline is containerized using Docker for easy setup and deployment.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Setup Instructions](#setup-instructions)
   - [Step 1: Clone the Repository](#step-1-clone-the-repository)
   - [Step 2: Start the Services](#step-2-start-the-services)
   - [Step 3: Verify the Pipeline](#step-3-verify-the-pipeline)
4. [Connecting to ClickHouse with DBeaver](#connecting-to-clickhouse-with-dbeaver)
5. [Troubleshooting](#troubleshooting)
6. [License](#license)

---

## Prerequisites
Before starting, ensure you have the following installed:
- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)
- **DBeaver** (optional, for connecting to ClickHouse): [Download DBeaver](https://dbeaver.io/download/)

---

## Project Structure
The project consists of the following files:
- `docker-compose.yml`: Defines the Elasticsearch, Logstash, and ClickHouse services.
- `logstash.conf`: Logstash configuration file for reading data from Elasticsearch and writing it to ClickHouse.
- `README.md`: This file.

---

## Setup Instructions

### Step 1: Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/your-repo/elasticsearch-logstash-clickhouse.git
cd elasticsearch-logstash-clickhouse
```

---

### Step 2: Start the Services
1. **Update the Logstash Configuration**:
   Open the `logstash.conf` file and replace `your_index_name` with the name of your Elasticsearch index.

2. **Start the Docker Containers**:
   Run the following command to start Elasticsearch, Logstash, and ClickHouse:
   ```bash
   docker-compose up -d
   ```

3. **Verify the Services**:
   - **Elasticsearch**: Open [http://localhost:9200](http://localhost:9200) in your browser or use `curl`:
     ```bash
     curl http://localhost:9200
     ```
   - **ClickHouse**: Open [http://localhost:8123](http://localhost:8123) or use `curl`:
     ```bash
     curl http://localhost:8123
     ```

---

### Step 3: Verify the Pipeline
1. **Add Data to Elasticsearch**:
   Insert sample data into Elasticsearch:
   ```bash
   curl -X POST "http://localhost:9200/your_index_name/_doc" -H "Content-Type: application/json" -d '{
     "imei": "123456789012345",
     "date_created": "2025-02-09T12:00:00Z",
     "imsi": "123456789012345",
     "msisdn": "1234567890"
   }'
   ```

2. **Check Logstash Logs**:
   Ensure Logstash is processing the data:
   ```bash
   docker logs logstash
   ```

3. **Query ClickHouse**:
   Connect to ClickHouse and verify the data:
   ```bash
   docker exec -it clickhouse clickhouse-client --query "SELECT * FROM device_data"
   ```

---

## Connecting to ClickHouse with DBeaver
To connect to ClickHouse using DBeaver:
1. **Install the ClickHouse JDBC Driver**:
   - Open DBeaver.
   - Go to **Database** → **Driver Manager**.
   - Add a new driver with the following details:
     - **Driver Name**: `ClickHouse`
     - **Driver Type**: `Generic`
     - **Class Name**: `ru.yandex.clickhouse.ClickHouseDriver`
     - **URL Template**: `jdbc:clickhouse://{host}[:{port}]/[{database}]`
     - **Default Port**: `8123`
   - Add the ClickHouse JDBC driver JAR file (download from [here](https://github.com/ClickHouse/clickhouse-jdbc)).

2. **Create a New Connection**:
   - Go to **Database** → **New Database Connection**.
   - Select **ClickHouse** and fill in the connection details:
     - **Host**: `localhost`
     - **Port**: `8123`
     - **Database**: `default`
     - **Username**: `default`
     - **Password**: Leave blank.
   - Click **Test Connection** and then **Finish**.

3. **Browse and Query Data**:
   - Use DBeaver to explore the `device_data` table and run SQL queries.

---
