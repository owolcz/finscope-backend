from unittest.mock import patch
from datetime import datetime
import zoneinfo

from services.finnhub import _is_market_open, get_market_status


def test_rynek_zamkniety_w_weekend():
    # giełda powinna być zamknięta w sobotę niezależnie od godziny
    tz_name = "America/New_York"
    tz = zoneinfo.ZoneInfo(tz_name)
    sobota = datetime(2023, 1, 7, 12, 0, 0, tzinfo=tz)

    with patch("services.finnhub.datetime") as mock_dt:
        mock_dt.now.return_value = sobota
        assert _is_market_open(tz_name, "09:30", "16:00") is False


def test_rynek_otwarty_w_godzinach_handlu():
    # giełda powinna być otwarta w poniedziałek o 10:00
    tz_name = "America/New_York"
    tz = zoneinfo.ZoneInfo(tz_name)
    poniedzialek_10 = datetime(2023, 1, 2, 10, 0, 0, tzinfo=tz)

    with patch("services.finnhub.datetime") as mock_dt:
        mock_dt.now.return_value = poniedzialek_10
        assert _is_market_open(tz_name, "09:30", "16:00") is True


def test_rynek_zamkniety_przed_otwarciem():
    # giełda powinna być zamknięta w poniedziałek o 8:00, przed otwarciem o 9:30
    tz_name = "America/New_York"
    tz = zoneinfo.ZoneInfo(tz_name)
    poniedzialek_8 = datetime(2023, 1, 2, 8, 0, 0, tzinfo=tz)

    with patch("services.finnhub.datetime") as mock_dt:
        mock_dt.now.return_value = poniedzialek_8
        assert _is_market_open(tz_name, "09:30", "16:00") is False


async def test_get_market_status_zwraca_cztery_gieldy():
    # API obsługuje dokładnie 4 giełdy: US, UK, Canada, Germany
    result = await get_market_status()
    assert len(result) == 4


async def test_get_market_status_ma_wymagane_pola():
    # każda giełda musi mieć region i status open/closed
    result = await get_market_status()
    for market in result:
        assert "region" in market
        assert "current_status" in market
        assert market["current_status"] in ("open", "closed")
