import psycopg2
from config import config


class CreateDatabase:
    """Класс для создания таблиц"""

    def __init__(self):
        """Инициализация подключения к базе данных"""
        params = config()

        # 1. Подключаемся к системной базе postgres
        conn = psycopg2.connect(
            host=params["host"],
            user=params["user"],
            password=params["password"],
            port=params["port"],
            database="postgres",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # 2. Проверяем, существует ли база aircraft_tracker
        db_name = params["database"]
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()

        # 3. Если нет - создаем
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ База данных '{db_name}' создана")
        else:
            print(f"ℹ️ База данных '{db_name}' уже существует")

        cursor.close()
        conn.close()

        # 4. Подключаемся к нашей базе
        self.conn = psycopg2.connect(**params)
        self.cursor = self.conn.cursor()
        print(f"✅ Подключение к БД '{params['database']}' установлено")

    def create_tables(self):
        """
        Создание новых таблиц.
        Удаляет старые таблицы и создает новые с чистыми данными.
        """
        try:
            self.cursor.execute("DROP TABLE IF EXISTS aeroplanes CASCADE")
            self.cursor.execute("DROP TABLE IF EXISTS countries CASCADE")
            print("✅ Старые таблицы удалены")

            # Создаем таблицу стран
            self.cursor.execute("""
                CREATE TABLE countries (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    bounds_min_lat DECIMAL(10, 6),
                    bounds_max_lat DECIMAL(10, 6),
                    bounds_min_lon DECIMAL(10, 6),
                    bounds_max_lon DECIMAL(10, 6)
                )
            """)

            # Создаем таблицу самолетов
            self.cursor.execute("""
                CREATE TABLE aeroplanes (
                    id SERIAL PRIMARY KEY,
                    icao24 VARCHAR(10) NOT NULL,
                    callsign VARCHAR(20),
                    origin_country VARCHAR(100),
                    longitude DECIMAL(10, 6),
                    latitude DECIMAL(10, 6),
                    velocity DECIMAL(10, 2),
                    heading DECIMAL(10, 2),
                    on_ground BOOLEAN,
                    country_id INTEGER REFERENCES countries(id)
                )
            """)

            self.conn.commit()

        except psycopg2.Error as e:
            print(f"❌ Ошибка при создании таблиц: {e}")
            self.conn.rollback()
            raise

    def close(self):
        """Закрытие соединения с базой данных"""
        self.cursor.close()
        self.conn.close()
