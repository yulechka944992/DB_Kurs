import pytest
from unittest.mock import Mock, patch
from src.db_manager import DBManager


class TestDBManager:
    @patch('src.db_manager.psycopg2.connect')
    def test_init(self, mock_connect):
        """Тест: инициализация DBManager"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = DBManager()

        assert db.conn is not None
        assert db.cursor is not None

    @patch('src.db_manager.psycopg2.connect')
    def test_get_or_create_country_existing(self, mock_connect):
        """Тест: получение существующей страны"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)

        db = DBManager()
        country_id = db.get_or_create_country("Russia", ["55.0", "60.0", "30.0", "40.0"])

        assert country_id == 1

    @patch('src.db_manager.psycopg2.connect')
    def test_save_aeroplanes_empty(self, mock_connect):
        """Тест: сохранение пустого списка самолетов"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = DBManager()
        count = db.save_aeroplanes(1, [])

        assert count == 0

    @patch('src.db_manager.psycopg2.connect')
    def test_get_avg_speed(self, mock_connect):
        """Тест: получение средней скорости"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (500.5,)

        db = DBManager()
        avg = db.get_avg_speed()

        assert avg == 500.5

    @patch('src.db_manager.psycopg2.connect')
    def test_get_aeroplanes_with_keyword(self, mock_connect):
        """Тест: поиск по ключевому слову"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("abc123", "ACA123", "USA"),
            ("def456", "ACA456", "Canada")
        ]

        db = DBManager()
        result = db.get_aeroplanes_with_keyword("ACA")

        assert len(result) == 2
        assert result[0]['icao24'] == "abc123"
        assert result[0]['callsign'] == "ACA123"