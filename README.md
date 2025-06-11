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