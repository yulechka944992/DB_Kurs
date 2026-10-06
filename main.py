from src.create_database import CreateDatabase
from src.data_collector import DataCollector
from src.db_manager import DBManager


def show_statistics(db):
    """Показать статистику"""
    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПО САМОЛЕТАМ")
    print("=" * 60)

    # 1. Страны и количество самолетов
    print("\n1. СТРАНЫ И КОЛИЧЕСТВО САМОЛЕТОВ:")
    stats = db.get_countries_and_aeroplanes_count()
    for stat in stats:
        print(f"   {stat['country']}: {stat['count']} самолетов")

    # 2. Все самолеты
    print("\n2. ВСЕ САМОЛЕТЫ В ВОЗДУХЕ:")
    planes = db.get_all_aeroplanes()
    if planes:
        for plane in planes[:5]:
            print(f"   {plane['callsign']} - {plane['velocity']} км/ч, {plane['origin_country']}")
        if len(planes) > 5:
            print(f"   ... и еще {len(planes) - 5} самолетов")
    else:
        print("   Нет самолетов в воздухе")

    # 3. Средняя скорость
    avg_speed = db.get_avg_speed()
    print(f"\n3. СРЕДНЯЯ СКОРОСТЬ: {avg_speed:.2f} км/ч")

    # 4. Самолеты со скоростью выше средней
    fast = db.get_aeroplanes_with_higher_speed()
    print(f"\n4. САМОЛЕТЫ СО СКОРОСТЬЮ ВЫШЕ СРЕДНЕЙ ({len(fast)} шт.):")
    if fast:
        for plane in fast[:5]:
            print(f"   {plane['callsign']} - {plane['velocity']} км/ч")
        if len(fast) > 5:
            print(f"   ... и еще {len(fast) - 5} самолетов")

    # 5. Поиск по ключевому слову
    keyword = "ACA"
    found = db.get_aeroplanes_with_keyword(keyword)
    print(f"\n5. САМОЛЕТЫ С ПОЗЫВНЫМ СОДЕРЖАЩИМ '{keyword}':")
    if found:
        for plane in found:
            print(f"   {plane['callsign']} ({plane['icao24']}) - {plane['origin_country']}")
    else:
        print(f"   Самолетов с позывным '{keyword}' не найдено")


def main():
    # 1. Создаем таблицы
    print("Создание таблиц...")
    setup = CreateDatabase()
    setup.create_tables()
    setup.close()

    # 2. Собираем данные (минимум 4 страны)
    countries = [
        'Russia',
        'United States',
        'Germany',
        'France',
        'Japan',
        'China',
        'United Kingdom',
        'Canada',
        'Australia',
        'Brazil'
    ]

    print("\nСбор данных...")
    collector = DataCollector()
    collector.collect_and_save(countries)
    collector.close()

    # 3. Показываем статистику
    db = DBManager()
    show_statistics(db)
    db.close()


if __name__ == "__main__":
    main()