import os
import requests

def download_pubmed_xml(pubmed_id: str, output_path: str = ".") -> str:
  """Downloads the PubMed XML for a given PubMed ID using NCBI E-utilities.

  Constructs a URL to fetch the XML data from NCBI, makes a GET request,
  checks for errors, and then saves the XML content to a specified file.

  Args:
    pubmed_id (str): The PubMed ID (PMID) of the article to download.
    output_path (str, optional): The directory where the XML file will be saved.
      Defaults to the current working directory (".").

  Returns:
    str: The full path to the saved XML file (e.g., "output_dir/12345.xml").

  Raises:
    requests.exceptions.RequestException: If there's an issue with the network
      request (e.g., DNS failure, connection refused).
    ValueError: If the NCBI API returns an error (e.g., invalid PubMed ID,
      API rate limits exceeded leading to non-200 status).
    IOError: If there's an error writing the XML file to disk.
  """
  # Construct the E-utilities URL for fetching PubMed articles in XML format.
  # Base URL for NCBI's EFetch utility
  base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
  # Parameters for the request:
  # - db=pubmed: Specifies the database to search (PubMed).
  # - id=pubmed_id: The specific PubMed ID of the article.
  # - rettype=xml: Requests the data in XML format.
  params = {
      "db": "pubmed",
      "id": pubmed_id,
      "rettype": "xml",
  }
  url = f"{base_url}?db={params['db']}&id={params['id']}&rettype={params['rettype']}"

  try:
    # Make the HTTP GET request
    response = requests.get(url)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
  except requests.exceptions.RequestException as e:
    print(f"Error downloading PubMed ID {pubmed_id}: {e}")
    raise

  if response.status_code != 200:
    # This check is largely redundant if response.raise_for_status() is used above,
    # as raise_for_status() will throw an HTTPError for non-200 codes.
    # However, it's kept here as a fallback or for cases where raise_for_status might be removed
    # or if more specific non-200 handling (that doesn't raise an exception) was desired before this point.
    error_message = f"Error fetching PubMed ID {pubmed_id}. Status code: {response.status_code}. Check if the ID is valid or if there's an API issue."
    print(error_message)
    raise ValueError(error_message)

  # Check for <ERROR> tag in response text even if status is 200
  # NCBI often returns 200 OK but with an error message in the XML body for invalid IDs.
  if "<ERROR>" in response.text and "</ERROR>" in response.text:
    # Try to extract the error message for better feedback
    try:
      error_content = response.text.split("<ERROR>")[1].split("</ERROR>")[0]
      detailed_error_message = f"NCBI API returned an error for PubMed ID {pubmed_id}: {error_content}"
    except IndexError:
      detailed_error_message = f"NCBI API returned an error for PubMed ID {pubmed_id}, and it contains an <ERROR> tag."
    print(detailed_error_message)
    raise ValueError(detailed_error_message)

  # Construct the filename (e.g., "12345.xml")
  filename = f"{pubmed_id}.xml"
  # Create the full path including the output directory
  full_output_path = os.path.join(output_path, filename)

  # Ensure the output directory exists.
  # If output_path is specified (not empty) and doesn't exist, create it.
  # exist_ok=True prevents an error if the directory already exists.
  if output_path and not os.path.exists(output_path):
    os.makedirs(output_path, exist_ok=True)

  # Write the XML content to the file using UTF-8 encoding
  try:
    with open(full_output_path, "w", encoding="utf-8") as f:
      f.write(response.text)
  except IOError as e:
    # Handle potential file writing errors (e.g., disk full, permissions)
    print(f"Error writing XML file to {full_output_path}: {e}")
    # Re-raise the exception to allow the caller to handle it
    raise

  return full_output_path
