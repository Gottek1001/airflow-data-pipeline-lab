from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import logging
import pandas as pd

default_args = {
    'owner': 'student',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    dag_id='02_extract_from_postgresql',
    default_args=default_args,
    description='Инкрементальная выгрузка из PostgreSQL в DWH',
    schedule_interval='*/10 * * * *',  # каждые 10 минут
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['postgresql', 'source2']
)

def extract_incremental_users(**context):
    """Инкрементальная выгрузка пользователей (только изменённые)"""
    
    # Подключаемся к источнику
    source_hook = PostgresHook(postgres_conn_id='source_postgres')
    
    # Получаем последнюю загруженную дату из XCom или используем начальную
    last_loaded = context['task_instance'].xcom_pull(key='last_loaded_ts', task_ids='extract_users') or '1970-01-01'
    
    # Выбираем только новые или изменённые записи
    sql = f"""
        SELECT id, name, email, status, updated_at
        FROM users
        WHERE updated_at > '{last_loaded}'
        ORDER BY updated_at
    """
    
    df = source_hook.get_pandas_df(sql)
    
    if not df.empty:
        new_max_ts = df['updated_at'].max()
    else:
        new_max_ts = last_loaded
    
    context['task_instance'].xcom_push(key='users_data', value=df.to_dict('records'))
    context['task_instance'].xcom_push(key='last_loaded_ts', value=str(new_max_ts))
    
    logging.info(f"✅ Извлечено {len(df)} новых/изменённых пользователей")
    return len(df)

def load_users_to_dwh(**context):
    """Загрузка пользователей в DWH"""
    users_data = context['task_instance'].xcom_pull(key='users_data', task_ids='extract_users')
    
    if not users_data:
        logging.info("Нет новых данных для загрузки")
        return
    
    dwh_hook = PostgresHook(postgres_conn_id='dwh_connection')
    
    for user in users_data:
        sql = """
            INSERT INTO raw.pg_users (id, name, email, status, source_updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                email = EXCLUDED.email,
                status = EXCLUDED.status,
                source_updated_at = EXCLUDED.source_updated_at
        """
        dwh_hook.run(sql, parameters=(
            user['id'],
            user['name'],
            user['email'],
            user['status'],
            user['updated_at']
        ))
    
    log_sql = """
        INSERT INTO mart.load_log (dag_name, source_name, rows_loaded, status)
        VALUES (%s, %s, %s, %s)
    """
    dwh_hook.run(log_sql, parameters=('02_extract_from_postgresql', 'PostgreSQL', len(users_data), 'SUCCESS'))
    
    logging.info(f"✅ Загружено {len(users_data)} пользователей в DWH")

def extract_orders(**context):
    """Выгрузка заказов из источника"""
    source_hook = PostgresHook(postgres_conn_id='source_postgres')
    df = source_hook.get_pandas_df("SELECT id, user_id, amount, order_date FROM orders")
    context['task_instance'].xcom_push(key='orders_data', value=df.to_dict('records'))
    logging.info(f"✅ Извлечено {len(df)} заказов")

def load_orders_to_dwh(**context):
    """Загрузка заказов в DWH"""
    orders_data = context['task_instance'].xcom_pull(key='orders_data', task_ids='extract_orders')
    
    if not orders_data:
        return
    
    dwh_hook = PostgresHook(postgres_conn_id='dwh_connection')
    
    for order in orders_data:
        sql = """
            INSERT INTO raw.pg_orders (id, user_id, amount, order_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """
        dwh_hook.run(sql, parameters=(
            order['id'],
            order['user_id'],
            order['amount'],
            order['order_date']
        ))
    
    logging.info(f"✅ Загружено {len(orders_data)} заказов в DWH")

# Задачи для пользователей
extract_users_task = PythonOperator(
    task_id='extract_users',
    python_callable=extract_incremental_users,
    dag=dag,
)

load_users_task = PythonOperator(
    task_id='load_users',
    python_callable=load_users_to_dwh,
    dag=dag,
)

# Задачи для заказов
extract_orders_task = PythonOperator(
    task_id='extract_orders',
    python_callable=extract_orders,
    dag=dag,
)

load_orders_task = PythonOperator(
    task_id='load_orders',
    python_callable=load_orders_to_dwh,
    dag=dag,
)

# Порядок выполнения
extract_users_task >> load_users_task
extract_orders_task >> load_orders_task