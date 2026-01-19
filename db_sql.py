import os
import urllib.parse
from sqlalchemy import create_engine, text

def get_engine(db_name="orders"):
    user = "postgres"
    password_raw = "P@roli4991"
    host = "localhost"
    port = "5432"
    
    password = urllib.parse.quote_plus(password_raw)
    url = f"postgresql+pg8000://{user}:{password}@{host}:{port}/{db_name}"
    return create_engine(url)

def init_db(sql_file_path):
    # 1. Підключаємося до системної бази 'postgres', щоб створити базу
    sys_engine = get_engine("postgres")
    
    try:
        # Вмикаємо autocommit для створення бази
        with sys_engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            # Перевіряємо, чи існує база 'orders'
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname='orders'"))
            if not result.fetchone():
                conn.execute(text("CREATE DATABASE orders"))
                print("--- База даних 'orders' створена успішно ---")
            else:
                print("--- База даних 'orders' уже існує ---")
    except Exception as e:
        print(f"Помилка при перевірці/створенні бази: {e}")
    finally:
        sys_engine.dispose()

    # 2. Тепер підключаємося до вже створеної бази 'orders' для виконання SQL
    engine = get_engine("orders")
    basedir = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(basedir, sql_file_path)
    
    try:
        with open(full_path, 'rb') as f:
            raw_data = f.read()
        
        # Використовуємо метод з pg8000
        sql_script = raw_data.decode('utf-8', errors='ignore')
        if "CREATE" not in sql_script.upper():
            sql_script = raw_data.decode('cp1251', errors='ignore')

        with engine.connect() as conn:
            # Виконуємо скрипт по одній команді
            for statement in sql_script.split(';'):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()
            print(f"--- Таблиці в базі 'orders' ініціалізовані успішно ---")
    except Exception as e:
        print(f"Помилка при виконанні SQL скрипта: {e}")