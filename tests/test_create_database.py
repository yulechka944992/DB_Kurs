import pytest
from unittest.mock import Mock, patch
from src.create_database import CreateDatabase


class TestCreateDatabase:
    @patch("src.create_database.psycopg2.connect")
    def test_init_connection(self, mock_connect):
        """Тест: подключение к БД"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = CreateDatabase()

        assert db.conn is not None
        assert db.cursor is not None

    @patch("src.create_database.psycopg2.connect")
    def test_create_tables(self, mock_connect):
        """Тест: создание таблиц"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db = CreateDatabase()
        db.create_tables()

        # Проверяем, что execute вызывался 4 раза (2 DROP + 2 CREATE)
        assert mock_cursor.execute.call_count >= 4
