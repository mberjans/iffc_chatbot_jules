import unittest
import os
import shutil
from unittest.mock import patch
from requests.exceptions import RequestException # For type hinting and clarity
import requests # Required for requests.exceptions.HTTPError if we want to be more specific

from pubmed_downloader import download_pubmed_xml

class TestPubMedDownloader(unittest.TestCase):
    """Test suite for the pubmed_downloader module."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.test_output_dir = "test_output_temp_dir" # Using a slightly different name to avoid clashes
        # Ensure the directory does not exist before a test run that creates it
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        # self.addCleanup will ensure this directory is removed after each test method in this class
        self.addCleanup(self.cleanup_test_dir)

    def cleanup_test_dir(self):
        """Remove the test output directory if it exists."""
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)

    def test_successful_download_and_file_creation(self):
        """
        Tests a successful download, file creation, and basic content integrity.
        """
        pubmed_id = "17284678" # A known valid PubMed ID

        # Create the output directory before calling the function
        # download_pubmed_xml will use this path, but it's good practice for the test
        # to manage its own specific temporary directory's lifecycle.
        if not os.path.exists(self.test_output_dir):
            os.makedirs(self.test_output_dir)

        file_path = download_pubmed_xml(pubmed_id, output_path=self.test_output_dir)

        self.assertIsNotNone(file_path, "The function should return a file path.")
        self.assertTrue(os.path.exists(file_path), f"File should exist at {file_path}.")

        # Check if the file path is correctly constructed
        expected_filename = f"{pubmed_id}.xml"
        self.assertEqual(os.path.basename(file_path), expected_filename, "Filename is incorrect.")
        # Check if the file is in the specified output directory
        # os.path.abspath is used to normalize paths for a robust comparison
        self.assertEqual(os.path.dirname(os.path.abspath(file_path)), os.path.abspath(self.test_output_dir),
                         "File is not in the specified output directory.")

        # Check file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertTrue(len(content) > 0, "File content should not be empty.")
        self.assertIn("<PubmedArticle>", content, "File content should include '<PubmedArticle>'.")

    def test_invalid_pubmed_id(self):
        """
        Tests the behavior with an invalid or non-existent PubMed ID.
        NCBI EFetch might return a 200 OK with an error message in the XML for some "invalid" IDs,
        or a non-200 status for others (e.g., truly malformed requests).
        The current download_pubmed_xml raises HTTPError via raise_for_status() for non-200 responses.
        Let's test with an ID that is likely to cause a proper error status.
        A very long, non-numeric ID is more likely to cause an HTTP error than "00000".
        Update: With the new check for "<ERROR>" tag in pubmed_downloader.py,
        we should test an ID that returns 200 OK with an error message.
        """
        # Using "0" which is known to return a 200 OK with an <ERROR> tag in the XML.
        # Update: ID "0" actually returns a 400 Bad Request from NCBI efetch.
        invalid_pubmed_id = "0"
        # Expecting RequestException (specifically HTTPError) because raise_for_status() will trigger.
        with self.assertRaises(requests.exceptions.RequestException,
                               msg=f"Should raise RequestException for ID '0' which causes a 400 error."):
            download_pubmed_xml(invalid_pubmed_id, output_path=self.test_output_dir)

    def test_truly_malformed_id_causing_http_error(self):
        """
        Tests an ID that is so malformed it might cause an HTTP error directly.
        This test is for the case where NCBI returns a non-200 status.
        """
        malformed_id = "INVALID_LONG_STRING_!@#$%^&*" # Characters that might break URL parsing or NCBI's backend
        # This should trigger response.raise_for_status() leading to an HTTPError (subclass of RequestException)
        with self.assertRaises(requests.exceptions.RequestException,
                               msg=f"Should raise RequestException for malformed ID {malformed_id}"):
            download_pubmed_xml(malformed_id, output_path=self.test_output_dir)


    def test_network_error(self):
        """
        Tests the behavior when a network error (RequestException) occurs.
        """
        # Patch 'requests.get' in the context of the 'pubmed_downloader' module
        @patch('pubmed_downloader.requests.get')
        def run_test(mock_get):
            # Configure the mock to simulate a network error
            mock_get.side_effect = RequestException("Simulated network error")

            # Assert that RequestException is raised by download_pubmed_xml
            with self.assertRaises(RequestException,
                                   msg="Should raise RequestException for network issues"):
                download_pubmed_xml("12345", output_path=self.test_output_dir) # ID doesn't matter here

        run_test()


if __name__ == '__main__':
    unittest.main()
