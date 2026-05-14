#!/usr/bin/env python3
"""
Скрипт для автоматической настройки Airflow в Docker-окружении
Запуск: python setup_airflow.py
"""

import subprocess
import time
import sys
import platform

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"\n{'='*50}")
    print(f"⏳ {description}...")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - выполнено")
        if result.stdout:
            clean_output = result.stdout.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"   {clean_output.strip()}")
        return True
    else:
        print(f"❌ Ошибка при выполнении: {description}")
        if result.stderr:
            clean_error = result.stderr.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"   Ошибка: {clean_error.strip()}")
        return False

def check_containers():
    """Проверка, что контейнеры запущены"""
    print(f"\n{'='*50}")
    print("⏳ Проверка контейнеров...")
    print(f"{'='*50}")
    
    if platform.system() == "Windows":
        result = subprocess.run('docker ps | findstr "postgres-dwh"', shell=True, capture_output=True, text=True)
    else:
        result = subprocess.run('docker ps | grep "postgres-dwh"', shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Контейнеры запущены")
        return True
    else:
        print("❌ Контейнер postgres-dwh не запущен!")
        return False

def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🚀  Установка и настройка Airflow для лабораторной работы ║
    ║                                                              ║
    ║     - Создание базы данных                                   ║
    ║     - Инициализация Airflow                                  ║
    ║     - Создание пользователя                                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Шаг 1: Проверка контейнеров
    if not check_containers():
        print("\n❌ Контейнеры не запущены!")
        print("   Запустите: docker compose up -d")
        print("   Затем снова запустите этот скрипт")
        sys.exit(1)
    
    # Шаг 2: Создание базы данных airflow
    run_command(
        'docker exec postgres-dwh psql -U dwh_user -d postgres -c "CREATE DATABASE airflow;"',
        "Создание базы данных airflow"
    )
    
    # Шаг 3: Выдача прав пользователю
    run_command(
        'docker exec postgres-dwh psql -U dwh_user -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;"',
        "Выдача прав пользователю airflow"
    )
    
    # Шаг 4: Инициализация базы данных Airflow (используем db migrate)
    run_command(
        'docker run --rm --network airflow-data-pipeline-lab_airflow-net -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@postgres-dwh:5432/airflow" apache/airflow:2.7.1 airflow db migrate',
        "Инициализация базы данных Airflow"
    )
    
    # Шаг 5: Создание пользователя Airflow
    run_command(
        'docker run --rm --network airflow-data-pipeline-lab_airflow-net -e AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://airflow:airflow@postgres-dwh:5432/airflow" apache/airflow:2.7.1 airflow users create --username airflow --password airflow --firstname Lab --lastname Student --role Admin --email student@lab.com',
        "Создание администратора Airflow"
    )
    
    # Шаг 6: Перезапуск Airflow
    run_command(
        "docker compose restart airflow",
        "Перезапуск Airflow"
    )
    
    # Шаг 7: Ожидание
    print("\n⏳ Ожидание запуска Airflow (15 секунд)...")
    time.sleep(15)
    
    # Шаг 8: Проверка статуса
    if platform.system() == "Windows":
        run_command("docker ps | findstr airflow", "Проверка статуса Airflow")
    else:
        run_command("docker ps | grep airflow", "Проверка статуса Airflow")
    
    # Финальный вывод
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     ✅  Airflow успешно настроен!                             ║
    ║                                                              ║
    ║     🌐  Откройте в браузере:                                 ║
    ║         http://localhost:8080                               ║
    ║                                                              ║
    ║     👤  Логин:  airflow                                      ║
    ║     🔑  Пароль: airflow                                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()