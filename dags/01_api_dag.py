from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.hooks.http import HttpHook
from datetime import datetime, timedelta
import logging

default_args = {
    'owner': 'student',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    dag_id='01_extract_from_api',
    default_args=default_args,
    description='Выгрузка данных из API в DWH',
    schedule_interval='*/5 * * * *',  # каждые 5 минут (CRON)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['api', 'source1']
)

def extract_from_api(**context):
    """Извлечение данных из API"""
    http_hook = HttpHook(method='GET', http_conn_id='mock_api')
    response = http_hook.run(endpoint='/orders?limit=15')
    data = response.json()
    
    context['task_instance'].xcom_push(key='api_data', value=data['data'])
    logging.info(f"✅ Извлечено {len(data['data'])} заказов из API")
    return len(data['data'])

def load_to_dwh(**context):
    """Загрузка данных в DWH (сырой слой)"""
    api_data = context['task_instance'].xcom_pull(key='api_data', task_ids='extract_api')
    
    pg_hook = PostgresHook(postgres_conn_id='dwh_connection')
    
    for order in api_data:
        sql = """
            INSERT INTO raw.api_orders 
            (order_id, customer_id, product, amount, quantity, status, order_date, load_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """
        pg_hook.run(sql, parameters=(
            order['order_id'],
            order['customer_id'],
            order['product'],
            order['amount'],
            order['quantity'],
            order['status'],
            order['order_date'],
            datetime.now().date()
        ))
    
    # Логируем загрузку
    log_sql = """
        INSERT INTO mart.load_log (dag_name, source_name, rows_loaded, status)
        VALUES (%s, %s, %s, %s)
    """
    pg_hook.run(log_sql, parameters=('01_extract_from_api', 'API', len(api_data), 'SUCCESS'))
    
    logging.info(f"✅ Загружено {len(api_data)} записей в DWH")

extract_task = PythonOperator(
    task_id='extract_api',
    python_callable=extract_from_api,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_to_dwh',
    python_callable=load_to_dwh,
    dag=dag,
)

extract_task >> load_task