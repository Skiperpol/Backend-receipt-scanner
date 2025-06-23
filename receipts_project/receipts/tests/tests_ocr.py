import pytest

from datetime import date, time

from receipts.ocr import ReceiptParser


class TestReceiptParser:

    @pytest.mark.parametrize("text,expected", [
        ("2025-03-04", "2025-03-04"),
        ("04.03.2025", "04.03.2025"),
        ("Invalid", None),
    ])
    def test_extract_date(self, text, expected):
        assert ReceiptParser.extract_date(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("14:32", "14:32"),
        ("14.32", "14:32"),
        ("7;21", "07:21"),
        ("59:99", None),
    ])
    def test_extract_time(self, text, expected):
        assert ReceiptParser.extract_time(text) == expected

    @pytest.mark.parametrize("text,expected", [
        ("Gotówka", "CASH"),
        ("Karta", "CARD"),
        ("Blik", None),
    ])
    def test_extract_payment_method(self, text, expected):
        assert ReceiptParser.extract_payment_method(text) == expected

    @pytest.mark.parametrize("price_str,expected", [
        ("123,45", 123.45),
        ("~123 45", -123.45),
        ("9.99", 9.99),
        ("invalid", None),
    ])
    def test_parse_price(self, price_str, expected):
        assert ReceiptParser.parse_price(price_str) == expected

    @pytest.mark.parametrize("item_str,expected", [
        ("MASŁO 10szt", (10, "MASŁO")),
        ("CHLEB * 2", (2, "CHLEB *")),
        ("JABŁKA", (None, "JABŁKA")),
    ])
    def test_parse_count(self, item_str, expected):
        assert ReceiptParser.parse_count(item_str) == expected

    @pytest.mark.parametrize("date_str,expected", [
        ("2024-06-01", date(2024, 6, 1)),
        ("01.06.2024", date(2024, 6, 1)),
        ("wrong", None),
    ])
    def test_parse_date(self, date_str, expected):
        assert ReceiptParser.parse_date(date_str) == expected

    @pytest.mark.parametrize("time_str,expected", [
        ("14:21", time(14, 21)),
        ("7:03", time(7, 3)),
        ("25:00", None),
    ])
    def test_parse_time(self, time_str, expected):
        assert ReceiptParser.parse_time(time_str) == expected

    def test_fuzzy_find_substring(self):
        text = "to jest paragon fiskalny test"
        pattern = "paragon fiskalny"
        match = ReceiptParser.fuzzy_find_substring(text, pattern, threshold=70)
        assert match is not None
        start, end = match
        assert "paragon fiskalny" in text[start:end].lower()

    def test_extract_items_basic(self):
        # Synthetic output
        test_text = """
        SVETER 1*79,9o /9,90 A
        TORBA 2szt x5,99 = 11,98 A
        """
        items, discounts = ReceiptParser.extract_items(test_text)

        assert len(items) == 2

        assert items[0]["name"].lower().startswith("sveter")
        assert items[0]["price"] == 79.90
        assert items[0]["count"] == 1
        assert not items[0]["count_estimated"]

        assert items[1]["name"].lower().startswith("torba")
        assert items[1]["price"] == 5.99
        assert items[1]["count"] == 2
        assert not items[1]["count_estimated"]

        assert discounts == []

    def test_split_receipt_sections_simple(self):
        parser = ReceiptParser(gpu=False)

        # Synthetic output
        parser.raw_output = [
            "SKLEP ABC",
            "ul. Przykładowa 1",
            "PARAGON FISKALNY",
            "SVETER 1*79,90= 79,90 A",
            "SPRZEDAŻ OPODATKOWANA",
            "SUMA PLN 79,90",
            "XYZ1234567890",
            "Karta"
        ]

        sections = parser.split_receipt_sections()

        assert "header" in sections
        assert "items" in sections
        assert "summary" in sections
        assert "identifier" in sections
        assert "footer" in sections

        assert "SKLEP ABC" in sections["header"]
        assert "SVETER" in sections["items"]
        assert "SUMA PLN" in sections["summary"]
        assert "XYZ1234567890" in sections["identifier"]