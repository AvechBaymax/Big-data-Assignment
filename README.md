# 🚌 Bus GPS Lambda Architecture

Hệ thống **Big Data Pipeline** xử lý dữ liệu GPS xe buýt theo kiến trúc **Lambda Architecture** với real-time streaming và batch processing.

![Architecture](https://img.shields.io/badge/Architecture-Lambda-blue)
![Kafka](https://img.shields.io/badge/Kafka-3.x-orange)
![Spark](https://img.shields.io/badge/Spark-3.5-yellow)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Grafana](https://img.shields.io/badge/Grafana-10.2-green)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

---

## 📊 Dataset

- **Nguồn dữ liệu**: GPS xe buýt TP.HCM (~9.8 triệu bản ghi/ngày, 2,575 xe)
- **Kích thước**: 849MB raw data
- **Thuộc tính**:
  - `datetime` - Thời gian ghi nhận
  - `vehicle_id` - Mã xe (biển số)
  - `lng`, `lat` - Tọa độ GPS
  - `speed` - Tốc độ (km/h)
  - `driver` - Mã tài xế
  - `door_up`, `door_down` - Trạng thái cửa

---

## 🏗️ Lambda Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LAMBDA ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────┐     ┌─────────────────────────────────────────────────────┐  │
│   │  CSV     │     │                   SPEED LAYER                       │  │
│   │  Data    │────▶│  Kafka ──▶ Consumer ──▶ PostgreSQL ──▶ Grafana     │  │
│   │          │     │  (Real-time streaming, <1s latency)                 │  │
│   └──────────┘     └─────────────────────────────────────────────────────┘  │
│        │                                                                     │
│        │           ┌─────────────────────────────────────────────────────┐  │
│        │           │                   BATCH LAYER                        │  │
│        └──────────▶│  HDFS ──▶ Spark ──▶ PostgreSQL                      │  │
│                    │  (Daily aggregations, analytics)                     │  │
│                    └─────────────────────────────────────────────────────┘  │
│                                                                              │
│                    ┌─────────────────────────────────────────────────────┐  │
│                    │                  SERVING LAYER                       │  │
│                    │  PostgreSQL (Speed + Batch views)                    │  │
│                    │  Grafana Dashboard (Visualization)                   │  │
│                    └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🐳 Tech Stack

| Component      | Technology   | Version | Port | Role                      |
| -------------- | ------------ | ------- | ---- | ------------------------- |
| Message Broker | Apache Kafka | 7.4.0   | 9092 | Real-time streaming       |
| Storage        | Hadoop HDFS  | 3.2.1   | 9870 | Distributed storage       |
| Processing     | Apache Spark | 3.5.0   | 8082 | Batch & Stream processing |
| Database       | PostgreSQL   | 15      | 5432 | Serving layer             |
| Visualization  | Grafana      | 10.2.0  | 3000 | Real-time dashboard       |
| DB Admin       | pgAdmin      | 4       | 5050 | Database management       |
| Coordination   | Zookeeper    | 7.4.0   | 2181 | Kafka coordination        |

---

## 📁 Project Structure

```
first_project/
├── docker-compose.yml          # Docker infrastructure
├── hadoop.env                  # Hadoop configuration
├── requirements.txt            # Python dependencies
│
├── config/
│   └── grafana/
│       ├── dashboards/
│       │   └── bus_realtime.json       # Grafana dashboard
│       └── provisioning/
│           ├── dashboards/dashboards.yml
│           └── datasources/datasources.yml
│
├── data/
│   ├── raw_2025-04-01.csv      # Full dataset (849MB)
│   └── samples/                # Test datasets
│       ├── sample_quick_test.csv    (1,000 records)
│       ├── sample_small_dev.csv     (10,000 records)
│       ├── sample_medium_test.csv   (50,000 records)
│       └── sample_first_hour.csv    (100,000 records)
│
├── scripts/
│   ├── init_db.sql             # PostgreSQL schema
│   ├── create_sample_data.py   # Generate sample data
│   ├── run_demo.ps1            # Windows demo script
│   └── run_demo.sh             # Linux demo script
│
└── src/
    ├── kafka/
    │   ├── producer.py         # CSV → Kafka producer
    │   └── consumer.py         # Kafka → Console consumer
    │
    ├── streaming/
    │   └── speed_layer_consumer.py  # Kafka → PostgreSQL (Speed Layer)
    │
    └── spark/
        ├── batch_layer.py      # HDFS → PostgreSQL (Batch Layer)
        └── batch_processing.py # Spark batch jobs
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Docker Desktop
- Python 3.10+
- Git

### 2. Clone & Setup

```bash
git clone https://github.com/AvechBaymax/Big-data-Assignment.git
cd Big-data-Assignment
git checkout lambda_architectur
```

### 3. Start Infrastructure

```bash
# Start all services
docker-compose up -d

# Wait for services to be healthy (~60s)
docker ps

# Create Kafka topic
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic bus-gps-tracking \
  --partitions 3 \
  --replication-factor 1

# Initialize PostgreSQL database
docker exec postgres psql -U admin -d postgres -c "CREATE DATABASE bus_analytics;"
cat scripts/init_db.sql | docker exec -i postgres psql -U admin -d bus_analytics
```

### 4. Install Python Dependencies

```bash
pip install confluent-kafka psycopg2-binary pyspark
```

### 5. Run the Pipeline

**Terminal 1 - Start Speed Layer Consumer:**

```bash
python src/streaming/speed_layer_consumer.py
```

**Terminal 2 - Send Data via Producer:**

```bash
# Quick test (1000 records)
python src/kafka/producer.py data/samples/sample_quick_test.csv 1000

# Medium test (50000 records)
python src/kafka/producer.py data/samples/sample_medium_test.csv 50000

# Full data
python src/kafka/producer.py data/raw_2025-04-01.csv
```

### 6. View Dashboard

Open Grafana: http://localhost:3000

- **Username**: admin
- **Password**: admin123
- Navigate to: **Dashboards → Bus GPS → Bus GPS Real-time Dashboard**

---

## 📊 Dashboard Features

| Panel                   | Description                             |
| ----------------------- | --------------------------------------- |
| Active Buses            | Count of buses active in last 5 minutes |
| Avg Speed (km/h)        | Average speed of all buses              |
| Events (Last Hour)      | Total GPS events in the last hour       |
| Door Events (1h)        | Door open/close events                  |
| Real-time Bus Locations | Geo-map showing bus positions           |
| Speed Over Time         | Time-series chart of speed              |

---

## 🗄️ Database Schema

### Speed Layer Tables (Real-time)

```sql
-- Current bus locations (latest position per vehicle)
bus_realtime_location (
    vehicle_id, latitude, longitude, speed,
    driver_id, door_up, door_down, last_updated
)

-- Streaming history (last 24 hours)
bus_tracking_stream (
    id, vehicle_id, latitude, longitude, speed,
    driver_id, door_up, door_down, event_time, ingested_at
)
```

### Batch Layer Tables (Analytics)

```sql
-- Daily vehicle summary
daily_vehicle_summary (
    summary_date, vehicle_id, total_records, total_distance_km,
    avg_speed, max_speed, active_hours, door_events
)

-- Hourly traffic analysis
hourly_traffic_analysis (
    analysis_date, hour_of_day, active_vehicles,
    total_events, avg_speed, speed_variance
)

-- Driver performance
driver_performance (
    report_date, driver_id, vehicles_driven, total_events,
    avg_speed, max_speed, total_door_events
)

-- Geographic hotspots
geo_hotspots (
    analysis_date, lat_bucket, lng_bucket, event_count,
    unique_vehicles, avg_speed
)
```

---

## 🔧 Service URLs

| Service       | URL                   | Credentials             |
| ------------- | --------------------- | ----------------------- |
| Grafana       | http://localhost:3000 | admin / admin123        |
| pgAdmin       | http://localhost:5050 | admin@admin.com / admin |
| Spark Master  | http://localhost:8082 | -                       |
| HDFS Namenode | http://localhost:9870 | -                       |
| Kafka         | localhost:9092        | -                       |

---

## 🧪 Testing

### Test Kafka Connection

```bash
# List topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Consume messages
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic bus-gps-tracking \
  --from-beginning --max-messages 5
```

### Test PostgreSQL

```bash
# Check tables
docker exec postgres psql -U admin -d bus_analytics -c "\dt"

# Query real-time data
docker exec postgres psql -U admin -d bus_analytics -c \
  "SELECT COUNT(*) FROM bus_realtime_location;"
```

---

## 📈 Performance

| Metric              | Value           |
| ------------------- | --------------- |
| Producer Throughput | ~5,000 msgs/sec |
| Consumer Latency    | <1 second       |
| Kafka Partitions    | 3               |
| Compression         | LZ4             |
| Batch Insert Size   | 100 records     |

---

## 🛑 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean reset)
docker-compose down -v
```

---

## 👥 Authors

- **Team**: Big Data Assignment - HCMUT

---

## 📝 License

MIT License
