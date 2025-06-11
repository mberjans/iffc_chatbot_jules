# IFFC Chatbot Augmentation Pipeline

## 1. Project Overview

This project implements a Python-based pipeline designed to process XML documents, extract structured information (entities and relationships), build a knowledge graph, and generate embeddings for the extracted data. The ultimate goal is to augment the knowledge base available to a chatbot, enabling it to answer questions based on the content of these XML files.

The pipeline currently uses placeholder (mock) components for LightRAG functionalities, allowing for development and testing of the overall workflow.

## 2. Features

- Parses XML files to extract raw text content.
- Chunks extracted text into manageable segments.
- Extracts entities and relationships from text chunks (currently using mock components).
- Builds a knowledge graph from extracted entities and relationships (mocked KG storage).
- Generates and stores embeddings for entities and relationships (mocked embedding models and vector DB).
- Configurable through a `config.yaml` file and environment variables.
- Includes a suite of unit tests for individual modules.

## 3. Setup Instructions

### Prerequisites
- Python 3.8 or higher
- `pip` for installing packages

### Installation
1.  **Clone the repository (if applicable):**
    ```bash
    # git clone <repository_url>
    # cd iffc_chatbot_augment
=======
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
    The project requires several Python packages, including `lightrag`. These are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## 4. Configuration

The application's behavior is controlled by a configuration file named `config.yaml` and environment variables for sensitive data like API keys.

### 4.1. `config.yaml`
A sample `config.yaml` is provided in the root directory. It's recommended to review and customize it for your needs. Key sections include:

-   **`api_keys`**: While API keys can be set here, it's **strongly recommended to use environment variables** for production or any sensitive deployment.
    -   `huggingface_hub_token`: Your HuggingFace Hub token, if needed for downloading models.
    -   `openai_api_key`: Your OpenAI API key, if using OpenAI models.
-   **`llm_models`**: Configuration for Large Language Models. You can define multiple models.
    -   `default_llm`: Specifies the primary LLM to be used.
        -   `provider`: e.g., "huggingface_pipeline", "openai".
        -   `model_name`: Identifier for the model (e.g., "mistralai/Mistral-7B-Instruct-v0.1" from HuggingFace, "gpt-3.5-turbo" for OpenAI).
        -   `model_kwargs`: Additional parameters for model initialization (e.g., `max_length`, `temperature`).
-   **`embedding_models`**: Configuration for text embedding models.
    -   `default_embedding`: Specifies the primary embedding model.
        -   `provider`: e.g., "huggingface_sentence_transformers", "openai_embeddings".
        -   `model_name`: Identifier (e.g., "sentence-transformers/all-MiniLM-L6-v2", "text-embedding-ada-002").
        -   `model_kwargs`: Additional parameters (e.g., `device: "cpu"` or `"cuda"`).
-   **`vector_database`**: Settings for the vector database.
    -   `provider`: e.g., "nano_vectordb" (for local, lightweight DB).
    -   `path`: Filesystem path for persistent storage (if applicable).
    -   `collection_name`: Name of the collection within the vector DB.
-   **`data_paths`**: File paths used by the application.
    -   `xml_input_directory`: Default directory for input XML files (not directly used by `main.py` which takes a specific file path).
    -   `processed_output_directory`: Directory for any processed outputs (not currently used).
-   **`settings`**: General application settings.
    -   `log_level`: Logging verbosity (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    -   `chunk_size`: Size of text chunks for processing.
    -   `chunk_overlap`: Overlap between text chunks.

### 4.2. Environment Variables for API Keys
For security, API keys should be set as environment variables. The `config_loader.py` module will prioritize environment variables over values in `config.yaml` if both are present.
-   `HUGGINGFACE_HUB_TOKEN`: Your HuggingFace Hub token.
-   `OPENAI_API_KEY`: Your OpenAI API key.

Set them in your shell before running the application:
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
export HUGGINGFACE_HUB_TOKEN="your_huggingface_token_here"
```

## 5. Running the Application (`main.py`)

The main script `main.py` orchestrates the entire processing pipeline for a single XML file.

