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
            # Using medline_parser for metadata
            article_iterator = pubmed_parser.medline_parser.parse_medline_xml(
                self.xml_file_path,
                year_info_only=False,
                author_list=True
            )
            # parse_medline_xml returns an iterator; get the first (and only) article
            parsed_article = next(article_iterator, None)
            # print(f"DEBUG: parsed_article from medline_parser: {parsed_article}") # DEBUG line

            if parsed_article:
                # print(f"DEBUG: article keys: {parsed_article.keys()}") # DEBUG line
                self.parsed_data['pmid'] = parsed_article.get('pmid', None)
                self.parsed_data['title'] = parsed_article.get('title', None)
                # Authors are expected to be a list of dicts with 'name' and 'affiliation'
                # The actual structure from parse_medline_xml with author_list=True needs to be verified.
                # Assuming it returns a list of strings or dicts that might need transformation.
                # For now, let's assign it directly and adjust based on test output.
                raw_authors = parsed_article.get('authors', [])
                if raw_authors and isinstance(raw_authors, list):
                    # Placeholder: actual author parsing might be more complex
                    # This assumes authors are dicts with 'last_name', 'first_name', 'affiliation'
                    self.parsed_data['authors'] = [
                        {'name': f"{a.get('last_name', '')}, {a.get('first_name', '')}".strip(', '),
                         'affiliation': a.get('affiliation', None)}
                        for a in raw_authors
                    ] # This is a guess, might need adjustment
                else:
                     self.parsed_data['authors'] = []

                self.parsed_data['journal'] = parsed_article.get('journal', None)
                # 'pubdate' from the library might be YYYY-MM-DD or YYYY-MM or YYYY
                self.parsed_data['publication_date'] = parsed_article.get('pubdate', None)
                self.parsed_data['keywords'] = parsed_article.get('mesh_terms', "").split('; ') if parsed_article.get('mesh_terms') else []
                # Abstract is often part of medline data
                self.parsed_data['abstract'] = parsed_article.get('abstract', None)
            else:
                # Initialize with None or empty lists if parsing fails or fields are missing
                self.parsed_data['pmid'] = None
                self.parsed_data['title'] = None
                self.parsed_data['authors'] = []
                self.parsed_data['journal'] = None
                self.parsed_data['publication_date'] = None
                self.parsed_data['keywords'] = []
                self.parsed_data['abstract'] = None

        except FileNotFoundError:
            print(f"Error: XML file not found at {self.xml_file_path}")
            self.parsed_data['pmid'] = None
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
            # Using pubmed_oa_parser.parse_pubmed_paragraph for full text
            paragraph_list = pubmed_parser.pubmed_oa_parser.parse_pubmed_paragraph(
                self.xml_file_path,
                all_paragraph=True
            )
            if paragraph_list:
                full_text_parts = [para.get('text', '') for para in paragraph_list if para.get('text')]
                self.parsed_data['full_text'] = "\n".join(full_text_parts).strip() if full_text_parts else None
            else:
                self.parsed_data['full_text'] = None
                # If no paragraphs, try to get abstract as fallback, if available from metadata
                if 'abstract' in self.parsed_data and self.parsed_data['abstract']:
                    self.parsed_data['full_text'] = self.parsed_data['abstract']


        except FileNotFoundError:
            print(f"Error: XML file not found at {self.xml_file_path} during full text extraction.")
            # Ensure abstract from metadata is used as fallback if available
            if 'abstract' in self.parsed_data and self.parsed_data['abstract']:
                 self.parsed_data['full_text'] = self.parsed_data['abstract']
            else:
                 self.parsed_data['full_text'] = None
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
            # Using pubmed_oa_parser.parse_pubmed_paragraph for sections
            paragraph_list = pubmed_parser.pubmed_oa_parser.parse_pubmed_paragraph(
                self.xml_file_path,
                all_paragraph=True
            )
            sections_dict = {} # Use a dictionary to group paragraphs by section heading

            if paragraph_list:
                for para in paragraph_list:
                    heading = para.get('section', 'Unknown/Abstract') # Default heading if not specified
                    text = para.get('text', '').strip()
                    if not text:
                        continue

                    if heading in sections_dict:
                        sections_dict[heading] += "\n" + text
                    else:
                        sections_dict[heading] = text

                self.parsed_data['sections'] = [{'heading': h, 'text': t} for h, t in sections_dict.items()]
            else:
                self.parsed_data['sections'] = []
                # Fallback for sections: if abstract is available, create a section for it.
                if 'abstract' in self.parsed_data and self.parsed_data['abstract']:
                    self.parsed_data['sections'].append({'heading': 'Abstract', 'text': self.parsed_data['abstract']})


        except FileNotFoundError:
            print(f"Error: XML file not found at {self.xml_file_path} during section extraction.")
            # Fallback for sections if file not found
            if 'abstract' in self.parsed_data and self.parsed_data['abstract']:
                 self.parsed_data['sections'] = [{'heading': 'Abstract', 'text': self.parsed_data['abstract']}]
            else:
                 self.parsed_data['sections'] = []
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
