import argparse
import os
from xml_parser import parse_xml
from text_processor import chunk_text_from_xml_element
from graph_builder import GraphBuilder

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Indexing Phase: XML to Document Knowledge Graph")
    parser.add_argument("input_xml_file", help="Path to the input XML file.")
    parser.add_argument("output_graph_file", help="Path to save the constructed graph (e.g., graph.gml).")
    # Optional: Add argument for different chunking strategies or edge types in the future

    args = parser.parse_args()

    # Ensure data directory exists if not an absolute path for output
    output_dir = os.path.dirname(args.output_graph_file)
    if output_dir and not os.path.exists(output_dir) and not os.path.isabs(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # 1. Parse XML
    print(f"Parsing XML file: {args.input_xml_file}...")
    xml_root = parse_xml(args.input_xml_file)

    if xml_root is None:
        print(f"Failed to parse XML. Exiting.")
        return

    print("XML parsed successfully.")

    # Initialize graph builder
    builder = GraphBuilder()

    # 2. Process each document / relevant element in the XML
    #    This example assumes the XML has <doc> elements, and we process each one.
    #    Adjust findall criteria based on actual XML structure.
    doc_elements = xml_root.findall('doc')
    if not doc_elements:
        # Fallback: if no <doc> elements, try to process the root itself or other common structures.
        # This part might need to be more sophisticated depending on XML variability.
        # For now, if no <doc>, we can attempt to chunk the entire root if it has paragraphs.
        # Or, signal that no processable elements were found.
        print("No <doc> elements found. Attempting to process root element for paragraphs...")
        # Check if root itself can be considered a single document content holder
        # This is a simplistic fallback.
        doc_elements = [xml_root] if xml_root.find('paragraph') is not None else []
        if not doc_elements:
            print("No processable content (e.g. <doc> tags or <paragraph> tags in root) found in XML. Exiting.")
            return


    all_processed_node_ids = []
    for i, doc_element in enumerate(doc_elements):
        doc_id_attr = doc_element.get('id', f"doc_{i}")
        print(f"Processing document/element: {doc_id_attr}...")

        # 3. Chunk Text
        text_chunks = chunk_text_from_xml_element(doc_element)
        if not text_chunks:
            print(f"No text chunks found for {doc_id_attr}. Skipping.")
            continue

        print(f"Found {len(text_chunks)} text chunks for {doc_id_attr}.")

        # 4. Add Nodes
        # We could add a prefix or metadata to nodes related to their source document
        # For now, nodes are global.
        current_doc_node_ids = builder.add_nodes_from_text_chunks(text_chunks)
        print(f"Added {len(current_doc_node_ids)} nodes for {doc_id_attr}.")

        # 5. Add Edges (sequentially within the current document's chunks)
        builder.add_sequential_edges(current_doc_node_ids)
        print(f"Added sequential edges for {doc_id_attr}.")
        all_processed_node_ids.extend(current_doc_node_ids)

    if not builder.get_graph().nodes():
        print("No nodes were added to the graph. Exiting.")
        return

    # 6. Save Graph
    print(f"Saving graph to {args.output_graph_file}...")
    builder.save_graph_gml(args.output_graph_file)
    print("Graph construction complete.")

    # Example of how to run from command line:
    # First, create a dummy data/input.xml:
    # <root>
    #   <doc id="1">
    #     <title>Document 1</title>
    #     <paragraph>This is paragraph one of doc one.</paragraph>
    #     <paragraph>This is paragraph two of doc one.</paragraph>
    #   </doc>
    #   <doc id="2">
    #     <title>Document 2</title>
    #     <paragraph>This is a paragraph in doc two.</paragraph>
    #   </doc>
    # </root>
    # Then run:
    # python src/main.py data/input.xml data/output_graph.gml

if __name__ == '__main__':
    # Create dummy data for testing if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    dummy_xml_path = "data/sample_input.xml"
    if not os.path.exists(dummy_xml_path):
        dummy_xml_content = """
<root>
    <doc id="doc1">
        <title>Sample Document One</title>
        <paragraph>This is the first paragraph of the first sample document.</paragraph>
        <paragraph>This is the second paragraph, providing more details and context for document one.</paragraph>
    </doc>
    <doc id="doc2">
        <title>Sample Document Two</title>
        <paragraph>Document two starts with this opening paragraph.</paragraph>
        <paragraph>It continues with another paragraph, discussing different topics.</paragraph>
        <paragraph>A final short paragraph for document two.</paragraph>
    </doc>
    <doc id="doc3_empty">
        <title>Empty Document</title>
    </doc>
    <misc>
        <paragraph>This paragraph is not in a doc tag.</paragraph>
    </misc>
</root>
        """
        with open(dummy_xml_path, "w") as f:
            f.write(dummy_xml_content)
        print(f"Created dummy XML file: {dummy_xml_path}")

    # To run the main function as if called from CLI with arguments:
    # You would typically run this script from the project root directory.
    # e.g., python src/main.py data/sample_input.xml data/knowledge_graph.gml

    # The following is for easy execution during development/testing from within an IDE
    # or by directly running `python src/main.py`
    # Note: This direct call to main() will fail if sys.argv doesn't match expectations.
    # It's better to run via command line as intended.

    # To make it runnable directly for a quick test:
    # import sys
    # sys.argv = ['src/main.py', dummy_xml_path, 'data/output_graph.gml']

    main()
