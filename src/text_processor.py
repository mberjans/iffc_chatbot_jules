from xml.etree.ElementTree import Element

def chunk_text_from_xml_element(xml_element: Element) -> list[str]:
    """
    Extracts text from an XML element and chunks it.
    Currently, it assumes 'paragraph' tags contain the text to be chunked.
    Each paragraph's text becomes a separate chunk.

    Args:
        xml_element (xml.etree.ElementTree.Element): The XML element to process.
                                                    Typically a 'doc' element.

    Returns:
        list[str]: A list of text chunks.
    """
    chunks = []
    if xml_element is None:
        return chunks

    for paragraph_element in xml_element.findall('paragraph'):
        if paragraph_element.text:
            chunks.append(paragraph_element.text.strip())
    return chunks

if __name__ == '__main__':
    # Example usage with a dummy XML structure
    from xml.etree.ElementTree import fromstring

    dummy_doc_xml = """
    <doc id="1">
        <title>Document 1</title>
        <paragraph>This is the first paragraph. It contains sentences.</paragraph>
        <paragraph>  This is the second paragraph, with leading/trailing spaces.  </paragraph>
        <paragraph></paragraph>
        <paragraph>A third paragraph here.</paragraph>
    </doc>
    """
    doc_element = fromstring(dummy_doc_xml)

    text_chunks = chunk_text_from_xml_element(doc_element)
    print("Text chunks:")
    for i, chunk in enumerate(text_chunks):
        print(f"{i+1}: '{chunk}'")

    # Example with an element that is None
    none_chunks = chunk_text_from_xml_element(None)
    print(f"\nChunks from None element: {none_chunks}")

    # Example with an element that has no paragraph tags
    dummy_nopara_xml = """
    <doc id="2">
        <title>Document without paragraphs</title>
        <content>Some other content</content>
    </doc>
    """
    nopara_element = fromstring(dummy_nopara_xml)
    nopara_chunks = chunk_text_from_xml_element(nopara_element)
    print(f"\nChunks from element with no paragraphs: {nopara_chunks}")
