# kag_builder/serialization.py

import networkx as nx
import json # For potentially saving/loading separate index structures if needed

# Define standard filenames or allow customization
DEFAULT_GRAPH_FILENAME = "knowledge_graph.graphml"
DEFAULT_INDEX_FILENAME = "mutual_index.json" # If we had a separate index

def save_kg(graph, filename: str = DEFAULT_GRAPH_FILENAME):
    """
    Saves the knowledge graph to a file using NetworkX's GraphML format.

    Args:
        graph (nx.Graph or nx.DiGraph or nx.MultiDiGraph): The graph to save.
        filename (str): The path to the file where the graph will be saved.
                        Defaults to 'knowledge_graph.graphml'.

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    try:
        nx.write_graphml(graph, filename)
        print(f"Knowledge graph saved successfully to {filename}")
        return True
    except Exception as e:
        print(f"Error saving knowledge graph to {filename}: {e}")
        return False

def load_kg(filename: str = DEFAULT_GRAPH_FILENAME):
    """
    Loads a knowledge graph from a GraphML file.

    Args:
        filename (str): The path to the GraphML file.
                        Defaults to 'knowledge_graph.graphml'.

    Returns:
        nx.Graph or nx.DiGraph or nx.MultiDiGraph or None: The loaded graph,
                                                            or None if loading fails.
    """
    try:
        # Specify node_type=str if node IDs are strings and you want to ensure they are read as such.
        # NetworkX usually infers types, but explicit typing can be safer.
        # For attributes, GraphML handles basic Python types (str, int, float, bool, list).
        graph = nx.read_graphml(filename)
        print(f"Knowledge graph loaded successfully from {filename}")
        return graph
    except FileNotFoundError:
        print(f"Error: Graph file not found at {filename}")
        return None
    except Exception as e:
        print(f"Error loading knowledge graph from {filename}: {e}")
        return None

# Placeholder for saving a separate mutual index structure if it becomes more complex.
# For now, the 'text_chunk_id' is part of the graph attributes.
def save_mutual_index(index_data: dict, filename: str = DEFAULT_INDEX_FILENAME):
    """
    Saves a mutual index data structure to a JSON file.
    (Currently a placeholder as index is embedded in graph).

    Args:
        index_data (dict): The index data to save.
        filename (str): The filename for the JSON output.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        with open(filename, 'w') as f:
            json.dump(index_data, f, indent=4)
        print(f"Mutual index saved successfully to {filename}")
        return True
    except Exception as e:
        print(f"Error saving mutual index to {filename}: {e}")
        return False

def load_mutual_index(filename: str = DEFAULT_INDEX_FILENAME) -> dict:
    """
    Loads a mutual index data structure from a JSON file.
    (Currently a placeholder).

    Args:
        filename (str): The filename of the JSON input.

    Returns:
        dict: The loaded index data, or None if an error occurs.
    """
    try:
        with open(filename, 'r') as f:
            index_data = json.load(f)
        print(f"Mutual index loaded successfully from {filename}")
        return index_data
    except FileNotFoundError:
        print(f"Error: Index file not found at {filename}")
        return None
    except Exception as e:
        print(f"Error loading mutual index from {filename}: {e}")
        return None

if __name__ == '__main__':
    print("Attempting to run serialization module test...")

    # Create a sample graph (similar to kg_construction output)
    g_test = nx.MultiDiGraph()
    g_test.add_node("Aspirin", label="CHEMICAL", text_chunk_id="doc1_sent1")
    g_test.add_node("Pain Relief", label="SYMPTOM", text_chunk_id="doc1_sent1")
    g_test.add_edge("Aspirin", "Pain Relief", type="TREATS", text_chunk_id="doc1_sent1", confidence=0.9)

    # Test saving the graph
    graph_filepath = "test_kg.graphml"
    print(f"\nAttempting to save graph to: {graph_filepath}")
    save_success = save_kg(g_test, graph_filepath)

    if save_success:
        print("\nAttempting to load graph from:", graph_filepath)
        g_loaded = load_kg(graph_filepath)

        if g_loaded:
            print(f"Loaded graph has {g_loaded.number_of_nodes()} nodes and {g_loaded.number_of_edges()} edges.")
            # Verify some data
            if g_loaded.has_node("Aspirin"):
                print("Aspirin node data:", g_loaded.nodes["Aspirin"])
            if g_loaded.has_edge("Aspirin", "Pain Relief"):
                # For MultiDiGraph, get_edge_data returns a dict of keys to attributes
                edge_data = g_loaded.get_edge_data("Aspirin", "Pain Relief")
                print("Aspirin -> Pain Relief edge data:", edge_data)
                # Example: Accessing the first edge's data (key 0 if only one)
                if 0 in edge_data:
                     print("Edge (key 0) attributes:", edge_data[0])


    # Test saving a dummy index (conceptual)
    dummy_index = {
        "doc1_sent1": {
            "nodes": ["Aspirin", "Pain Relief"],
            "edges": [("Aspirin", "Pain Relief", 0)] # (u,v,key)
        }
    }
    index_filepath = "test_mutual_index.json"
    print(f"\nAttempting to save dummy index to: {index_filepath}")
    save_index_success = save_mutual_index(dummy_index, index_filepath)

    if save_index_success:
        print("\nAttempting to load dummy index from:", index_filepath)
        loaded_index = load_mutual_index(index_filepath)
        if loaded_index:
            print("Loaded index data:", loaded_index)

    # Clean up test files (optional, but good practice for automated tests)
    # For now, this is a manual step if you run this file directly.
    # import os
    # if os.path.exists(graph_filepath):
    #     os.remove(graph_filepath)
    # if os.path.exists(index_filepath):
    #     os.remove(index_filepath)

    print("\nSerialization module basic test finished.")
