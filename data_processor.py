import xml.etree.ElementTree as ET
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_xml_file(file_path: str) -> str:
    """
    Parses an XML file and extracts all text content.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        str: The extracted text content, or an empty string if an error occurs.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        text_content = []
        for element in root.iter():
            if element.text and element.text.strip():
                text_content.append(element.text.strip())
            if element.tail and element.tail.strip(): # Also capture text in element tails
                text_content.append(element.tail.strip())
        return " ".join(filter(None, text_content)) # Filter out potential empty strings if strip results in empty
    except ET.ParseError as e:
        logging.error(f"Error parsing XML file {file_path}: {e}")
        return ""
    except FileNotFoundError:
        logging.error(f"XML file not found: {file_path}")
        return ""
    except Exception as e:
        logging.error(f"An unexpected error occurred while parsing {file_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int, overlap: int = 0) -> list[str]:
    """
    Splits text into chunks of a specified size with a given overlap.
    The stride (step size) is chunk_size - overlap.
    """
    if not text:
        logging.warning("Attempted to chunk empty text.")
        return []
    if chunk_size <= 0:
        logging.error("Chunk size must be a positive integer.")
        raise ValueError("Chunk size must be a positive integer.")
    if overlap < 0:
        logging.error("Overlap must be a non-negative integer.")
        raise ValueError("Overlap must be a non-negative integer.")
    if overlap >= chunk_size:
        logging.error("Overlap cannot be greater than or equal to chunk size.")
        raise ValueError("Overlap cannot be greater than or equal to chunk size.")

    chunks = []
    start = 0
    while start < len(text):
        actual_end = min(start + chunk_size, len(text))
        chunks.append(text[start:actual_end])
        start += (chunk_size - overlap)
    return chunks

if __name__ == '__main__':
    # Example Usage (optional, for testing purposes)
    logging.basicConfig(level=logging.DEBUG) # Enable debug for local testing
    logging.info("Starting example usage of data_processor module.")

    # Create a dummy XML file for testing
    dummy_xml_content = """
    <root>
        <doc>
            <title>Document 1 Title</title>
            <paragraph>This is the first paragraph of document 1. It contains some text.</paragraph>
            <paragraph>This is another paragraph. It provides more information.</paragraph>
        </doc>
        <doc>
            <title>Document 2 Title</title>
            <section>
                <heading>Section 1</heading>
                <content>Content of section 1.</content>
            </section>
            <section>
                <heading>Section 2</heading>
                <item>Item A</item>
                <item>Item B</item>
            </section>
            <sometail>text in tail</sometail>after tail text.
        </doc>
    </root>
    """
    dummy_xml_file = "dummy_example.xml"
    with open(dummy_xml_file, "w", encoding="utf-8") as f:
        f.write(dummy_xml_content)
    logging.info(f"Created dummy XML file: {dummy_xml_file}")

    # Test XML parsing
    extracted_text = parse_xml_file(dummy_xml_file)
    if extracted_text:
        logging.info(f"Successfully extracted text: '{extracted_text}'")
    else:
        logging.warning("No text extracted or error occurred during parsing.")

    # Test text chunking
    sample_text_for_chunking = "This is a sample text for chunking."
    logging.info(f"Chunking sample text: '{sample_text_for_chunking}'")
    test_chunks = chunk_text(sample_text_for_chunking, chunk_size=10, overlap=3)
    logging.info(f"Test chunks: {test_chunks}")
    # Expected: ['This is a ', ' sample t', 'ext for ch', 'unking.', 'chunking.', 'g.']

    # Test with non-existent file
    logging.info("Testing with a non-existent XML file.")
    parse_xml_file("non_existent_file.xml")

    # Test chunking with invalid parameters
    logging.info("Testing chunk_text with invalid parameters.")
    try:
        chunk_text("Some sample text.", chunk_size=0, overlap=0)
    except ValueError as e:
        logging.error(f"Caught expected error for chunk_size=0: {e}")
    try:
        chunk_text("Some sample text.", chunk_size=10, overlap=-1)
    except ValueError as e:
        logging.error(f"Caught expected error for overlap=-1: {e}")
    try:
        chunk_text("Some sample text.", chunk_size=10, overlap=10)
    except ValueError as e:
        logging.error(f"Caught expected error for overlap >= chunk_size: {e}")

    logging.info("Example usage finished.")
