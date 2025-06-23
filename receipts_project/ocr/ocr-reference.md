# OCR - Receipt parser documentation

## Files
`receipts/ocr.py` - ReceiptParser class

## Description
ReceiptParser class is used to read text from an image of a receipt and convert it to appropriate JSON output.

Returned JSON format:
- date
- time
- total
- payment method
- items
- discounts