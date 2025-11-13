import json
import csv
import sys
from datetime import datetime
from confluent_kafka import Producer

# Configuration - PRODUCTION READY
conf = {
    'bootstrap.servers': 'localhost:9092',  # Docker Kafka exposed port
    'enable.idempotence': True,  # Đảm bảo không bị duplicate
    'acks': 'all',  # Đảm bảo message được ghi nhận
    'retries': 3,  # Số lần thử lại khi gửi thất bại
    'max.in.flight.requests.per.connection': 5,  # Giới hạn số request đồng thời

    # Batching settings
    'linger.ms': 2,  # Giảm số lần gửi bằng cách chờ
    'batch.size': 32*1024,  # Kích thước batch gửi  32KB
    'compression.type': 'lz4',  # Nén dữ liệu để tiết kiệm băng thông

    # Timeout and buffering
    'message.timeout.ms': 15000,  # Timeout cho mỗi message
    'delivery.timeout.ms': 30000,  # Tổng timeout cho delivery
    'buffer.memory': 64*1024*1024,  # Bộ nhớ đệm 64MB
}

# Create producer instance
producer = Producer(conf)

# Create callback for delivery reports
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

# create send_message function
