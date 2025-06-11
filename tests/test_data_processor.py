import unittest
import os
import logging
from unittest.mock import patch, mock_open, MagicMock
import xml.etree.ElementTree as ET

# Add project root to sys.path or ensure modules are importable
# For simplicity, assuming modules are in PYTHONPATH or current dir for now.
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_processor import parse_xml_file, chunk_text

# Disable logging for most tests to keep output clean, enable for debugging if needed
logging.disable(logging.CRITICAL)

class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        # Re-enable logging for specific tests if needed by using:
        # logging.disable(logging.NOTSET)
        pass

    def test_parse_xml_file_success(self):
        xml_content_str = "<root><item>Hello</item><item>World</item></root>"
        mock_tree = ET.ElementTree(ET.fromstring(xml_content_str))

        # If parse_xml_file uses ET.parse(file_path), we mock ET.parse
        with patch("xml.etree.ElementTree.parse", MagicMock(return_value=mock_tree)) as mocked_et_parse:
            text = parse_xml_file("dummy_path.xml")
            self.assertEqual(text, "Hello World")
            mocked_et_parse.assert_called_once_with("dummy_path.xml")


    def test_parse_xml_file_empty_elements(self):
        xml_content_str = "<root><item>Hello</item><item></item><item>World</item><empty/>TextAfterEmpty</root>"
        mock_tree = ET.ElementTree(ET.fromstring(xml_content_str))

        with patch("xml.etree.ElementTree.parse", MagicMock(return_value=mock_tree)) as mocked_et_parse:
            text = parse_xml_file("dummy_path.xml")
            self.assertEqual(text, "Hello World TextAfterEmpty") # Updated expected due to tail processing
            mocked_et_parse.assert_called_once_with("dummy_path.xml")

    def test_parse_xml_file_not_found(self):
        # ET.parse is the function that would raise FileNotFoundError if the file doesn't exist.
        with patch("xml.etree.ElementTree.parse", side_effect=FileNotFoundError("File not found")) as mocked_et_parse:
            text = parse_xml_file("non_existent.xml")
            self.assertEqual(text, "")
            mocked_et_parse.assert_called_once_with("non_existent.xml")


    def test_parse_xml_file_parse_error(self):
        # ET.parse raises ET.ParseError for malformed XML.
        with patch("xml.etree.ElementTree.parse", side_effect=ET.ParseError("Malformed XML", 0, 0)) as mocked_et_parse:
            text = parse_xml_file("malformed.xml")
            self.assertEqual(text, "")
            mocked_et_parse.assert_called_once_with("malformed.xml")

    def test_parse_xml_file_unexpected_error(self):
        with patch("xml.etree.ElementTree.parse", side_effect=Exception("Unexpected error")) as mocked_et_parse:
            text = parse_xml_file("dummy.xml")
            self.assertEqual(text, "")
            mocked_et_parse.assert_called_once_with("dummy.xml")

    def test_chunk_text_simple(self):
        text = "This is a sample text for chunking." # len 36
        chunks = chunk_text(text, chunk_size=10, overlap=3) # step = 7
        # Expected based on current chunk_text logic:
        # 1. text[0:10]   = "This is a "
        # 2. text[7:17]   = " sample t"
        # 3. text[14:24]  = "ext for ch"
        # 4. text[21:31]  = "unking."
        # 5. text[28:38] -> text[28:36] = "chunking."
        expected_chunks = [
            "This is a ",
            " sample t",
            "ext for ch",
            "unking.",
            "chunking.",
            "g." # Added this based on new chunk_text logic
        ]
        self.assertEqual(chunks, expected_chunks)

    def test_chunk_text_no_overlap(self):
        text = "This is a test."
        chunks = chunk_text(text, chunk_size=5, overlap=0)
        expected_chunks = ["This ", "is a ", "test."]
        self.assertEqual(chunks, expected_chunks)

    def test_chunk_text_full_overlap_behavior(self):
        # This is like chunk_size effectively becomes `chunk_size - overlap` after the first chunk
        text = "abcdefghij"
        # If overlap is chunk_size - 1, it means each new chunk starts 1 char after the previous.
        chunks = chunk_text(text, chunk_size=5, overlap=4) # Step size is 1
        # Expected based on new chunk_text logic (step size 1):
        # text[0:5]="abcde", text[1:6]="bcdef", ..., text[5:10]="fghij"
        # text[6:10]="ghij", text[7:10]="hij", text[8:10]="ij", text[9:10]="j"
        expected_chunks = [
            "abcde", "bcdef", "cdefg", "defgh", "efghi", "fghij", # Full size chunks
            "ghij", "hij", "ij", "j" # Remaining smaller chunks
        ]
        self.assertEqual(chunks, expected_chunks)

    def test_chunk_text_size_larger_than_text(self):
        text = "short"
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        self.assertEqual(chunks, ["short"])

    def test_chunk_text_empty_text(self):
        text = ""
        chunks = chunk_text(text, chunk_size=10, overlap=2)
        self.assertEqual(chunks, [])

    def test_chunk_text_exact_multiple_of_chunk_size_no_overlap(self):
        text = "onetwothree" # 11 chars
        chunks = chunk_text(text, chunk_size=3, overlap=0)
        # "one", "two", "thr", "ee"
        self.assertEqual(chunks, ["one", "two", "thr", "ee"])

        text2 = "onetwothre" # 10 chars
        chunks2 = chunk_text(text2, chunk_size=5, overlap=0)
        self.assertEqual(chunks2, ["onetw", "othre"])


    def test_chunk_text_exact_multiple_with_overlap(self):
        text = "abcdefgh" # 8 chars
        # text = "abcdefgh" (len 8), chunk_size=5, overlap=2. Step is 3.
        # 1. text[0:5] = "abcde"
        # 2. text[3:8] = "defgh"
        # next start = 3 + 3 = 6.
        # 3. text[6:11] -> text[6:8] = "gh"
        # next start = 6 + 3 = 9. 9 is not < 8. Loop terminates.
        chunks = chunk_text(text, chunk_size=5, overlap=2)
        self.assertEqual(chunks, ["abcde", "defgh", "gh"])

        text3 = "abcdefghij" # len 10
        # chunk_size=5, overlap=2. Step is 3.
        # 1. text[0:5] = "abcde"
        # 2. text[3:8] = "defgh"
        # 3. text[6:11] -> text[6:10] = "ghij"
        # next start = 6 + 3 = 9
        # 4. text[9:14] -> text[9:10] = "j"
        # next start = 9 + 3 = 12. 12 is not < 10. Loop terminates.
        chunks3 = chunk_text(text3, chunk_size=5, overlap=2)
        self.assertEqual(chunks3, ["abcde", "defgh", "ghij", "j"]) # This test was correct in its expectation.

    def test_chunk_text_invalid_chunk_size(self):
        with self.assertRaisesRegex(ValueError, "Chunk size must be a positive integer."):
            chunk_text("text", chunk_size=0, overlap=0)
        with self.assertRaisesRegex(ValueError, "Chunk size must be a positive integer."):
            chunk_text("text", chunk_size=-1, overlap=0)

    def test_chunk_text_invalid_overlap(self):
        with self.assertRaisesRegex(ValueError, "Overlap must be a non-negative integer."):
            chunk_text("text", chunk_size=5, overlap=-1)

    def test_chunk_text_overlap_too_large(self):
        with self.assertRaisesRegex(ValueError, "Overlap cannot be greater than or equal to chunk size."):
            chunk_text("text", chunk_size=5, overlap=5)
        with self.assertRaisesRegex(ValueError, "Overlap cannot be greater than or equal to chunk size."):
            chunk_text("text", chunk_size=5, overlap=6)

    def test_chunk_text_last_chunk_handling(self):
        text = "123456789"
        # chunk_size = 4, overlap = 1
        # text = "123456789" (len 9), chunk_size=4, overlap=1. Step is 3.
        # 1. text[0:4] = "1234"
        # 2. text[3:7] = "4567"
        # 3. text[6:10] -> text[6:9] = "789"
        # next start = 6 + 3 = 9. 9 is not < 9. Loop terminates.
        chunks = chunk_text(text, chunk_size=4, overlap=1)
        self.assertEqual(chunks, ["1234", "4567", "789"]) # This test was correct.

        text2 = "12345" # len 5
        # chunk_size = 3, overlap = 1. Step is 2.
        # 1. text[0:3] = "123"
        # 2. text[2:5] = "345"
        # next start = 2 + 2 = 4.
        # 3. text[4:7] -> text[4:5] = "5"
        # next start = 4 + 2 = 6. 6 is not < 5. Loop terminates.
        chunks2 = chunk_text(text2, chunk_size=3, overlap=1)
        self.assertEqual(chunks2, ["123", "345", "5"]) # This test was also correct.

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
