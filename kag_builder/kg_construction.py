# kag_builder/kg_construction.py

import networkx as nx

def create_kg(entities: list, relations: list):
    """
    Creates a knowledge graph from lists of entities and relations.

    Args:
        entities (list): A list of entity dictionaries. Each entity dict is expected
                         to have at least 'text' (unique identifier for the node) and 'label'.
                         Other attributes like 'start_char', 'end_char', 'text_chunk_id'
                         will be added as node attributes.
        relations (list): A list of relation dictionaries. Each relation dict is expected
                          to have 'entity1_text', 'entity2_text', and 'type'.
                          'text_chunk_id' will be added as an edge attribute.

    Returns:
        nx.MultiDiGraph: A NetworkX MultiDiGraph object representing the knowledge graph.
                         Nodes are entity texts, and edges represent relations.
                         Node attributes include 'label', 'start_char', 'end_char', 'text_chunk_id'.
                         Edge attributes include 'type' and 'text_chunk_id'.
    """
    graph = nx.MultiDiGraph() # MultiDiGraph allows multiple edges between two nodes

    # Add nodes (entities)
    for entity_dict in entities:
        node_id = entity_dict["text"] # Using entity text as unique ID for now

        # Prepare attributes, excluding 'text' itself if it's used as node_id
        attributes = {k: v for k, v in entity_dict.items() if k != "text"}

        if not graph.has_node(node_id):
            graph.add_node(node_id, **attributes)
        else:
            # If node exists, update its attributes (e.g., if seen in another chunk)
            # This is a simple update; more sophisticated merging might be needed
            for key, value in attributes.items():
                # Potentially handle lists if an attribute can have multiple values
                if key not in graph.nodes[node_id] or graph.nodes[node_id][key] != value:
                     # A simple strategy: overwrite or add. Could be more complex.
                    graph.nodes[node_id][key] = value


    # Add edges (relations)
    for rel_dict in relations:
        source_node = rel_dict["entity1_text"]
        target_node = rel_dict["entity2_text"]
        relation_type = rel_dict["type"]

        # Prepare edge attributes
        edge_attributes = {k: v for k, v in rel_dict.items()
                           if k not in ["entity1_text", "entity2_text", "type"]}
        edge_attributes["type"] = relation_type # Ensure 'type' is an attribute

        # Ensure both source and target nodes exist from the entities list before adding edge
        # This assumes entities list is comprehensive for all relations.
        if graph.has_node(source_node) and graph.has_node(target_node):
            graph.add_edge(source_node, target_node, **edge_attributes)
        else:
            # This case should ideally not happen if entities and relations are consistent
            print(f"Warning: Skipping relation {rel_dict} due to missing node(s). "
                  f"Source '{source_node}' present: {graph.has_node(source_node)}, "
                  f"Target '{target_node}' present: {graph.has_node(target_node)}")

    return graph

if __name__ == '__main__':
    print("Attempting to run KG construction test...")

    # Sample entities and relations (typically from other modules)
    sample_entities = [
        {'text': 'Aspirin', 'label': 'CHEMICAL', 'start_char': 0, 'end_char': 7, 'text_chunk_id': 'chunk1'},
        {'text': 'pain relief', 'label': 'MEDICAL_CONDITION', 'start_char': 28, 'end_char': 39, 'text_chunk_id': 'chunk1'},
        {'text': 'blood clots', 'label': 'MEDICAL_CONDITION', 'start_char': 55, 'end_char': 66, 'text_chunk_id': 'chunk1'},
        {'text': 'Interleukin-6', 'label': 'GENE_OR_GENE_PRODUCT', 'start_char': 0, 'end_char': 13, 'text_chunk_id': 'chunk2'},
        {'text': 'cytokine', 'label': 'PROTEIN', 'start_char': 30, 'end_char': 38, 'text_chunk_id': 'chunk2'}, # Added for relation
    ]

    sample_relations = [
        {'entity1_text': 'Aspirin', 'entity1_label': 'CHEMICAL',
         'entity2_text': 'pain relief', 'entity2_label': 'MEDICAL_CONDITION',
         'type': 'TREATS', 'text_chunk_id': 'chunk1'},
        {'entity1_text': 'Aspirin', 'entity1_label': 'CHEMICAL',
         'entity2_text': 'blood clots', 'entity2_label': 'MEDICAL_CONDITION',
         'type': 'PREVENTS', 'text_chunk_id': 'chunk1'}, # Example of another relation type
        {'entity1_text': 'Interleukin-6', 'entity1_label': 'GENE_OR_GENE_PRODUCT',
         'entity2_text': 'cytokine', 'entity2_label': 'PROTEIN',
         'type': 'IS_A', 'text_chunk_id': 'chunk2'}
    ]

    # Test with a relation where one entity might be missing (if sample_entities is not updated)
    # sample_relations.append(
    #     {'entity1_text': 'Interleukin-6', 'entity1_label': 'GENE_OR_GENE_PRODUCT',
    #      'entity2_text': 'inflammation', 'entity2_label': 'PROCESS', # 'inflammation' not in sample_entities
    #      'type': 'ASSOCIATED_WITH', 'text_chunk_id': 'chunk2'}
    # )


    print(f"\nBuilding KG with {len(sample_entities)} entities and {len(sample_relations)} relations.")
    kg = create_kg(sample_entities, sample_relations)

    print(f"\nKG Construction complete.")
    print(f"Number of nodes in KG: {kg.number_of_nodes()}")
    print(f"Number of edges in KG: {kg.number_of_edges()}")

    print("\nNodes in KG (with attributes):")
    for node, data in kg.nodes(data=True):
        print(f"- {node}: {data}")

    print("\nEdges in KG (with attributes):")
    for u, v, data in kg.edges(data=True):
        print(f"- ({u}) -> ({v}): {data}")

    # Example of adding more entities and relations to an existing graph (conceptually)
    # This function creates a new graph, but you could modify it to update an existing one.
    print("\nDemonstrating adding to KG (conceptually):")
    additional_entities = [
        {'text': 'Metformin', 'label': 'CHEMICAL', 'start_char': 0, 'end_char':9, 'text_chunk_id': 'chunk3'},
        {'text': 'Diabetes Type 2', 'label': 'DISEASE', 'start_char': 20, 'end_char':35, 'text_chunk_id': 'chunk3'}
    ]
    additional_relations = [
        {'entity1_text': 'Metformin', 'entity1_label': 'CHEMICAL',
         'entity2_text': 'Diabetes Type 2', 'entity2_label': 'DISEASE',
         'type': 'TREATS', 'text_chunk_id': 'chunk3'}
    ]

    # To truly update, you'd pass `kg` to a modified `create_kg` or have an `update_kg` function.
    # For this example, we'll just create a new graph with combined data.
    combined_entities = sample_entities + additional_entities
    combined_relations = sample_relations + additional_relations

    kg_combined = create_kg(combined_entities, combined_relations)
    print(f"Number of nodes in combined KG: {kg_combined.number_of_nodes()}")
    print(f"Number of edges in combined KG: {kg_combined.number_of_edges()}")

    # Check if Aspirin node attributes were updated if it appeared in additional_entities with new info
    # (In this specific example, it doesn't, but it's a point for consideration in merging)

    print("\nKG construction module basic test finished.")
