import logging
from typing import List, Dict, Any, Set

# Assuming entity_extractor.py is in the same directory or accessible in PYTHONPATH
# from entity_extractor import Entity, Relationship # If running as part of a larger package
# For now, let's redefine them here for standalone module creation,
# but in a real project, they'd be imported.

class Entity(Dict[str, Any]): # Using Dict for simplicity here, replace with TypedDict if preferred
    id: str
    label: str
    text: str
    attributes: Dict[str, Any]

class Relationship(Dict[str, Any]): # Using Dict for simplicity
    id: str
    source_entity_id: str
    target_entity_id: str
    label: str
    attributes: Dict[str, Any]

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Placeholder for LightRAG Knowledge Graph client or components
# from lightrag.graph import KnowledgeGraph, KGNode, KGRelation # Example LightRAG imports

class MockLightRAGKnowledgeGraph:
    """
    Mocks the behavior of a LightRAG Knowledge Graph client or interface.
    In a real scenario, this would interact with LightRAG's graph database
    or graph management APIs.
    """
    def __init__(self, connection_string: str = "dummy_graph_db_connection"):
        logging.info(f"MockLightRAGKnowledgeGraph initialized with connection: {connection_string}")
        self.nodes: Dict[str, Entity] = {}
        self.edges: Dict[str, Relationship] = {}
        self._temp_node_ids: Set[str] = set() # To track nodes added in the current session for relationships

    def add_node(self, entity: Entity) -> str:
        """Simulates adding or updating a node (entity) in the graph."""
        node_id = entity.get("id")
        if not node_id:
            node_id = f"node_{len(self.nodes) + 1}" # Generate an ID if not present
            entity["id"] = node_id

        if node_id in self.nodes:
            logging.info(f"MockLightRAGKG: Updating node {node_id} ('{entity.get('text')}')")
            self.nodes[node_id].update(entity) # Simple update
        else:
            logging.info(f"MockLightRAGKG: Adding new node {node_id} ('{entity.get('text')}')")
            self.nodes[node_id] = entity.copy()
        self._temp_node_ids.add(node_id)
        return node_id

    def add_edge(self, relationship: Relationship) -> str:
        """Simulates adding or updating an edge (relationship) in the graph."""
        edge_id = relationship.get("id")
        source_id = relationship.get("source_entity_id")
        target_id = relationship.get("target_entity_id")

        if not edge_id:
            edge_id = f"edge_{len(self.edges) + 1}"
            relationship["id"] = edge_id

        # Check if source and target nodes exist (either pre-existing or added in this session)
        if not (source_id in self.nodes or source_id in self._temp_node_ids):
            logging.error(f"MockLightRAGKG: Source node {source_id} not found for relationship {edge_id}. Relationship not added.")
            raise ValueError(f"Source node {source_id} not found.")
        if not (target_id in self.nodes or target_id in self._temp_node_ids):
            logging.error(f"MockLightRAGKG: Target node {target_id} not found for relationship {edge_id}. Relationship not added.")
            raise ValueError(f"Target node {target_id} not found.")

        if edge_id in self.edges:
            logging.info(f"MockLightRAGKG: Updating edge {edge_id} ({source_id}-{relationship.get('label')}->{target_id})")
            self.edges[edge_id].update(relationship)
        else:
            logging.info(f"MockLightRAGKG: Adding new edge {edge_id} ({source_id}-{relationship.get('label')}->{target_id})")
            self.edges[edge_id] = relationship.copy()
        return edge_id

    def get_graph_summary(self) -> str:
        return f"Graph contains {len(self.nodes)} nodes and {len(self.edges)} edges."

    def clear_session_tracking(self):
        """Clears temporary tracking for a new batch of operations."""
        self._temp_node_ids.clear()


# Global LightRAG Knowledge Graph instance (or manage as per application structure)
try:
    # In a real app, configuration would come from settings or environment variables
    kg_instance = MockLightRAGKnowledgeGraph(connection_string="lightrag_graph_connection_details")
except Exception as e:
    logging.error(f"Failed to initialize LightRAG Knowledge Graph instance: {e}")
    kg_instance = None


def add_entities_to_graph(entities: List[Entity]) -> List[str]:
    """
    Adds a list of entities to the LightRAG knowledge graph.
    Returns a list of node IDs that were added or updated.
    """
    if not kg_instance:
        logging.error("Knowledge Graph instance is not available. Cannot add entities.")
        return []

    added_node_ids: List[str] = []
    if not entities:
        logging.info("No entities provided to add to the graph.")
        return []

    logging.info(f"Attempting to add {len(entities)} entities to the graph.")
    for entity in entities:
        try:
            node_id = kg_instance.add_node(entity)
            added_node_ids.append(node_id)
        except Exception as e:
            logging.error(f"Error adding entity '{entity.get('text', 'Unknown')}' (ID: {entity.get('id', 'N/A')}) to graph: {e}")
    logging.info(f"Successfully processed {len(added_node_ids)} entities for graph addition.")
    return added_node_ids

