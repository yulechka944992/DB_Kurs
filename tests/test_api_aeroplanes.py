import pytest
import requests
from unittest.mock import Mock, patch, MagicMock

from requests import RequestException

from src.api_aeroplanes import APIAeroplanes


class TestAPIAeroplanes:
    """Тесты для класса APIAeroplanes"""

    @pytest.fixture
    def api(self):
        return APIAeroplanes()

    def test_get_country_bounds_success(self, api):
        """Тест успешного получения границ страны"""
        with patch("src.api_aeroplanes.requests.get") as mock_get:

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"boundingbox": ["55.0", "60.0", "30.0", "40.0"]}]
            mock_get.return_value = mock_response

            bounds = api.get_country_bounds("Russia")

            assert bounds == ["55.0", "60.0", "30.0", "40.0"]
            mock_get.assert_called_once()

    def test_get_country_bounds_empty_country(self, api):
        """Пустое название страны"""
        with pytest.raises(ValueError) as exc_info:
            api.get_country_bounds("")
        assert "Название страны не может быть пустым" in str(exc_info.value)

        with pytest.raises(ValueError):
            api.get_country_bounds("   ")

    def test_get_country_bounds_country_not_found(self, api):
        """Тест: страна не найдена"""
        with patch("src.api_aeroplanes.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

        with pytest.raises(ValueError) as exc_info:
            api.get_country_bounds("Zombieland")

        assert "Страна 'Zombieland' не найдена" in str(exc_info.value)

    def test_get_country_not_bounds(self, api):
        """Страна найдена, но без bounding box"""
        with patch("src.api_aeroplanes.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = [{"name": "Test"}]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            with patch("builtins.print") as mock_print:
                bounds = api.get_country_bounds("Test")

                assert bounds == []
                mock_print.assert_called_once_with("Для страны 'Test' не найдены границы")

    def test_get_country_bounds_request_exception(self, api):
        """Ошибка сети/API"""
        with patch("src.api_aeroplanes.requests.get") as mock_get:
            mock_get.side_effect = RequestException("Connection error")

            with patch("builtins.print") as mock_print:
                bounds = api.get_country_bounds("Russia")

                assert bounds == []
                mock_print.assert_called_once_with("Ошибка API при получении Russia: Connection error")

    def test_get_aircraft_by_bounds_none(self, api):
        """bounds = None"""
        with pytest.raises(ValueError) as exc_info:
            api.get_aircraft_by_bounds(None)
        assert "Не указаны границы области" in str(exc_info.value)

    def test_get_aircraft_by_bounds_success(self, api):
        """Успешное получение данных"""
        with patch("src.api_aeroplanes.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "states": [["abc123", "TEST", "US", 123, 456, 10.0, 20.0, 1000, False, 200, 90, 5]]
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = api.get_aircraft_by_bounds(["55.0", "60.0", "30.0", "40.0"])

            assert result == {"states": [["abc123", "TEST", "US", 123, 456, 10.0, 20.0, 1000, False, 200, 90, 5]]}

    def test_get_aircraft_by_bounds_request_exception(self, api):
        """Ошибка API"""
        with patch("src.api_aeroplanes.requests.get") as mock_get:
            mock_get.side_effect = RequestException("API error")

            with patch("builtins.print") as mock_print:
                result = api.get_aircraft_by_bounds(["55.0", "60.0", "30.0", "40.0"])

                assert result == {}
                mock_print.assert_called_once_with("Ошибка при получении данных о самолетах: API error")

    def test_get_aircraft_by_country_success(self, api):
        """Успешное получение самолетов по стране"""
        with patch.object(api, "get_country_bounds") as mock_bounds:
            with patch.object(api, "get_aircraft_by_bounds") as mock_aircraft:
                mock_bounds.return_value = ["55.0", "60.0", "30.0", "40.0"]
                mock_aircraft.return_value = {
                    "states": [["abc123", "TEST", "US", 123, 456, 10.0, 20.0, 1000, False, 200, 90, 5]]
                }

                result = api.get_aircraft_by_country("Russia")

                expected = [
                    {
                        "icao24": "abc123",
                        "callsign": "TEST",
                        "origin_country": "US",
                        "time_position": 123,
                        "last_contact": 456,
                        "longitude": 10.0,
                        "latitude": 20.0,
                        "baro_altitude": 1000,
                        "on_ground": False,
                        "velocity": 200,
                        "heading": 90,
                        "vertical_rate": 5,
                    }
                ]
                assert result == expected

    def test_get_aircraft_by_countries_success(self, api):
        """Успешное получение для нескольких стран"""
        with patch.object(api, "get_aircraft_by_country") as mock_get:
            mock_get.side_effect = [[{"icao24": "abc1", "callsign": "FLT1"}], [{"icao24": "abc2", "callsign": "FLT2"}]]

            with patch("builtins.print") as mock_print:
                result = api.get_aircraft_by_countries(["Russia", "USA"])

                expected = {
                    "Russia": [{"icao24": "abc1", "callsign": "FLT1"}],
                    "USA": [{"icao24": "abc2", "callsign": "FLT2"}],
                }
                assert result == expected
                assert mock_print.call_count == 4

    def test_get_aircraft_by_countries_empty(self, api):
        """Пустой список стран"""
        with patch("builtins.print") as mock_print:
            result = api.get_aircraft_by_countries([])

            assert result == {}
            mock_print.assert_called_once_with("Список стран пуст")
