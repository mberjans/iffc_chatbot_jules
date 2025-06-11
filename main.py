import argparse
import logging
import sys
import os

# Attempt to import project modules
try:
    from config_loader import get_config, AppConfig
    from data_processor import parse_xml_file, chunk_text
    from entity_extractor import extract_entities_and_relationships, Entity, Relationship
    from kg_builder import build_or_update_graph
    from embedding_store import store_embeddings
except ImportError as e:
    # Simple fallback for path if modules are not found directly (e.g. running from a subdir)
    # In a real project, better PYTHONPATH setup or packaging is needed.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    from config_loader import get_config, AppConfig
    from data_processor import parse_xml_file, chunk_text
    from entity_extractor import extract_entities_and_relationships, Entity, Relationship
    from kg_builder import build_or_update_graph
    from embedding_store import store_embeddings


# Initialize a logger for the main script
logger = logging.getLogger(__name__) # Using __name__ is conventional

def setup_logging(log_level_str: str = "INFO"):
    """Configures root logger based on string level."""
    numeric_level = getattr(logging, log_level_str.upper(), None)
    if not isinstance(numeric_level, int):
        logging.warning(f"Invalid log level: {log_level_str}. Defaulting to INFO.")
        numeric_level = logging.INFO

    # Configure the root logger
    # BasicConfig should ideally be called once. If config_loader also calls it,
    # subsequent calls might be ignored or behave unexpectedly depending on Python version/setup.
    # For robustness, let's try to set the level on the root logger directly if already configured.
    if logging.getLogger().handlers: # Check if root logger has handlers (already configured)
        logging.getLogger().setLevel(numeric_level)
        logger.info(f"Root logger level updated to {log_level_str.upper()}.")
    else: # If no handlers, it's safe to call basicConfig
        logging.basicConfig(level=numeric_level,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            handlers=[logging.StreamHandler(sys.stdout)]) # Ensure logs go to stdout
        logger.info(f"Root logger configured with level {log_level_str.upper()}.")


def main():
    # Load configuration
    try:
        config: AppConfig = get_config()
        # Setup logging based on config (get_config might have already set it if it calls load_config)
        # This call ensures it's set if get_config() returned a cached config without re-evaluating log level.
        log_level = config.get("settings", {}).get("log_level", "INFO")
        setup_logging(log_level)
        logger.debug("Configuration loaded successfully.")
    except Exception as e:
        logger.error(f"Critical error loading configuration: {e}", exc_info=True)
        sys.exit(1)

    # Command-line argument parsing
    parser = argparse.ArgumentParser(description="Process an XML file to build a knowledge graph and store embeddings.")
    parser.add_argument("xml_file_path", type=str, help="Path to the XML file to process.")
    args = parser.parse_args()

    logger.info(f"Starting processing for XML file: {args.xml_file_path}")

    # 1. Parse and Chunk XML content (Data Processor)
    try:
        logger.info("Step 1: Parsing XML file...")
        raw_text = parse_xml_file(args.xml_file_path)
        if not raw_text:
            logger.error(f"No text could be extracted from {args.xml_file_path}. Exiting.")
            sys.exit(1)
        logger.info(f"Successfully parsed XML. Extracted text length: {len(raw_text)} characters.")

        chunk_size = config.get("settings", {}).get("chunk_size", 512)
        chunk_overlap = config.get("settings", {}).get("chunk_overlap", 64)
        logger.info(f"Step 2: Chunking text with chunk_size={chunk_size}, overlap={chunk_overlap}...")
        text_chunks = chunk_text(raw_text, chunk_size=chunk_size, overlap=chunk_overlap)
        if not text_chunks:
            logger.error("No chunks were generated from the text. Exiting.")
            sys.exit(1)
        logger.info(f"Text chunked into {len(text_chunks)} chunks.")

    except Exception as e:
        logger.error(f"Error during data processing (parsing/chunking): {e}", exc_info=True)
        sys.exit(1)

    # 2. Extract Entities and Relationships (Entity Extractor)
    all_entities: list[Entity] = []
    all_relationships: list[Relationship] = []
    try:
        logger.info("Step 3: Extracting entities and relationships from chunks...")
        for i, chunk in enumerate(text_chunks):
            logger.debug(f"Processing chunk {i+1}/{len(text_chunks)}...")
            extracted_data = extract_entities_and_relationships(chunk)
            chunk_entities = extracted_data.get("entities", [])
            chunk_relationships = extracted_data.get("relationships", [])
            if chunk_entities:
                all_entities.extend(chunk_entities)
            if chunk_relationships:
                all_relationships.extend(chunk_relationships)
            logger.debug(f"Chunk {i+1}: Found {len(chunk_entities)} entities, {len(chunk_relationships)} relationships.")

        # Deduplicate entities and relationships (simple deduplication by ID)
        all_entities = list({e['id']: e for e in all_entities}.values())
        all_relationships = list({r['id']: r for r in all_relationships}.values())
        logger.info(f"Total unique entities found: {len(all_entities)}")
        logger.info(f"Total unique relationships found: {len(all_relationships)}")

    except Exception as e:
        logger.error(f"Error during entity/relationship extraction: {e}", exc_info=True)
        # Decide if to proceed with potentially partial data or exit
        # For now, let's exit if extraction fails broadly.
        sys.exit(1)

    # 3. Build Knowledge Graph (KG Builder)
    if all_entities or all_relationships: # Proceed only if there's something to add
        try:
            logger.info("Step 4: Building/updating Knowledge Graph...")
            kg_results = build_or_update_graph(entities=all_entities, relationships=all_relationships)
            logger.info(f"Knowledge Graph update results: {kg_results.get('added_nodes', [])} nodes added/updated, "
                        f"{kg_results.get('added_edges', [])} edges added/updated.")
        except Exception as e:
            logger.error(f"Error during Knowledge Graph building: {e}", exc_info=True)
            # Non-critical, can proceed to embeddings if KG build fails for some reason
    else:
        logger.info("Step 4: Skipped Knowledge Graph building as no entities or relationships were extracted.")


    # 4. Generate and Store Embeddings (Embedding Store)
    if all_entities or all_relationships:
        try:
            logger.info("Step 5: Generating and storing embeddings...")
            # Create an entities map for relationship context if needed by embedding store
            entities_map_for_embedding = {entity["id"]: entity for entity in all_entities}

            embedding_results = store_embeddings(
                entities=all_entities,
                relationships=all_relationships,
                entities_map_for_relationships=entities_map_for_embedding
            )
            logger.info(f"Embedding storage results: {embedding_results.get('entities_processed',0)} entities processed, "
                        f"{embedding_results.get('relationships_processed',0)} relationships processed.")
        except Exception as e:
            logger.error(f"Error during embedding generation/storage: {e}", exc_info=True)
    else:
        logger.info("Step 5: Skipped embedding generation as no entities or relationships were available.")

    logger.info("Processing finished.")


if __name__ == "__main__":
    # Note: The setup_logging call using config is inside main()
    # If there's an issue loading config, initial logs might use default Python logging settings.
    main()
