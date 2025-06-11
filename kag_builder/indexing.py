# kag_builder/indexing.py

# The mutual indexing is primarily achieved by ensuring that entities and relations,
# and subsequently graph nodes and edges, store an identifier for their source
# (e.g., 'text_chunk_id').
# The `entity_extraction` module already adds `text_chunk_id` to entities.
# The `kg_construction` module already adds these as attributes to nodes and edges.

# This module can provide utility functions for working with these indices if needed,
# or define more complex index structures in the future.

def get_source_ids_for_node(graph, node_id) -> set:
    """
    Retrieves the set of text_chunk_ids associated with a given node.
    A node might be derived from text found in multiple chunks if entities are merged.

    Args:
        graph (networkx.Graph): The knowledge graph.
        node_id: The ID of the node (e.g., entity text).

    Returns:
        set: A set of text_chunk_ids. Returns an empty set if node not found
             or no 'text_chunk_id' attribute.
    """
    if not graph.has_node(node_id):
        return set()

    node_data = graph.nodes[node_id]
    # Assuming 'text_chunk_id' could be a single value or a list if merged from multiple sources.
    # For now, let's assume it's a single string as per current entity_extraction.
    # A more robust implementation might handle cases where it's a list.
    source_id = node_data.get("text_chunk_id")
    if source_id:
        if isinstance(source_id, list):
            return set(source_id)
        return {source_id}
    return set()

def get_source_ids_for_edge(graph, u, v, key=None) -> set:
    """
    Retrieves the set of text_chunk_ids associated with a given edge.
    If key is None, it checks all edges between u and v.

    Args:
        graph (networkx.MultiDiGraph): The knowledge graph.
        u: The source node of the edge.
        v: The target node of the edge.
        key: The key of the edge (for MultiDiGraph). If None, returns sources for all
             edges between u and v.

    Returns:
        set: A set of text_chunk_ids. Returns an empty set if edge not found
             or no 'text_chunk_id' attribute.
    """
    if not graph.has_edge(u, v):
        return set()

    source_ids = set()
    if key is not None:
        if graph.has_edge(u, v, key):
            edge_data = graph.get_edge_data(u, v, key)
            source_id = edge_data.get("text_chunk_id")
            if source_id:
                if isinstance(source_id, list):
                    source_ids.update(source_id)
                else:
                    source_ids.add(source_id)
    else: # Check all edges between u and v
        for edge_data in graph.get_edge_data(u, v).values():
            source_id = edge_data.get("text_chunk_id")
            if source_id:
                if isinstance(source_id, list):
                    source_ids.update(source_id)
                else:
                    source_ids.add(source_id)
    return source_ids

# Future enhancements could include:
# - A dedicated index structure (e.g., a dictionary mapping chunk_id to list of nodes/edges).
# - Functions to build this reverse index from a graph.
# - More sophisticated merging strategies for text_chunk_ids if entities/relations
#   from different chunks are identified as identical.

if __name__ == '__main__':
    print("Attempting to run indexing module conceptual test...")

    # This test requires a graph, so we'll use a simplified version
    # of what kg_construction would produce.
    import networkx as nx

    # Sample data similar to what kg_construction would use/produce
    sample_entities_for_graph = [
        {'text': 'Aspirin', 'label': 'CHEMICAL', 'text_chunk_id': 'doc1_sent1'},
        {'text': 'pain relief', 'label': 'MEDICAL_CONDITION', 'text_chunk_id': 'doc1_sent1'},
        {'text': 'Aspirin', 'label': 'CHEMICAL', 'text_chunk_id': 'doc2_sent5'}, # Aspirin mentioned in another doc
    ]

    sample_relations_for_graph = [
        {'entity1_text': 'Aspirin', 'entity2_text': 'pain relief', 'type': 'TREATS', 'text_chunk_id': 'doc1_sent1'},
    ]

    # Simplified graph creation for testing indexing
    g = nx.MultiDiGraph()
    # Add nodes, handling potential multiple mentions by storing IDs as a list (conceptual)
    # Current kg_construction would overwrite; this shows how one might collect IDs.
    # For this test, we'll manually create what a more complex node aggregation might do.
    g.add_node("Aspirin", label="CHEMICAL", text_chunk_id=["doc1_sent1", "doc2_sent5"]) # Manually creating list
    g.add_node("pain relief", label="MEDICAL_CONDITION", text_chunk_id="doc1_sent1")

    g.add_edge("Aspirin", "pain relief", type="TREATS", text_chunk_id="doc1_sent1")

    print(f"Graph created with {g.number_of_nodes()} nodes and {g.number_of_edges()} edges.")

    # Test get_source_ids_for_node
    node_id_aspirin = "Aspirin"
    aspirin_sources = get_source_ids_for_node(g, node_id_aspirin)
    print(f"Source chunk IDs for node '{node_id_aspirin}': {aspirin_sources}")
    # Expected: {'doc1_sent1', 'doc2_sent5'}

    node_id_pain = "pain relief"
    pain_sources = get_source_ids_for_node(g, node_id_pain)
    print(f"Source chunk IDs for node '{node_id_pain}': {pain_sources}")
    # Expected: {'doc1_sent1'}

    node_id_nonexistent = "NonExistentDrug"
    nonexistent_sources = get_source_ids_for_node(g, node_id_nonexistent)
    print(f"Source chunk IDs for node '{node_id_nonexistent}': {nonexistent_sources}")
    # Expected: set()

    # Test get_source_ids_for_edge
    edge_u, edge_v = "Aspirin", "pain relief"
    edge_sources = get_source_ids_for_edge(g, edge_u, edge_v) # Will get for all keys if multiple
    print(f"Source chunk IDs for edges between '{edge_u}' and '{edge_v}': {edge_sources}")
    # Expected: {'doc1_sent1'} (assuming one edge with this ID)

    # Test with specific key (assuming key=0 for the first/only edge)
    edge_key = 0 # NetworkX assigns integer keys for MultiDiGraph edges
    if g.has_edge(edge_u, edge_v, key=edge_key):
        edge_sources_key = get_source_ids_for_edge(g, edge_u, edge_v, key=edge_key)
        print(f"Source chunk IDs for edge ('{edge_u}', '{edge_v}', key={edge_key}): {edge_sources_key}")
        # Expected: {'doc1_sent1'}
    else:
        print(f"Edge ('{edge_u}', '{edge_v}', key={edge_key}) not found for specific key test.")


    print("\nIndexing module conceptual test finished.")
    print("Note: True mutual indexing relies on consistent 'text_chunk_id' propagation "
          "from entity/relation extraction into graph construction.")
