from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, count

# 1. Khởi tạo Spark
spark = SparkSession.builder \
    .appName("BusDataBatch_Raw") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.hive.metastore.uris", "thrift://hive-metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()

print(">>> Reading RAW data from HDFS...")

# 2. Đọc file CSV (QUAN TRỌNG: Thêm option delimiter để đọc file Tab-separated)
# Dùng inferSchema=True để Spark tự đoán kiểu dữ liệu (số/chữ)
df = spark.read \
    .option("header", "true") \
    .option("delimiter", "\t") \
    .option("inferSchema", "true") \
    .csv("/data/raw/raw_2025-04-01.csv")

# Debug: In ra schema để chắc chắn đã tách đúng cột
print(">>> Detected Schema:")
df.printSchema()

# Fallback: Nếu vẫn chỉ đọc được 1 cột (do file dùng phẩy), thử đọc lại bằng phẩy
if len(df.columns) <= 1:
    print(">>> WARNING: Tab delimiter failed (only 1 col found). Trying comma...")
    df = spark.read \
        .option("header", "true") \
        .option("delimiter", ",") \
        .option("inferSchema", "true") \
        .csv("/data/raw/raw_2025-04-01.csv")

# 3. Làm sạch và Ép kiểu dữ liệu
# Đảm bảo cột speed là số thực
df_clean = df.withColumn("speed", col("speed").cast("double")) \
             .filter(col("speed").isNotNull() & col("driver").isNotNull())

print(f">>> Processing {df_clean.count()} records...")

# 4. Tính toán thống kê
df_stats = df_clean.groupBy("driver").agg(
    avg("speed").alias("avg_speed"),
    max("speed").alias("max_speed"),
    count("vehicle").alias("trip_count")
)

# 5. Ghi kết quả xuống HDFS
output_path = "/data/processed/driver_stats"
print(f">>> Writing to HDFS: {output_path}")

df_stats.write.mode("overwrite").parquet(output_path)

print(">>> Batch Job Completed Successfully!")
spark.stop()
EOFcat <<EOF > src/spark/batch_processing.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, count

# 1. Khởi tạo Spark
spark = SparkSession.builder \
    .appName("BusDataBatch_Raw") \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .config("spark.hadoop.hive.metastore.uris", "thrift://hive-metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()

print(">>> Reading RAW data from HDFS...")

# 2. Đọc file CSV (QUAN TRỌNG: Thêm option delimiter để đọc file Tab-separated)
# Dùng inferSchema=True để Spark tự đoán kiểu dữ liệu (số/chữ)
df = spark.read \
    .option("header", "true") \
    .option("delimiter", "\t") \
    .option("inferSchema", "true") \
    .csv("/data/raw/raw_2025-04-01.csv")

# Debug: In ra schema để chắc chắn đã tách đúng cột
print(">>> Detected Schema:")
df.printSchema()

# Fallback: Nếu vẫn chỉ đọc được 1 cột (do file dùng phẩy), thử đọc lại bằng phẩy
if len(df.columns) <= 1:
    print(">>> WARNING: Tab delimiter failed (only 1 col found). Trying comma...")
    df = spark.read \
        .option("header", "true") \
        .option("delimiter", ",") \
        .option("inferSchema", "true") \
        .csv("/data/raw/raw_2025-04-01.csv")

# 3. Làm sạch và Ép kiểu dữ liệu
# Đảm bảo cột speed là số thực
df_clean = df.withColumn("speed", col("speed").cast("double")) \
             .filter(col("speed").isNotNull() & col("driver").isNotNull())

print(f">>> Processing {df_clean.count()} records...")

# 4. Tính toán thống kê
df_stats = df_clean.groupBy("driver").agg(
    avg("speed").alias("avg_speed"),
    max("speed").alias("max_speed"),
    count("vehicle").alias("trip_count")
)

# 5. Ghi kết quả xuống HDFS
output_path = "/data/processed/driver_stats"
print(f">>> Writing to HDFS: {output_path}")

df_stats.write.mode("overwrite").parquet(output_path)

print(">>> Batch Job Completed Successfully!")
spark.stop()
