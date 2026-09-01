from typing import List, Dict

import psycopg2
from config import config

class DBManager:
    def __init__(self):
        params = config()

        self.conn = psycopg2.connect(**params)
        self.cursor = self.conn.cursor()

    def get_or_create_country(self, name: str, bounds: List[str]) -> int:
        """Получить ID страны или создать новую"""
        self.cursor.execute("SELECT id FROM countries WHERE name = %s", (name,))
        result = self.cursor.fetchone()

        if result:
            return result[0]

        self.cursor.execute("""
            INSERT INTO countries (name, bounds_min_lat, bounds_max_lat, bounds_min_lon, bounds_max_lon)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (name, bounds[0], bounds[1], bounds[2], bounds[3]))

        country_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return country_id

    def save_aeroplanes(self, country_id: int, aircrafts: List[Dict]) -> int:
        """Сохранить самолеты"""
        count = 0
        for plane in aircrafts:
            self.cursor.execute("""
                INSERT INTO aeroplanes (
                    icao24, callsign, origin_country, longitude, latitude,
                    velocity, heading, on_ground, country_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                plane.get('icao24'),
                plane.get('callsign', ''),
                plane.get('origin_country', 'Unknown'),
                plane.get('longitude'),
                plane.get('latitude'),
                plane.get('velocity'),
                plane.get('heading'),
                plane.get('on_ground', False),
                country_id
            ))
            count += 1

        self.conn.commit()
        return count

    def get_countries_and_aeroplanes_count(self) -> List[Dict]:
        """Список стран и количество самолетов"""
        self.cursor.execute("""
            SELECT c.name, COUNT(a.id) as count
            FROM countries c
            LEFT JOIN aeroplanes a ON c.id = a.country_id
            GROUP BY c.id, c.name
            ORDER BY count DESC
        """)

        return [{'country': row[0], 'count': row[1]} for row in self.cursor.fetchall()]

    def get_all_aeroplanes(self) -> List[Dict]:
        """Список всех самолетов в воздухе"""
        self.cursor.execute("""
                    SELECT icao24, callsign, origin_country, velocity, latitude, longitude
                    FROM aeroplanes
                    WHERE on_ground = false
                """)

        return [
            {
                'icao24': row[0],
                'callsign': row[1],
                'origin_country': row[2],
                'velocity': row[3],
                'latitude': row[4],
                'longitude': row[5]
            }
            for row in self.cursor.fetchall()
        ]

    def get_avg_speed(self) -> float:
        """Средняя скорость"""
        self.cursor.execute("""
                    SELECT AVG(velocity) 
                    FROM aeroplanes 
                    WHERE velocity IS NOT NULL AND on_ground = false
                """)

        result = self.cursor.fetchone()[0]
        return float(result) if result else 0.0

    def get_aeroplanes_with_higher_speed(self) -> List[Dict]:
        """Самолеты со скоростью выше средней"""
        avg_speed = self.get_avg_speed()

        self.cursor.execute("""
                    SELECT icao24, callsign, velocity
                    FROM aeroplanes
                    WHERE velocity > %s AND on_ground = false
                    ORDER BY velocity DESC
                """, (avg_speed,))

        return [
            {'icao24': row[0], 'callsign': row[1], 'velocity': row[2]}
            for row in self.cursor.fetchall()
        ]

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Dict]:
        """Поиск по ключевому слову в позывном"""
        self.cursor.execute("""
                    SELECT icao24, callsign, origin_country
                    FROM aeroplanes
                    WHERE callsign ILIKE %s AND on_ground = false
                """, (f'%{keyword}%',))

        return [
            {'icao24': row[0], 'callsign': row[1], 'origin_country': row[2]}
            for row in self.cursor.fetchall()
        ]

    def close(self):
        """Закрыть соединение"""
        self.cursor.close()
        self.conn.close()
        