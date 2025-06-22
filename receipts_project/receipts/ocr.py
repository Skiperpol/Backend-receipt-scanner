from json import dump
from os import path
from re import search, split, compile, VERBOSE, IGNORECASE
from datetime import datetime, date, time
from pathlib import Path
from typing import Optional
from numpy import ndarray
from rapidfuzz import fuzz
from easyocr import Reader

import cv2

# TODO: Add type annotations
class ReceiptParser:

    supported_payment_methods = {
        'Karta': 'CARD',
        'Gotówka': 'CASH'
    }

    def __init__(self, gpu: bool = True):
        # Settings
        self.threshold = 75 # Global threshold
        self.gpu = gpu
        self.image = None

        # Extracted text
        self.raw_output = []
        self.sections = {}

        # Extracted elements
        self.date = None
        self.time = None
        self.total = None
        self.payment_method = None
        self.items = None

        self.reader = Reader(lang_list=['pl', 'en'], gpu=self.gpu)

    def load_image_from_path(self, image_path: Path):
        # Check whether provided path is correct
        if not path.exists(image_path):
            raise FileNotFoundError(f'File {image_path} not found')
        self.__load_image(image_path.as_posix())

    def load_image_from_np_ndarray(self, np_ndarray: ndarray):
        if np_ndarray is None or np_ndarray.size == 0:
            raise ValueError('Invalid numpy array')
        self.__load_image(np_ndarray)

    def __load_image(self, image_input):
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
        elif isinstance(image_input, ndarray):
            image = image_input
        else:
            raise TypeError("Unsupported image input type")

        self.image = image

    def extract_text(self):
        """
        Read text from an image
        :return:  raw output
        """
        # Check whether the receipt has been loaded correctly
        if self.image is None:
            raise ValueError(f'Image not loaded. Use load_image_from_XXX to load an image of a receipt first')

        # Process image
        result = self.reader.readtext(
            self.image,
            detail=0,
            paragraph=True,
            contrast_ths=0.3,
            adjust_contrast=0.5,
            canvas_size=5000
        )

        self.raw_output = [line.strip() for line in result if line.strip()] # type: ignore

        return self.raw_output

    def split_receipt_sections(self) -> dict:
        """
        Split raw image output into sections
        :return: dictionary of sections (header, items, summary, identifier, footer)
        """

        text = "\n".join(self.raw_output)

        # Normalize case
        text_lower = text.lower()

        # Section 1 (header) - until "PARAGON FISKALNY"
        match = self.fuzzy_find_substring(text_lower, pattern="paragon fiskalny", threshold=self.threshold)

        if not match:
            raise ValueError("Couldn't find keyword: 'paragon fiskalny'")

        idx_title_start, idx_title_end = match

        # Section 3 (summary) - from "SPRZED. OPOD" or "SPRZEDAŻ. OPODATKOWANA"
        summary_matches = ['Sprzedaż opodatkowana', 'Sprzedaz opodatkowana', 'Sprzedaż opodatk.', 'Sprzedaz opodatk.', 'Sprzed. opod.', 'Sprzed_ opod_']
        summary_match = None

        for match in summary_matches:
            summary_match = self.fuzzy_find_substring(text_lower[idx_title_end:], pattern=match, threshold=85)
            if summary_match:
                break

        if not summary_match:
            raise ValueError("Couldn't find keyword: 'Sprzedaż opodatkowana'")

        idx_summary_start, _ = summary_match
        idx_summary_start += idx_title_end

        # Section 3 ends with "SUMA PLN <float>"
        total_match = self.fuzzy_find_substring(text_lower[idx_summary_start:], pattern="SUMA PLN", threshold=self.threshold)
        if not match:
            raise ValueError("Couldn't find keyword: 'SUMA PLN'")

        _, idx_summary_end = total_match # type: ignore
        idx_summary_end += idx_summary_start

        # Convert next digits to total
        amount_match = search(r'(\d{1,5})[,.\s](\d{2})', text_lower[idx_summary_end:])

        if not amount_match:
            raise ValueError("Couldn't find the total")

        whole, decimal = amount_match.groups()
        amount_str = f"{whole}.{decimal}"

        try:
            self.total = float(amount_str)
        except ValueError:
            raise ValueError("Error while converting the total to float (likely distorted data)")

        idx_summary_end += amount_match.end()

        # Section 4 (identifier) – 40 digits code + fiscal logo + identifier: 3 letters + 10 digits
        tail_text = text[idx_summary_end:]
        identifier_match = search(r"\b(?!nip)[A-Z]{3}[\s()\\.,;'\-/\[\]]*\d{10}\b", tail_text, flags=IGNORECASE)

        if not identifier_match:
            raise ValueError("Couldn't find the receipt identifier")

        idx_identifier_end = idx_summary_end + identifier_match.end()

        # Create dictionary to return
        self.sections['header'] = text[:idx_title_start].strip()
        self.sections['items'] = text[idx_title_end:idx_summary_start].strip()
        self.sections['summary'] = text[idx_summary_start:idx_summary_end].strip()
        self.sections['identifier'] = text[idx_summary_end:idx_identifier_end].strip()
        self.sections['footer'] = text[idx_identifier_end:].strip()

        return self.sections

    def extract_data_from_sections(self):
        """
        Extract data from extracted sections and save it
        """
        # Date can be found in the header or identifier section
        raw_date = self.extract_date(self.sections['header']) or self.extract_date(self.sections['identifier'])
        # Time can be found in the identifier section or footer section
        raw_time = self.extract_time(self.sections['identifier']) or self.extract_time(self.sections['footer'])

        self.date = self.parse_date(raw_date) if raw_date else None
        self.time = self.parse_time(raw_time) if raw_time else None

        # Payment method can be found in the identifier or footer section
        self.payment_method = self.extract_payment_method(self.sections['identifier']) or self.extract_payment_method(self.sections['footer'])

        # Items can be found in the items section (well who would have expected)
        self.items = self.extract_items(self.sections['items'])


    def to_json(self):
        return {
            "date": None if self.date is None else self.date.isoformat(),
            "time": None if self.time is None else self.time.strftime("%H:%M:%S"),
            "total": self.total,
            "payment_method": self.payment_method,
            "items": self.items
        }

    def save_to_json_file(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            dump(self.to_json(), f, indent=4, ensure_ascii=False)

    def run(self):
        """
        MAIN FUNCTION\n
        1. Extract text from an image
        2. Split raw image output into sections
        3. Extract data from sections
        :return: JSON representation of sections
        """
        self.extract_text()
        self.split_receipt_sections()
        self.extract_data_from_sections()

        return self.to_json()


    # Static methods used for various data conversions or extractions --------------------------------------------------

    # TODO: Add variable offset
    @staticmethod
    def fuzzy_find_substring(text: str, pattern: str, threshold: int = 85, ignore_case: bool = True) -> Optional[
        tuple[int, int]]:
        """
        Perform fuzzy search

        :param text: search section
        :param pattern: keyword
        :param threshold: confidence threshold
        :param ignore_case: ignore case. If set to True, converts search section and keyword to lowercase before performing fuzzy search
        :return: tuple: (index_start, index_end) or None
        """
        text = text.lower()
        pattern = pattern.lower() if ignore_case else pattern
        best_score = 0
        best_match = None

        window_size = len(pattern)
        for i in range(len(text) - window_size + 1):
            window = text[i:i + window_size + 2]  # +2 offset in case of poor quality raw data. Higher values = less accuracy but higher chance of matching
            score = fuzz.ratio(window, pattern)
            if score > best_score and score >= threshold:
                best_score = score
                best_match = (i, i + len(window))

        return best_match

    # TODO: Add items count verification
    # TODO: Code cleanup
    # TODO: Add discounts recognition
    @staticmethod
    def extract_items(items_section: str, verify_items_count: bool = False, estimate_items_count: bool = True, estimation_threshold: float = 0.05):
        """
        WIP
        :param items_section: items section
        :param verify_items_count: whether to verify items count (WIP)
        :param estimate_items_count: whether to estimate items count based on total amount and price of an item
        :param estimation_threshold: threshold for count estimation (in case of fail count is set to None)
        """

        # Try to replace some characters before parsing for better results
        def __replace_characters(text: str) -> str:
            char_to_digit = {
                'O': '0', 'Q': '0',
                'I': '1', 'L': '1', '|': '1',
                'Z': '2',
                'E': '3',
                'A': '4',
                'S': '5',
                '/': '7',
                'B': '8',
            }

            return ''.join(char_to_digit.get(c.upper(), c) for c in text)

        # Prepare items_section
        normalized_items_section = __replace_characters(items_section)

        # Items list
        # Structure:
        #   "name": item name,
        #   "price": item price,
        #   "count": item count,
        #   "count_estimated": is item count estimated
        items = []

        pattern = compile(
            r"""[*x]?\s* (\d+\s*[.,\s]\s*\d{2}) \s*[=/\\]?\s* (\d+\s*[.,\s]\s*\d{2}) \s*[A-Za-z]?\d*""", VERBOSE
            # Pattern explanation:
            #   optional * lub x (count indication)
            #   first price (item) (np. 59,99 / 59 99 / 59.99)
            #   separator: ' ' = / \
            #   second price (total)
            #   optional letters (tax rate) (np. A / 4 / A5)
        )

        matches = pattern.finditer(normalized_items_section)
        idx_current = 0

        for match in matches:
            # print(f'{match} | {match.group(1)} | {match.group(2)} | {match.start()} | {match.end()}')

            item_raw = items_section[idx_current:match.start()]
            price_raw = match.group(1)
            total_raw = match.group(2)

            count, item_raw = ReceiptParser.parse_count(item_raw)  # Get count and trim item if necessary
            price = ReceiptParser.parse_price(price_raw)
            total = ReceiptParser.parse_price(total_raw)

            # Try to calculate the count based on extracted price and total (if count couldn't be parsed)
            is_count_estimated = False

            if estimate_items_count and not count:
                count_estimation = total / price # type: ignore

                if abs(count_estimation - round(count_estimation)) <= estimation_threshold:
                    count = int(count_estimation)
                    is_count_estimated = True

            # Create a dictionary
            items.append({
                "name": item_raw,
                "price": price,
                "count": count,
                "count_estimated": is_count_estimated
            })

            idx_current = match.end()

        # if verify_items_count:
        #     comma_count = items_section.count(',')
        #     if comma_count % 2 != 0:
        #         raise AssertionError(f'Invalid comma count {comma_count}. Expected even number (2 commas for each product).')
        #     if comma_count != len(items) * 2:
        #         raise AssertionError(f'Invalid number of products. Got: {len(items)}, expected: {int(comma_count / 2)}')

        return items

    @staticmethod
    def extract_date(text: str) -> Optional[str]:
        """
        Attempt to extract date from text
        :param text: search section
        :return: date string or None
        """
        # Date patterns
        patterns = [
            r'\b\d{4}[-./]\d{2}[-./]\d{2}',  # 2025-03-04, 2025.03.04, 2025/03/04
            r'\b\d{2}[-./]\d{2}[-./]\d{4}',  # 04-03-2025, 04.03.2025, 04/03/2025
        ]
        for pattern in patterns:
            match = search(pattern, text)
            if match:
                return match.group()
        return None

    @staticmethod
    def extract_time(text: str) -> Optional[str]:
        """
        Attempt to extract time from text
        :param text: search section
        :return: HH:MM string or None
        """
        match = search(r'\d{2}:\d{2}(?::\d{2})?\b', text)
        if match:
            # Return hours and minutes
            return match.group()[:5]
        return None

    @staticmethod
    def extract_payment_method(payment_method_search_section: str) -> Optional[str]:
        """
        Attempt to extract payment method from payment method search section
        :param payment_method_search_section: search section
        :return: payment_method name (if supported) or None
        """

        for payment_method_pattern, payment_method_name in ReceiptParser.supported_payment_methods.items():
            match = ReceiptParser.fuzzy_find_substring(payment_method_search_section, pattern=payment_method_pattern, threshold=70)
            if match is not None:
                return payment_method_name
        return None

    # Parsing methods --------------------------------------------------------------------------------------------------

    @staticmethod
    def parse_price(price_str: str) -> Optional[float]:
        parts = [s.strip() for s in split(r"[,.\s]", price_str)]
        try:
            price = float(f'{parts[0]}.{parts[1]}')
        except ValueError:
            return None
        return price

    @staticmethod
    def parse_count(item_str: str):

        last_characters_search_count = 5 # Usually the count can be found near the end of a product's name, ex. MASŁO 10szt, CHLEB * 2

        last_characters = item_str[-last_characters_search_count:]

        # Search for digits
        match = search(r'\d(?:\s?\d){0,}', last_characters)

        if match:
            matched_fragment = match.group()
            number = int(matched_fragment.replace(' ', ''))

            # Remove count from the original item string and leave only the name of a product
            start_index = len(item_str) - last_characters_search_count + match.start()
            cleaned_string = item_str[:start_index]

            return number, cleaned_string.strip()

        return None, item_str.strip()

    @staticmethod
    def parse_date(date_str: str) -> Optional[date]:
        """
        Attempt to parse date from a string
        :param date_str: string representation of date
        :return: datetime.date or None
        """
        formats = ["%Y-%m-%d", "%Y.%m.%d", "%d-%m-%Y", "%d.%m.%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    # TODO: Improve time parsing (add different separators, add a verification and constraints (0 <= HH <= 24, 0 <= MM <= 59)
    @staticmethod
    def parse_time(time_str: str) -> Optional[time]:
        """
        Attempt to parse time from a string
        :param time_str: string representation of time
        :return: datetime.time or None
        """
        try:
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            try:
                return datetime.strptime(time_str, "%H:%M:%S").time()
            except ValueError:
                return None

# ----------------------------------------------------------------------------------------------------------------------

"""
Examples:

# 1

    parser = ReceiptParser()
    parser.load_image_from_path('receipt.png')
    
    parser.extract_text()
    parser.split_receipt_sections()
    parser.extract_data_from_sections()
    
    parser.save_to_json_file('receipt.json'))
    
# 2
    
    parser = ReceiptParser()
    parser.load_image_from_np_ndarray(image_as_np_ndarray)
    parser.run()

"""