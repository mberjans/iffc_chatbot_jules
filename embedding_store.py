import logging
import json # For creating string representations of attributes
from typing import List, Dict, Any, Optional, Tuple, Union

# Assuming entity_extractor.py defines these, redefining for standalone creation
class Entity(Dict[str, Any]):
    id: str
    label: str
    text: str
    attributes: Optional[Dict[str, Any]]

class Relationship(Dict[str, Any]):
    id: str
    source_entity_id: str
    target_entity_id: str
    label: str
    attributes: Optional[Dict[str, Any]]
    # For relationships, we might need context from the entities it connects
    # This can be passed or fetched if the system allows
    source_entity_text: Optional[str]
    target_entity_text: Optional[str]


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Placeholder for LightRAG Embedding Model and VectorDB clients
# from lightrag.components.embedder import SomeEmbeddingModel # Example
# from lightrag.vector_store import NanoVectorDB, VectorDBConfig # Example
# from lightrag.core.types import Document # Example for items to store

class MockEmbeddingModel:
    """Mocks a text embedding model client."""
    def __init__(self, model_name: str = "mock-embedding-model"):
        self.model_name = model_name
        logging.info(f"MockEmbeddingModel initialized with model: {self.model_name}")

    def embed(self, text: str) -> List[float]:
        """Simulates generating an embedding vector for a given text."""
        if not text or not text.strip():
            logging.warning("MockEmbeddingModel: Attempted to embed empty text. Returning zero vector.")
            return [0.0] * 5 # Assuming a small embedding dimension for mock
        # Simple hash-based embedding for predictability in tests
        # In reality, this would be a call to a real model (e.g., OpenAI, SentenceTransformers)
        val = hash(text) % 1000 / 1000.0 # Normalize to [0,1)
        embedding = [val, val + 0.1, val + 0.2, val + 0.3, val + 0.4]
        logging.debug(f"MockEmbeddingModel: Embedded text '{text[:30]}...' to vector starting with {embedding[0]:.2f}")
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Simulates generating embeddings for a batch of texts."""
        return [self.embed(text) for text in texts]

class MockVectorDBClient:
    """Mocks a LightRAG Vector Database client (like nano_vectordb)."""
    def __init__(self, db_path: str = ":memory:", collection_name: str = "default_collection"):
        self.db_path = db_path
        self.collection_name = collection_name
        self._vector_store: Dict[str, Dict[str, Any]] = {} # item_id -> {text_description, vector, metadata}
        logging.info(f"MockVectorDBClient initialized for collection '{collection_name}' at path '{db_path}'")

    def add_item(self, item_id: str, text_description: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        """Simulates adding/upserting an item with its vector and metadata."""
        if not item_id:
            logging.error("MockVectorDBClient: Item ID is required to add an item.")
            raise ValueError("Item ID cannot be empty.")

        self._vector_store[item_id] = {
            "text_description": text_description,
            "vector": vector,
            "metadata": metadata or {}
        }
        logging.info(f"MockVectorDBClient: Added/updated item {item_id} in collection '{self.collection_name}'.")

    def add_items(self, items: List[Dict[str, Any]]):
        """
        Simulates adding/upserting multiple items.
        Each item dict should have 'id', 'text_description', 'vector', and optional 'metadata'.
        """
        for item in items:
            if not item.get("id") or not item.get("text_description") or not item.get("vector"):
                logging.error(f"MockVectorDBClient: Skipping item due to missing id, text_description, or vector: {item.get('id')}")
                continue
            self.add_item(
                item_id=item["id"],
                text_description=item["text_description"],
                vector=item["vector"],
                metadata=item.get("metadata")
            )

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self._vector_store.get(item_id)

    def get_collection_size(self) -> int:
        return len(self._vector_store)

# Initialize mock clients
try:
    embedding_model_client = MockEmbeddingModel()
    vector_db_client = MockVectorDBClient(collection_name="knowledge_graph_embeddings")
except Exception as e:
    logging.error(f"Failed to initialize mock clients: {e}")
    embedding_model_client = None
    vector_db_client = None

def _create_entity_description(entity: Entity) -> str:
    """Creates a textual description for an entity."""
    description = f"Entity: {entity.get('text', 'Unnamed Entity')} (Type: {entity.get('label', 'Unknown')})"
    # Check if "attributes" key exists and is not None
    if entity.get("attributes") is not None:
        attrs_str = json.dumps(entity["attributes"], sort_keys=True)
        description += f"\nAttributes: {attrs_str}"
    return description

def _create_relationship_description(relationship: Relationship, entities_map: Dict[str, Entity]) -> str:
    """Creates a textual description for a relationship, using context from connected entities."""
    source_entity_text = "Unknown Source Entity"
    target_entity_text = "Unknown Target Entity"

    source_entity = entities_map.get(relationship["source_entity_id"])
    if source_entity:
        source_entity_text = source_entity.get("text", source_entity_text)

    target_entity = entities_map.get(relationship["target_entity_id"])
    if target_entity:
        target_entity_text = target_entity.get("text", target_entity_text)

    description = (
        f"Relationship: '{source_entity_text}' "
        f"{relationship.get('label', 'RELATED_TO')} "
        f"'{target_entity_text}'. (ID: {relationship.get('id')})"
    )
    if relationship.get("attributes"):
        attrs_str = json.dumps(relationship["attributes"], sort_keys=True)
        description += f"\nAttributes: {attrs_str}"
    return description


def store_embeddings(
    entities: Optional[List[Entity]] = None,
    relationships: Optional[List[Relationship]] = None,
    entities_map_for_relationships: Optional[Dict[str, Entity]] = None
) -> Dict[str, int]:
    """
    Generates and stores embeddings for provided entities and/or relationships.
    `entities_map_for_relationships` is needed if relationships are processed to provide context.
    """
    if not embedding_model_client or not vector_db_client:
        logging.error("Embedding model or vector DB client not initialized. Cannot store embeddings.")
        return {"entities_processed": 0, "relationships_processed": 0}

    items_to_add_to_db = []
    entities_processed_count = 0
    relationships_processed_count = 0

    # Process Entities
    if entities:
        logging.info(f"Processing {len(entities)} entities for embedding and storage.")
        entity_texts = [_create_entity_description(e) for e in entities]
        try:
            entity_vectors = embedding_model_client.embed_batch(entity_texts)
            for entity, text_desc, vector in zip(entities, entity_texts, entity_vectors):
                items_to_add_to_db.append({
                    "id": f"entity_{entity['id']}", # Prefix to avoid ID collision with relationships
                    "text_description": text_desc,
                    "vector": vector,
                    "metadata": {"type": "entity", "original_id": entity["id"], "label": entity.get("label")}
                })
                entities_processed_count +=1
        except Exception as e:
            logging.error(f"Error embedding batch of entities: {e}")


    # Process Relationships
    if relationships:
        if not entities_map_for_relationships:
            logging.warning("`entities_map_for_relationships` not provided for relationship processing. Descriptions may lack context.")
            entities_map_for_relationships = {}

        logging.info(f"Processing {len(relationships)} relationships for embedding and storage.")
        rel_texts = [_create_relationship_description(r, entities_map_for_relationships) for r in relationships]
        try:
            rel_vectors = embedding_model_client.embed_batch(rel_texts)
            for rel, text_desc, vector in zip(relationships, rel_texts, rel_vectors):
                items_to_add_to_db.append({
                    "id": f"relationship_{rel['id']}", # Prefix
                    "text_description": text_desc,
                    "vector": vector,
                    "metadata": {
                        "type": "relationship",
                        "original_id": rel["id"],
                        "label": rel.get("label"),
                        "source_id": rel.get("source_entity_id"),
                        "target_id": rel.get("target_entity_id")
                    }
                })
                relationships_processed_count +=1
        except Exception as e:
            logging.error(f"Error embedding batch of relationships: {e}")

    if items_to_add_to_db:
        try:
            vector_db_client.add_items(items_to_add_to_db)
            logging.info(f"Successfully submitted {len(items_to_add_to_db)} items to vector DB.")
        except Exception as e:
            logging.error(f"Error adding items to vector DB: {e}")
            # Potentially retry or handle partial success

    return {"entities_processed": entities_processed_count, "relationships_processed": relationships_processed_count}


if __name__ == '__main__':
    logging.info("Starting example usage of embedding_store module.")

    # Sample data (could come from entity_extractor and kg_builder modules)
    sample_entities: List[Entity] = [
        {"id": "e1", "label": "PERSON", "text": "Alice Smith", "attributes": {"role": "Senior Engineer", "email": "alice@example.com"}},
        {"id": "e2", "label": "ORGANIZATION", "text": "Google", "attributes": {"industry": "Tech"}},
        {"id": "e5", "label": "PROJECT", "text": "LightRAG", "attributes": {"status": "Alpha"}},
    ]
    # Create a map for relationship context
    entities_lookup_map = {entity["id"]: entity for entity in sample_entities}

    sample_relationships: List[Relationship] = [
        {"id": "r1", "source_entity_id": "e1", "target_entity_id": "e2", "label": "WORKS_AT", "attributes": {"confidence": 0.95}},
        {"id": "r4", "source_entity_id": "e1", "target_entity_id": "e5", "label": "WORKS_ON", "attributes": {}},
    ]

    if embedding_model_client and vector_db_client:
        initial_db_size = vector_db_client.get_collection_size()
        logging.info(f"Initial vector DB size: {initial_db_size}")

        logging.info("\n--- Storing entity embeddings ---")
        entity_results = store_embeddings(entities=sample_entities)
        logging.info(f"Entity storage results: {entity_results}")
        logging.info(f"Vector DB size after entities: {vector_db_client.get_collection_size()}")

        # Verify one entity embedding
        item_e1 = vector_db_client.get_item("entity_e1")
        if item_e1:
            logging.info(f"Details for entity_e1: Text='{item_e1['text_description'][:50]}...', Vector[0]={item_e1['vector'][0]:.2f}, Metadata={item_e1['metadata']}")
        else:
            logging.error("Could not retrieve entity_e1 from vector DB.")

        logging.info("\n--- Storing relationship embeddings ---")
        # Pass the entities_map for context in relationship descriptions
        relationship_results = store_embeddings(relationships=sample_relationships, entities_map_for_relationships=entities_lookup_map)
        logging.info(f"Relationship storage results: {relationship_results}")
        logging.info(f"Vector DB size after relationships: {vector_db_client.get_collection_size()}")

        # Verify one relationship embedding
        item_r1 = vector_db_client.get_item("relationship_r1")
        if item_r1:
            logging.info(f"Details for relationship_r1: Text='{item_r1['text_description'][:60]}...', Vector[0]={item_r1['vector'][0]:.2f}, Metadata={item_r1['metadata']}")
        else:
            logging.error("Could not retrieve relationship_r1 from vector DB.")

        # Test storing both in one call
        logging.info("\n--- Storing both entities and relationships in one call (with new data) ---")
        new_entities: List[Entity] = [{"id": "e6", "label": "SKILL", "text": "Python Programming", "attributes": {}}]
        new_relationships: List[Relationship] = [{"id": "r5", "source_entity_id": "e1", "target_entity_id": "e6", "label": "HAS_SKILL", "attributes": {}}]

        # Update entities_lookup_map for the new entities if they are to be used for new relationships in the same call
        entities_lookup_map_updated = {**entities_lookup_map, new_entities[0]["id"]: new_entities[0]}

        combined_results = store_embeddings(
            entities=new_entities,
            relationships=new_relationships,
            entities_map_for_relationships=entities_lookup_map_updated
        )
        logging.info(f"Combined storage results: {combined_results}")
        logging.info(f"Final vector DB size: {vector_db_client.get_collection_size()}")

        item_e6 = vector_db_client.get_item("entity_e6")
        if item_e6:
            logging.info(f"Details for entity_e6: Text='{item_e6['text_description'][:50]}...', Vector[0]={item_e6['vector'][0]:.2f}, Metadata={item_e6['metadata']}")
        item_r5 = vector_db_client.get_item("relationship_r5")
        if item_r5:
             logging.info(f"Details for relationship_r5: Text='{item_r5['text_description'][:60]}...', Vector[0]={item_r5['vector'][0]:.2f}, Metadata={item_r5['metadata']}")


        # Test with clients unavailable
        logging.info("\n--- Testing with clients unavailable ---")
        original_embedding_client = embedding_model_client
        original_db_client = vector_db_client
        embedding_model_client = None
        vector_db_client = None
        error_results = store_embeddings(entities=sample_entities)
        logging.info(f"Results with clients unavailable: {error_results}")
        embedding_model_client = original_embedding_client
        vector_db_client = original_db_client

    logging.info("Example usage finished.")
