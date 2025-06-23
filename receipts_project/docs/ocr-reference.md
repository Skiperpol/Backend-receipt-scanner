# OCR - Receipt parser documentation

## Files
`receipts/ocr.py` - ReceiptParser class

## Description
The `ReceiptParser` class is responsible for analyzing receipt images using OCR (EasyOCR), splitting the text into sections and extracting key information such as: date, time, products, total, payment method and discounts.<br>

> This parser works **only with fiscal receipts**, as they have standardized layout. Non-fiscal receipts will not be parsed correctly or even parsed at all.

For more detailed information on how this works, check the comments in the code.

Returned JSON format:
- date
- time
- total
- payment method
- items
- discounts

### Quick start

1. Load the image of your receipt
- using `numpy` array:
```python
parser = ReceiptParser()
parser.load_image_from_np_ndarray(image_as_np_ndarray)
```
- or using `Path` object:
```python
parser = ReceiptParser()
image_path = Path() / 'my_receipts' / 'receipt.png'
parser.load_image_from_path(image_path)
```
2. **Run it!**
```python
json_result = parser.run()
```
Depending on the capabilities of your CPU/GPU, this may take a while!

3. View the result or save it as a JSON file:
```python
print(json_result)
```
```python
parser.save_to_json_file(Path('receipt.json'))
```

## Methods

### Constructor
```python
ReceiptParser(gpu: bool = True)
```

**Other important params**:
- `supported_payment_methods_patterns` - Recognized keywords used in payment methods extraction
- `supported_discount_patterns` - Recognized keywords used in discounts extraction
- `self.threshold` - Global threshold for the **fuzzy search**

### Loading an image
```python
def load_image_from_path(self, image_path: Path) -> None:
```

```python
def load_image_from_np_ndarray(self, np_ndarray: ndarray) -> None:
```

```python
def __load_image(self, image_input: Union[str, ndarray]) -> None:
```
This is a private method. Do not use it directly - use `load_image_from_path` or `load_image_from_np_ndarray` instead

### Extracting text

```python
def extract_text(self) -> list[str]:
```
Returns the extracted list of raw strings from the loaded image

```python
def split_receipt_sections(self) -> dict[str, str]:
```
Splits the extracted list of raw strings into corresponding sections and returns the following dictionary:
- `header`: shop name, address, NIP (taxpayer identification number)
- `items`: items, discounts
- `summary`: total, tax rates
- `identifier`: receipt's identifier, date, time, fiscal logo
- `footer`: payment method, other non-important data

Additionally, extracts `total`, as this is more optimal to do it while splitting sections

```python
def extract_data_from_sections(self) -> None:
```
Extracts the following data from sections:
- `date` - `datetime.date`
- `time` - `datetime.time`
- `payment_method` - `str`
- `items` - `list` of: **name**, **price** and **count**
- `discounts` - `list` of: **name/type** and **discount amount**

If some part could not be extracted, returns `None` or an empty `list`

### Exporting data

```python
def to_json(self) -> dict[str, Any]:
```

```python
def save_to_json_file(self, filepath: Path) -> None:
```

```python
def run(self) -> dict[str, Any]:
```
Main function (like standard `main()`) - parses and then returns data as `JSON` file. Remember to load the image of your receipt beforehand

### Static methods
Static methods used as helpers

```python
def fuzzy_find_substring(text: str, pattern: str, threshold: int = 85, offset: int = 2, ignore_case: bool = True) -> Optional[tuple[int, int]]:
```
Finds a `pattern` in the `provided text`
- `threshold` - confidence threshold. Higher = more strict search
- `offset` - additional search window size.
  - `offset < 0` - search window size smaller than pattern length (**not recommended, will likely result in no matches**)
  - `offset = 0` - search window size same as pattern length
  - `offset > 0` - search window size bigger than pattern length (**recommended, takes into account the possibility of spelling errors**)

```python
def extract_items(items_section: str, estimate_items_count: bool = True, estimation_threshold: float = 0.05) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
```
Extracts items and discounts
- `estimate_items_count` - whether try parser should attempt to estimate the count of items based on their price and total
- `estimation_threshold` - acceptable rounding error when estimating the count. If the error is bigger, the count is set to 1

```python
def extract_date(text: str) -> Optional[str]:
```

```python
def extract_time(text: str) -> Optional[str]:
```

```python
def extract_payment_method(payment_method_search_section: str) -> Optional[str]:
```

### Parsing various elements
Methods used to convert **raw string data** to corresponding **type**, ex. date -> `datetime.date`

```python
def parse_price(price_str: str) -> Optional[float]:
```

```python
def parse_count(item_str: str) -> tuple[Optional[int], str]:
```
Returns the parsed count and raw item string without the count part, ex. `MLEKO x 1 szt` -> `(1, MLEKO)`

```python
def parse_date(date_str: str) -> Optional[date]:
```

```python
def parse_time(time_str: str) -> Optional[time]:
```