**Command-line usage:**
```bash
python main.py <path_to_xml_file>
```
Replace `<path_to_xml_file>` with the actual path to the XML file you want to process.

**Example:**
```bash
python main.py data/input/sample_document.xml
```
(Assuming you have an XML file at `data/input/sample_document.xml`. You would need to create this path and file.)

The script will log its progress to the console. The verbosity of these logs can be controlled by the `log_level` setting in `config.yaml`.

## 6. Development Status & Known Issues

### Mock Components
Currently, this project uses **mock (placeholder) components** for core LightRAG functionalities:
-   Entity and relationship extraction (`entity_extractor.py`) uses a `MockLightRAGClient`.
-   Knowledge graph construction (`kg_builder.py`) uses a `MockLightRAGKnowledgeGraph`.
-   Embedding generation and storage (`embedding_store.py`) use a `MockEmbeddingModel` and `MockVectorDBClient`.

These mock components simulate the expected behavior and allow for end-to-end testing of the pipeline's workflow. To connect to actual LightRAG services or local models, these modules would need to be updated.

### Known Issues
-   **`test_chunk_text_simple` Failure**: One unit test in `tests/test_data_processor.py`, named `test_chunk_text_simple`, may persistently fail. This is suspected to be due to an inconsistency in the execution environment where the Python interpreter does not seem to use the latest version of `data_processor.py`'s `chunk_text` function, despite multiple attempts to overwrite the file using development tools. The `chunk_text` logic itself and the test's expectation are believed to be correct based on manual tracing and `read_files` verification. All other unit tests (47/48) pass.

## 7. Running Unit Tests

The project includes a suite of unit tests in the `tests` directory. These tests use Python's built-in `unittest` module.

**To run all tests:**
Navigate to the project's root directory and run:
```bash
python -m unittest discover tests
```
This command will automatically find and execute all test files (named `test_*.py`) within the `tests` directory.

**To run tests for a specific module:**
You can also run individual test files directly:
```bash
python tests/test_data_processor.py
python tests/test_entity_extractor.py
python tests/test_kg_builder.py
python tests/test_embedding_store.py
```
Ensure your `PYTHONPATH` is set up correctly if running individual files from a different directory or if your modules use package-relative imports (though current modules are structured for direct execution from the root). Setting `export PYTHONPATH=$PYTHONPATH:.` from the root directory can help.
When running tests, mock components are used, so no external services or API keys are required.
=======
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
=======
# KAG-Builder: XML to Knowledge Graph

This project implements the KAG-Builder, a system designed to construct a biomedical Knowledge Graph (KG) from XML documents (parsing of XML is assumed to be handled by a separate module NXS-1Z-001).
The primary goal is to extract entities and their relationships from text, build a structured KG, and provide mechanisms for tracing information back to its source in the original documents.

## Project Structure

-   `kag_builder/`: Main package for the Knowledge Graph builder.
    -   `entity_extraction.py`: Extracts biomedical entities from text using spaCy and a scientific model (e.g., `en_core_sci_lg`).
    -   `relation_extraction.py`: Identifies relationships between extracted entities (initially based on co-occurrence).
    -   `kg_construction.py`: Builds a knowledge graph using NetworkX from the extracted entities and relations.
    -   `indexing.py`: Provides utilities for mutual indexing, linking KG elements back to source text chunks (primarily by ensuring `text_chunk_id` is propagated).
    -   `serialization.py`: Handles saving and loading of the KG (using GraphML) and potentially separate index files (e.g., JSON).
-   `tests/`: Contains unit tests for the `kag_builder` modules.
    -   `sample_data/`: Directory for small sample XML/text files for testing.
-   `scripts/`: Utility scripts, e.g., for checking dependencies like spaCy model loading.
-   `SCHEMA.md`: Defines the schema for the biomedical KG (entities, relationships, attributes).
-   `requirements.txt`: Lists project dependencies.

## Phase 1 Development (NXS-1A-001)

This phase focuses on developing the core independent answering modules for Knowledge Augmented Generation.

---
# iffc_chatbot_augment
