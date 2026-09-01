from src.api_aeroplanes import APIAeroplanes
from src.db_manager import DBManager


class DataCollector:
    """Класс для сбора и сохранения данных"""

    def __init__(self):
        self.api = APIAeroplanes()
        self.db = DBManager()

    def collect_and_save(self, countries: list):
        """Собрать и сохранить данные по странам"""
        for country in countries:
            print(f"\nОбработка {country}...")

            # Получаем самолеты
            aircrafts = self.api.get_aircraft_by_country(country)

            if not aircrafts:
                print(f"Нет данных для {country}")
                continue

            # Получаем границы
            bounds = self.api.get_country_bounds(country)

            # Сохраняем страну
            country_id = self.db.get_or_create_country(country, bounds)

            # Сохраняем самолеты
            count = self.db.save_aeroplanes(country_id, aircrafts)
            print(f"Сохранено {count} самолетов")

    def close(self):
        """Закрыть соединение с БД"""
        self.db.close()
