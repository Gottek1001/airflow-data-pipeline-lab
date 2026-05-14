from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import logging
import pandas as pd
import io

default_args = {
    'owner': 'student',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    dag_id='03_extract_from_minio',
    default_args=default_args,
    description='Выгрузка данных из MinIO (S3) в DWH',
    schedule_interval='0 */2 * * *',  # каждые 2 часа
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['minio', 's3', 'source3']
)

def extract_from_minio(**context):
    """Извлечение CSV-файла из MinIO"""
    s3_hook = S3Hook(aws_conn_id='minio_connection')
    
    # Получаем файл из бакета
    obj = s3_hook.get_key(key='products.csv', bucket_name='raw-data')
    
    if obj is None:
        logging.warning("Файл products.csv не найден в MinIO")
        return 0
    
    # Читаем CSV
    content = obj.get()['Body'].read().decode('utf-8')
    df = pd.read_csv(io.StringIO(content))
    
    context['task_instance'].xcom_push(key='products_data', value=df.to_dict('records'))
    
    logging.info(f"✅ Извлечено {len(df)} продуктов из MinIO")
    return len(df)

def load_to_dwh(**context):
    """Загрузка данных в DWH"""
    products_data = context['task_instance'].xcom_pull(key='products_data', task_ids='extract_minio')
    
    if not products_data:
        logging.info("Нет данных для загрузки")
        return
    
    dwh_hook = PostgresHook(postgres_conn_id='dwh_connection')
    
    for product in products_data:
        sql = """
            INSERT INTO raw.minio_products (product_id, product_name, price, category, load_date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (product_id) DO UPDATE SET
                product_name = EXCLUDED.product_name,
                price = EXCLUDED.price,
                category = EXCLUDED.category
        """
        dwh_hook.run(sql, parameters=(
            product['product_id'],
            product['product_name'],
            product['price'],
            product['category'],
            datetime.now().date()
        ))
    
    log_sql = """
        INSERT INTO mart.load_log (dag_name, source_name, rows_loaded, status)
        VALUES (%s, %s, %s, %s)
    """
    dwh_hook.run(log_sql, parameters=('03_extract_from_minio', 'MinIO', len(products_data), 'SUCCESS'))
    
    logging.info(f"✅ Загружено {len(products_data)} продуктов в DWH")

extract_task = PythonOperator(
    task_id='extract_minio',
    python_callable=extract_from_minio,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_dwh',
    python_callable=load_to_dwh,
    dag=dag,
)

extract_task >> load_task