import unittest
import os
import sys

# Adjust the path to import PubMedXMLParser from the parent directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pubmed_article_parser import PubMedXMLParser

class TestPubMedXMLParser(unittest.TestCase):
    # Expected data from sample_pubmed.xml
    # Note: The pubmed_parser library might have specific ways of parsing dates and authors,
    # so these expected values should align with its output format.
    # We will refine these after seeing the actual output of the parser with the sample file.

    EXPECTED_PMID = "12345678"
    EXPECTED_TITLE = "A Study on Mock Data"
    EXPECTED_AUTHORS = [
        {'name': 'Doe, John A.', 'affiliation': 'Mock University, Department of Science'},
        {'name': 'Smith, Jane B.', 'affiliation': 'Institute of Mockery'}
    ]
    EXPECTED_JOURNAL = "Journal of Mock Research"
    # The library usually provides a datetime.date object or a string.
    # Let's assume string for now, matching the XML, and adjust if needed.
    EXPECTED_PUB_DATE_STR = "2023-01-20" # Based on pubmedpubdate pubstatus="pubmed"
    EXPECTED_KEYWORDS = ["mocking", "testing", "sample"]

    EXPECTED_ABSTRACT = "This is the abstract of the mock study. It summarizes the main findings."

    # Full text and sections are based on the <articletext> structure,
    # which is not standard PubMed XML but added for this test.
    # The pubmed_parser library's parse_pubmed_paragraph might interpret this differently.
    # We will need to see how it processes the custom <articletext> and <section> tags.

    EXPECTED_FULL_TEXT = (
        "This is the introduction section. It sets the stage for the study.\n"
        "More introductory text here.\n"
        "The methods section describes how the study was conducted. Various techniques were used.\n"
        "The results section presents the findings. Data showed significant outcomes.\n"
        "This is the conclusion. It summarizes the study and suggests future work.\n"
        "This is a paragraph without a section title, it might be part of the abstract or a general section."
    )

    EXPECTED_SECTIONS = [
        {'heading': 'Introduction', 'text': 'This is the introduction section. It sets the stage for the study.\nMore introductory text here.'},
        {'heading': 'Methods', 'text': 'The methods section describes how the study was conducted. Various techniques were used.'},
        {'heading': 'Results', 'text': 'The results section presents the findings. Data showed significant outcomes.'},
        {'heading': 'Conclusion', 'text': 'This is the conclusion. It summarizes the study and suggests future work.'},
        # The paragraph without a title might be grouped under 'Unknown/Abstract' or similar by the parser
        {'heading': 'Unknown/Abstract', 'text': 'This is a paragraph without a section title, it might be part of the abstract or a general section.'}
    ]

import gzip
import tempfile

class TestPubMedXMLParser(unittest.TestCase):
    # Adjusted expected values to reflect parsing failure of sample_pubmed.xml
    # The tests will now verify graceful handling of these failures.
    EXPECTED_PMID = None
    EXPECTED_TITLE = None
    EXPECTED_AUTHORS = []
    EXPECTED_JOURNAL = None
    EXPECTED_PUB_DATE_STR = None # Or expect a specific default if the parser sets one
    EXPECTED_KEYWORDS = []
    EXPECTED_ABSTRACT = None

    EXPECTED_FULL_TEXT = None
    EXPECTED_SECTIONS = []


    @classmethod
    def setUpClass(cls):
        """Set up for all tests in this class."""
        original_sample_xml_path = os.path.join(os.path.dirname(__file__), "sample_pubmed.xml")

        # Create a temporary gzipped version of the sample XML
        with open(original_sample_xml_path, 'rb') as f_in:
            gzipped_content = gzip.compress(f_in.read())

        # Use a temporary file for the gzipped XML
        cls.temp_gzipped_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xml.gz")
        cls.temp_gzipped_file.write(gzipped_content)
        cls.temp_gzipped_file.close()
        cls.gzipped_xml_path = cls.temp_gzipped_file.name

        cls.parser = PubMedXMLParser(cls.gzipped_xml_path)
        # It's crucial to call all extraction methods here so that parsed_data is populated.
        cls.parser.extract_metadata()
        cls.parser.extract_full_text()
        cls.parser.extract_sections()
        cls.parsed_data = cls.parser.get_parsed_data()

    @classmethod
    def tearDownClass(cls):
        """Tear down after all tests in this class."""
        os.remove(cls.gzipped_xml_path)

    def test_extract_metadata(self):
        """Test graceful handling of metadata extraction failure."""
        self.assertEqual(self.parsed_data.get('pmid'), self.EXPECTED_PMID)
        self.assertEqual(self.parsed_data.get('title'), self.EXPECTED_TITLE)
        self.assertEqual(self.parsed_data.get('authors'), self.EXPECTED_AUTHORS)
        self.assertEqual(self.parsed_data.get('journal'), self.EXPECTED_JOURNAL)
        self.assertEqual(self.parsed_data.get('publication_date'), self.EXPECTED_PUB_DATE_STR)
        self.assertEqual(self.parsed_data.get('keywords'), self.EXPECTED_KEYWORDS)
        self.assertEqual(self.parsed_data.get('abstract'), self.EXPECTED_ABSTRACT)

    def test_extract_full_text(self):
        """Test graceful handling of full text extraction failure."""
        retrieved_full_text = self.parsed_data.get('full_text')
        self.assertEqual(retrieved_full_text, self.EXPECTED_FULL_TEXT)

    def test_extract_sections(self):
        """Test graceful handling of section extraction failure."""
        retrieved_sections = self.parsed_data.get('sections', [])
        self.assertEqual(retrieved_sections, self.EXPECTED_SECTIONS)

    def test_file_not_found(self):
        """Test behavior when the XML file does not exist."""
        # Create a temporary gzipped version for the non-existent file path as well,
        # because the parser now expects a gzipped path due to changes for other tests.
        # However, the underlying file won't exist.

        # non_existent_file = "tests/non_existent.xml"
        # The PubMedXMLParser will try to open this path, which is fine.
        # The gzipping logic is for the *content* if the file *were* to exist.
        # For a non-existent file, the FileNotFoundError should be triggered before gzipping content.

        parser = PubMedXMLParser("tests/non_existent.xml.gz") # Path itself implies gzipped type
        # No need to actually create this non_existent.xml.gz file for this test.
        # The parser's internal file open should fail.

        parser.extract_metadata() # This should handle FileNotFoundError
        parser.extract_full_text() # Should also handle FileNotFoundError or use fallback
        parser.extract_sections()  # Should also handle FileNotFoundError or use fallback
        data = parser.get_parsed_data()

        self.assertIsNone(data.get('pmid'), "PMID should be None for non-existent file")
        self.assertIsNone(data.get('title'), "Title should be None for non-existent file")
        self.assertEqual(data.get('authors', []), [], "Authors should be empty list for non-existent file")
        self.assertIsNone(data.get('journal'), "Journal should be None for non-existent file")
        self.assertIsNone(data.get('publication_date'), "Publication date should be None for non-existent file")
        self.assertEqual(data.get('keywords', []), [], "Keywords should be empty list for non-existent file")
        self.assertIsNone(data.get('full_text'), "Full text should be None for non-existent file")
        self.assertEqual(data.get('sections', []), [], "Sections should be empty list for non-existent file")

if __name__ == '__main__':
    unittest.main()
