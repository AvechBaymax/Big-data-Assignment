from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, DoubleType, IntegerType

# Initialize Spark
spark = SparkSession.builder \
    .appName("BusDataBatch") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

# 1. Create Dummy Data (In real life, read from Kafka/HDFS raw JSON)
data = [
    ("bus-101", "2025-04-01 08:00:00", 45.5, "Driver A"),
    ("bus-101", "2025-04-01 08:00:05", 48.0, "Driver A"),
    ("bus-102", "2025-04-01 08:00:00", 35.0, "Driver B"),
    ("bus-102", "2025-04-01 08:00:05", 0.0,  "Driver B"),
]

schema = StructType() \
    .add("vehicle_id", StringType()) \
    .add("timestamp", StringType()) \
    .add("speed", DoubleType()) \
    .add("driver", StringType())

df = spark.createDataFrame(data, schema)

# 2. Process: Calculate Average Speed per Driver
df_stats = df.groupBy("driver").avg("speed").withColumnRenamed("avg(speed)", "avg_speed")

# 3. Write to HDFS in Parquet format (Trino loves Parquet)
# We write to a specific folder in HDFS
output_path = "/data/processed/driver_stats"
print(f"Writing data to HDFS: {output_path}")

df_stats.write.mode("overwrite").parquet(output_path)

print("Batch Job Completed Successfully!")
spark.stop()