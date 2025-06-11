import pubmed_parser

class PubMedXMLParser:
    """
    Parses PubMed XML files to extract metadata, full text, and article sections.

    Attributes:
        xml_file_path (str): The path to the PubMed XML file.
        parsed_data (dict): A dictionary to store the extracted data.
                            Keys include 'pmid', 'title', 'authors', 'journal',
                            'publication_date', 'keywords', 'full_text', and 'sections'.
    """
    def __init__(self, xml_file_path):
        """
        Initializes the PubMedXMLParser with the path to an XML file.

        Args:
            xml_file_path (str): The file path of the PubMed XML document to be parsed.
        """
        self.xml_file_path = xml_file_path
        self.parsed_data = {}  # Initialize container for parsed data

    def extract_metadata(self):
        """
        Extracts metadata from the XML file and stores it in self.parsed_data.

        Metadata includes PMID, title, authors (with affiliations), journal,
        publication date, and keywords. Handles missing fields gracefully by
        assigning None or empty lists.
        """
        try:
            # The pubmed_parser library is used to parse the main XML structure.
            parsed_xml = pubmed_parser.parse_pubmed_xml(self.xml_file_path)

            self.parsed_data['pmid'] = parsed_xml.get('pmid', None)
            self.parsed_data['title'] = parsed_xml.get('title', None)

            authors_list = []
            for author in parsed_xml.get('authors', []):
                authors_list.append({
                    'name': author.get('name', None),
                    'affiliation': author.get('affiliation', None)
                })
            self.parsed_data['authors'] = authors_list

            self.parsed_data['journal'] = parsed_xml.get('journal', None)
            self.parsed_data['publication_date'] = parsed_xml.get('publication_date', None)
            self.parsed_data['keywords'] = parsed_xml.get('keywords', [])

        except FileNotFoundError:
            print(f"Error: XML file not found at {self.xml_file_path}")
            self.parsed_data['pmid'] = None
        except Exception as e:
            print(f"Error parsing XML metadata: {e}")
            # Initialize with None or empty lists if parsing fails or specific fields are missing
            self.parsed_data['pmid'] = None
            self.parsed_data['title'] = None
            self.parsed_data['authors'] = []
            self.parsed_data['journal'] = None
            self.parsed_data['publication_date'] = None
            self.parsed_data['keywords'] = []

    def extract_full_text(self):
        """
        Extracts the full text from the XML file and stores it in self.parsed_data['full_text'].

        Uses pubmed_parser.parse_pubmed_paragraph to get paragraph data, which is then
        joined to form the full text. Handles errors and missing text by setting
        'full_text' to None.
        """
        try:
            # parse_pubmed_paragraph is used here, assuming paragraphs make up the bulk of full text.
            # The text from each paragraph object is extracted and joined.
            paragraphs = pubmed_parser.parse_pubmed_paragraph(self.xml_file_path)
            full_text = "\n".join([para.get('text', '') for para in paragraphs if para.get('text')])
            self.parsed_data['full_text'] = full_text if full_text else None # Store None if no text found

        except FileNotFoundError:
            print(f"Error: XML file not found at {self.xml_file_path} during full text extraction.")
            self.parsed_data['full_text'] = None
        except Exception as e:
            print(f"Error extracting full text: {e}") # Log other potential errors
            self.parsed_data['full_text'] = None

    def extract_sections(self):
        """
        Extracts distinct sections (e.g., Introduction, Methods, Results, Conclusion)
        from the XML file and stores them in self.parsed_data['sections'].

        Each section is stored as a dictionary with 'heading' and 'text'.
        Uses pubmed_parser.parse_pubmed_paragraph and groups paragraphs by their 'label'
        attribute, which often corresponds to section headings. Handles cases where
        sections are missing or not clearly demarcated.
        """
        try:
            # Uses paragraph data, grouping by 'label' which often indicates section titles.
            paragraphs = pubmed_parser.parse_pubmed_paragraph(self.xml_file_path)
            sections = []
            current_section = None  # Holds the section currently being aggregated

            for para in paragraphs:
                heading = para.get('label', None)  # 'label' usually contains the section heading.
                text = para.get('text', '').strip() # Get paragraph text, remove leading/trailing whitespace.

                if not text:  # Skip paragraphs with no actual text content.
                    continue

                if heading:
                    # A new heading indicates a new section.
                    # First, if a current_section is being built and has text, save it.
                    if current_section and current_section['text']:
                        sections.append(current_section)
                    # Then, start a new section with the new heading.
                    current_section = {'heading': heading, 'text': text}
                elif current_section:
                    # If there's no new heading, append this paragraph's text to the ongoing section.
                    current_section['text'] += "\n" + text
                else:
                    # This case handles text that appears before any recognized section heading (e.g., an abstract).
                    # It's stored as a section with a placeholder heading.
                    sections.append({'heading': 'Unknown/Abstract', 'text': text})

            # After the loop, ensure the last aggregated section is added.
            if current_section and current_section['text']:
                sections.append(current_section)

            self.parsed_data['sections'] = sections if sections else [] # Store empty list if no sections found

        except FileNotFoundError:
            print(f"Error: XML file not found at {self.xml_file_path} during section extraction.")
            self.parsed_data['sections'] = []
        except Exception as e:
            print(f"Error extracting sections: {e}") # Log other potential errors
            self.parsed_data['sections'] = []

    def get_parsed_data(self):
        """
        Returns the dictionary containing all parsed data.

        Returns:
            dict: The self.parsed_data dictionary with extracted information.
        """
        return self.parsed_data