def add_relationships_to_graph(relationships: List[Relationship]) -> List[str]:
    """
    Adds a list of relationships to the LightRAG knowledge graph.
    Returns a list of edge IDs that were added or updated.
    """
    if not kg_instance:
        logging.error("Knowledge Graph instance is not available. Cannot add relationships.")
        return []

    added_edge_ids: List[str] = []
    if not relationships:
        logging.info("No relationships provided to add to the graph.")
        return []

    logging.info(f"Attempting to add {len(relationships)} relationships to the graph.")
    for rel in relationships:
        try:
            edge_id = kg_instance.add_edge(rel)
            added_edge_ids.append(edge_id)
        except ValueError as ve: # Specific handling for missing nodes
            logging.error(f"Skipping relationship '{rel.get('id', 'N/A')}' due to missing node: {ve}")
        except Exception as e:
            logging.error(f"Error adding relationship ID '{rel.get('id', 'N/A')}' to graph: {e}")
    logging.info(f"Successfully processed {len(added_edge_ids)} relationships for graph addition.")
    return added_edge_ids

def build_or_update_graph(entities: List[Entity], relationships: List[Relationship]) -> Dict[str, List[str]]:
    """
    Builds or updates the knowledge graph with given entities and relationships.
    Clears session tracking before starting.
    """
    if not kg_instance:
        logging.error("Knowledge Graph instance is not available for building/updating.")
        return {"added_nodes": [], "added_edges": []}

    kg_instance.clear_session_tracking() # Start fresh for this batch

    logging.info("Starting graph build/update process.")
    added_node_ids = add_entities_to_graph(entities)
    added_edge_ids = add_relationships_to_graph(relationships)

    logging.info(f"Graph build/update process complete. Added/updated {len(added_node_ids)} nodes and {len(added_edge_ids)} edges.")
    return {"added_nodes": added_node_ids, "added_edges": added_edge_ids}

if __name__ == '__main__':
    logging.info("Starting example usage of kg_builder module.")

    # Sample data (mimicking output from entity_extractor)
    entities_data: List[Entity] = [
        {"id": "e1", "label": "PERSON", "text": "Alice", "attributes": {"role": "Engineer"}},
        {"id": "e2", "label": "ORGANIZATION", "text": "Google", "attributes": {"industry": "Tech"}},
        {"id": "e3", "label": "LOCATION", "text": "New York", "attributes": {"country": "USA"}},
        {"id": "e4", "label": "PERSON", "text": "Bob", "attributes": {"status": "Intern"}}, # New entity
    ]
    relationships_data: List[Relationship] = [
        {"id": "r1", "source_entity_id": "e1", "target_entity_id": "e2", "label": "WORKS_AT", "attributes": {"confidence": 0.95}},
        {"id": "r2", "source_entity_id": "e1", "target_entity_id": "e3", "label": "LIVES_IN", "attributes": {}}, # Alice lives in New York
        {"id": "r3", "source_entity_id": "e4", "target_entity_id": "e2", "label": "INTERNS_AT", "attributes": {}}, # Bob interns at Google
    ]

    # Simulate a new batch of data
    new_entities_data: List[Entity] = [
        {"id": "e5", "label": "PROJECT", "text": "LightRAG", "attributes": {"status": "Alpha"}},
        {"id": "e1", "label": "PERSON", "text": "Alice Smith", "attributes": {"role": "Senior Engineer", "email": "alice@example.com"}}, # Update Alice
    ]
    new_relationships_data: List[Relationship] = [
        {"id": "r4", "source_entity_id": "e1", "target_entity_id": "e5", "label": "WORKS_ON", "attributes": {}}, # Alice works on LightRAG
        {"id": "r_invalid", "source_entity_id": "e_nonexistent", "target_entity_id": "e1", "label": "REPORTS_TO", "attributes": {}}, # Invalid
    ]

    if kg_instance:
        logging.info(f"\n--- Initial Graph State ---")
        logging.info(kg_instance.get_graph_summary()) # Should be empty or from previous runs if not reset

        logging.info(f"\n--- Processing First Batch ---")
        results_batch1 = build_or_update_graph(entities_data, relationships_data)
        logging.info(f"Batch 1 Results: {results_batch1}")
        logging.info(kg_instance.get_graph_summary())
        # print("Nodes:", kg_instance.nodes) # For detailed inspection
        # print("Edges:", kg_instance.edges)

        logging.info(f"\n--- Processing Second Batch (updates and new data) ---")
        results_batch2 = build_or_update_graph(new_entities_data, new_relationships_data)
        logging.info(f"Batch 2 Results: {results_batch2}")
        logging.info(kg_instance.get_graph_summary())
        # print("Nodes:", kg_instance.nodes)
        # print("Edges:", kg_instance.edges)

        # Test adding relationship with one existing and one new node within the same batch
        logging.info(f"\n--- Processing Batch with new node and relationship to it ---")
        entities_batch3: List[Entity] = [
            {"id": "e6", "label": "SKILL", "text": "Python", "attributes": {}},
        ]
        relationships_batch3: List[Relationship] = [
            {"id": "r5", "source_entity_id": "e1", "target_entity_id": "e6", "label": "HAS_SKILL", "attributes": {}},
        ]
        results_batch3 = build_or_update_graph(entities_batch3, relationships_batch3)
        logging.info(f"Batch 3 Results: {results_batch3}")
        logging.info(kg_instance.get_graph_summary())


        # Test with KG instance unavailable
        logging.info("\n--- Testing with KG instance unavailable ---")
        original_kg_instance = kg_instance
        kg_instance = None
        results_no_kg = build_or_update_graph(entities_data, relationships_data)
        logging.info(f"Results with no KG instance: {results_no_kg}")
        kg_instance = original_kg_instance # Restore

    logging.info("Example usage finished.")
