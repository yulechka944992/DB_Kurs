import pytest
from unittest.mock import Mock, patch
from src.data_collector import DataCollector


class TestDataCollector:
    @patch('src.data_collector.APIAeroplanes')
    @patch('src.data_collector.DBManager')
    def test_init(self, mock_db, mock_api):
        """Тест: инициализация DataCollector"""
        collector = DataCollector()

        assert collector.api is not None
        assert collector.db is not None

    @patch('src.data_collector.APIAeroplanes')
    @patch('src.data_collector.DBManager')
    def test_collect_and_save_empty(self, mock_db, mock_api):
        """Тест: сбор данных для пустого списка стран"""
        collector = DataCollector()
        collector.collect_and_save([])

        assert collector.api.get_aircraft_by_country.call_count == 0

    @patch('src.data_collector.APIAeroplanes')
    @patch('src.data_collector.DBManager')
    def test_collect_and_save_one_country(self, mock_db, mock_api):
        """Тест: сбор данных для одной страны"""
        mock_api_instance = mock_api.return_value
        mock_api_instance.get_aircraft_by_country.return_value = [
            {'icao24': 'abc123', 'callsign': 'TEST'}
        ]
        mock_api_instance.get_country_bounds.return_value = ["55.0", "60.0", "30.0", "40.0"]

        mock_db_instance = mock_db.return_value
        mock_db_instance.get_or_create_country.return_value = 1
        mock_db_instance.save_aeroplanes.return_value = 1

        collector = DataCollector()
        collector.collect_and_save(["Russia"])

        mock_api_instance.get_aircraft_by_country.assert_called_once_with("Russia")
        mock_db_instance.get_or_create_country.assert_called_once()
        mock_db_instance.save_aeroplanes.assert_called_once()