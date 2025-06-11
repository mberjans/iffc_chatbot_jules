import xml.etree.ElementTree as ET

def parse_xml(file_path):
    """
    Parses an XML file and returns the root element.

    Args:
        file_path (str): The path to the XML file.

    Returns:
        xml.etree.ElementTree.Element: The root element of the parsed XML tree.
                                      Returns None if parsing fails.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return root
    except ET.ParseError as e:
        print(f"Error parsing XML file {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"Error: XML file not found at {file_path}")
        return None

if __name__ == '__main__':
    # This is an example of how to use the parser
    # Create a dummy XML file for testing
    dummy_xml_content = """
    <root>
        <doc id="1">
            <title>Document 1</title>
            <paragraph>This is the first paragraph of document 1.</paragraph>
            <paragraph>This is the second paragraph of document 1.</paragraph>
        </doc>
        <doc id="2">
            <title>Document 2</title>
            <paragraph>This is a paragraph in document 2.</paragraph>
        </doc>
    </root>
    """
    dummy_file_path = "dummy_test.xml"
    with open(dummy_file_path, "w") as f:
        f.write(dummy_xml_content)

    parsed_root = parse_xml(dummy_file_path)
    if parsed_root:
        print(f"Successfully parsed {dummy_file_path}")
        for doc_element in parsed_root.findall('doc'):
            title = doc_element.find('title').text
            print(f"Document Title: {title}")
            for para_element in doc_element.findall('paragraph'):
                print(f"  Paragraph: {para_element.text}")

    # Clean up the dummy file
    import os
    os.remove(dummy_file_path)
