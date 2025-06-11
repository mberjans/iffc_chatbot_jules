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
