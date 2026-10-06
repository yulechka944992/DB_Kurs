import requests
from typing import Dict, List


class APIAeroplanes:
    """Класс для работы с API"""

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all?"
        self.timeout = 30

    def get_country_bounds(self, country: str) -> List[str]:
        """Получает bounding box- координаты указанной страны"""
        if not country or not country.strip():
            raise ValueError("Название страны не может быть пустым")

        headers_nominatim = {"User-Agent": "test-app"}

        params_nominatim = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        try:
            response = requests.get(
                self.nominatim_url, params=params_nominatim, headers=headers_nominatim, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                raise ValueError(f"Страна '{country}' не найдена")

            bounds = data[0].get("boundingbox")
            if not bounds:
                print(f"Для страны '{country}' не найдены границы")
                return []

            return bounds

        except requests.RequestException as e:
            print(f"Ошибка API при получении {country}: {e}")
            return []

    def get_aircraft_by_bounds(self, bounds: List[str]) -> Dict:
        """Получает данные о самолетах в указанных границах"""
        if bounds is None:
            raise ValueError("Не указаны границы области")

        params_opensky = {
            "lamin": bounds[0],
            "lamax": bounds[1],
            "lomin": bounds[2],
            "lomax": bounds[3],
        }
        try:
            response = requests.get(self.opensky_url, params=params_opensky, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"Ошибка при получении данных о самолетах: {e}")
            return {}

    def get_aircraft_by_country(self, country: str) -> List[Dict]:
        """Получает данные о самолетах для конкретной страны"""
        try:
            bounds = self.get_country_bounds(country)
            if not bounds:
                print(f"Не удалось получить границы для {country}")
                return []

            print(f"Границы {country}: {bounds}")

            raw_data = self.get_aircraft_by_bounds(bounds)
            if not raw_data or "states" not in raw_data:
                print(f"Нет данных о самолетах для {country}")
                return []

            aircraft_list = []
            for state in raw_data["states"]:
                if state:
                    aircraft_list.append(
                        {
                            "icao24": state[0],
                            "callsign": state[1].strip() if state[1] else "",
                            "origin_country": state[2] if state[2] else "Unknown",
                            "time_position": state[3],
                            "last_contact": state[4],
                            "longitude": state[5],
                            "latitude": state[6],
                            "baro_altitude": state[7],
                            "on_ground": state[8],
                            "velocity": state[9],
                            "heading": state[10],
                            "vertical_rate": state[11],
                        }
                    )

            return aircraft_list

        except Exception as e:
            print(f"Ошибка при получении самолетов для {country}: {e}")
            return []

    def get_aircraft_by_countries(self, country_names: List[str]) -> Dict[str, List[Dict]]:
        """Получает данные о самолетах для нескольких стран"""
        if not country_names:
            print("Список стран пуст")
            return {}

        result = {}
        for country in country_names:
            print(f"Получение самолетов для {country}...")
            aircraft = self.get_aircraft_by_country(country)
            result[country] = aircraft
            print(f"Найдено {len(aircraft)} самолетов")

        return result
