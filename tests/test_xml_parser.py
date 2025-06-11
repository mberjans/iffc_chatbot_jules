import unittest
import os
import xml.etree.ElementTree as ET
from src.xml_parser import parse_xml # Assuming src is in PYTHONPATH or added to sys.path

# Helper to create dummy XML files
def create_dummy_xml(file_path, content):
    with open(file_path, "w") as f:
        f.write(content)

class TestXmlParser(unittest.TestCase):

    def setUp(self):
        # Create a directory for test files if it doesn't exist
        self.test_data_dir = "test_data_xml_parser"
        if not os.path.exists(self.test_data_dir):
            os.makedirs(self.test_data_dir)

        self.valid_xml_file = os.path.join(self.test_data_dir, "valid.xml")
        self.invalid_xml_file = os.path.join(self.test_data_dir, "invalid.xml")
        self.empty_xml_file = os.path.join(self.test_data_dir, "empty.xml") # For malformed empty
        self.non_existent_file = os.path.join(self.test_data_dir, "non_existent.xml")

        create_dummy_xml(self.valid_xml_file, "<root><item>Test</item></root>")
        create_dummy_xml(self.invalid_xml_file, "<root><item>Test</item>") # Malformed XML
        create_dummy_xml(self.empty_xml_file, "") # Empty file, will cause ParseError

    def tearDown(self):
        # Clean up created files and directory
        if os.path.exists(self.valid_xml_file):
            os.remove(self.valid_xml_file)
        if os.path.exists(self.invalid_xml_file):
            os.remove(self.invalid_xml_file)
        if os.path.exists(self.empty_xml_file):
            os.remove(self.empty_xml_file)
        if os.path.exists(self.test_data_dir):
            # Check if directory is empty before removing (optional, rmdir fails if not empty)
            if not os.listdir(self.test_data_dir):
                 os.rmdir(self.test_data_dir)
            else:
                # If other files were created, clean them up too or handle as needed
                # For now, assume only these files are there.
                # A more robust cleanup might involve shutil.rmtree(self.test_data_dir)
                # but that's more aggressive.
                pass # Or shutil.rmtree if sure
        # For safety, let's use shutil.rmtree if the directory exists
        import shutil
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)


    def test_parse_valid_xml(self):
        root = parse_xml(self.valid_xml_file)
        self.assertIsNotNone(root)
        self.assertEqual(root.tag, "root")
        self.assertEqual(root.find("item").text, "Test")

    def test_parse_invalid_xml(self):
        # Suppress print output from parse_xml for this test if desired
        # import io
        # from contextlib import redirect_stderr
        # f = io.StringIO()
        # with redirect_stderr(f):
        #     root = parse_xml(self.invalid_xml_file)
        # self.assertIsNone(root)
        # self.assertIn("Error parsing XML file", f.getvalue())

        # Simpler: just check for None and assume error message is printed
        root = parse_xml(self.invalid_xml_file)
        self.assertIsNone(root)

    def test_parse_empty_xml_file(self):
        # An empty file is also a form of invalid XML
        root = parse_xml(self.empty_xml_file)
        self.assertIsNone(root)

    def test_parse_non_existent_file(self):
        # Suppress print output
        # import io
        # from contextlib import redirect_stderr
        # f = io.StringIO()
        # with redirect_stderr(f):
        #    root = parse_xml(self.non_existent_file)
        # self.assertIsNone(root)
        # self.assertIn("Error: XML file not found", f.getvalue())

        root = parse_xml(self.non_existent_file)
        self.assertIsNone(root)

if __name__ == '__main__':
    # This allows running the tests directly
    # For integration with a test runner, this might not be necessary
    # or could be structured differently.

    # A common way to ensure src is discoverable if running tests/test_xml_parser.py directly:
    import sys
    if os.path.join(os.getcwd(), 'src') not in sys.path and os.path.join(os.getcwd(), '..', 'src') not in sys.path :
        # This attempts to add the 'src' directory to sys.path
        # It assumes the script is run from 'tests' directory or the root project directory
        # For `python -m unittest discover tests` from root, src should be importable.
        # For `python tests/test_xml_parser.py` from root, src should be importable.
        # If running `python test_xml_parser.py` from `tests` dir, need to add '../src'
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        src_path = os.path.join(project_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        # Re-check import after path modification, though it's usually done at module level
        global parse_xml
        from xml_parser import parse_xml


    unittest.main()
