# GraphRAG XML Indexing Pipeline

This project implements the indexing phase of a Graph-based Retrieval Augmented Generation (GraphRAG) system. It processes XML files, extracts text content, chunks it, and builds a knowledge graph representation where nodes are text chunks and edges represent relationships between them (currently, sequential relationships). The graph is then serialized to a GML file.

## Project Structure

```
.
├── data/                  # Directory for input XML files and output graphs
│   └── sample_input.xml   # Auto-generated sample XML if not present
├── src/                   # Source code
│   ├── xml_parser.py      # Handles XML parsing
│   ├── text_processor.py  # Handles text extraction and chunking
│   ├── graph_builder.py   # Handles graph creation (nodes, edges) and serialization
│   └── main.py            # Main script to run the indexing pipeline
├── tests/                 # Unit tests
│   ├── test_xml_parser.py
│   ├── test_text_processor.py
│   └── test_graph_builder.py
├── .gitignore
├── README.md
└── requirements.txt       # Python dependencies
```

## Features

-   Parses XML files to extract content.
-   Chunks text based on `<paragraph>` tags within `<doc>` elements (or root if no `<doc>` tags).
-   Builds a directed graph using NetworkX:
    -   Nodes represent text chunks.
    -   Edges represent sequential relationships between chunks.
-   Serializes the graph to GML (Graph Modeling Language) format.
-   Includes unit tests for core components.

## Prerequisites

-   Python 3.7+
-   Pip (Python package installer)

## Setup

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd <repository_directory>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install `networkx`.

## Usage

The main script `src/main.py` is used to run the indexing pipeline.

### Running the Pipeline

Execute `main.py` from the **root directory** of the project, providing the path to your input XML file and the desired path for the output graph file.

```bash
python src/main.py <path_to_input_xml> <path_to_output_gml>
```

**Example:**

1.  Ensure you have an XML file. You can use the auto-generated sample or create your own.
    The `main.py` script will create a `data/sample_input.xml` if it doesn't find it when run directly (primarily for testing purposes through `if __name__ == '__main__'`, not when run with arguments as below). For a clean run, place your XML in the `data` directory (e.g., `data/my_document.xml`).

    Example `data/my_document.xml`:
    ```xml
    <root>
        <doc id="doc1">
            <title>My First Document</title>
            <paragraph>This is the first paragraph of my document.</paragraph>
            <paragraph>This is the second paragraph, continuing the narrative.</paragraph>
        </doc>
        <doc id="doc2">
            <title>Another Document</title>
            <paragraph>This document contains different information.</paragraph>
        </doc>
    </root>
    ```

2.  Run the indexing script:
    ```bash
    python src/main.py data/my_document.xml data/knowledge_graph.gml
    ```

3.  This will:
    -   Parse `data/my_document.xml`.
    -   Create text chunks from the paragraphs.
    -   Build a graph with these chunks as nodes and sequential edges.
    -   Save the resulting graph to `data/knowledge_graph.gml`.

### Output

-   A GML file (e.g., `data/knowledge_graph.gml`) representing the constructed knowledge graph. This file can be inspected or used in subsequent GraphRAG phases.
-   Console output indicating the progress of parsing, chunking, and graph building.

## Running Tests

To run the unit tests, navigate to the root directory of the project and use the following command:

```bash
python -m unittest discover tests
```
This will automatically discover and run all tests within the `tests` directory.

## Future Enhancements (Optional based on Issue NXS-1B-001)

-   **More sophisticated text chunking:** Implement sentence-level chunking or other strategies.
-   **Advanced edge creation:**
    -   Semantic similarity edges using text embeddings.
    -   Co-occurrence based edges.
-   **Community detection:** Identify and label communities within the graph.
-   **Community summarization:** Use LLMs to summarize detected communities.
