import networkx as nx
import os # Added for path manipulation in save/load

class GraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_counter = 0

    def add_nodes_from_text_chunks(self, text_chunks: list[str]) -> list[int]:
        """
        Adds nodes to the graph, one for each text chunk.
        Each node stores the chunk's text and a unique ID.

        Args:
            text_chunks (list[str]): A list of text chunks.

        Returns:
            list[int]: A list of node IDs that were added, in order.
        """
        node_ids = []
        for chunk in text_chunks:
            node_id = self.node_counter
            # GML requires node IDs to be strings or numbers, let's ensure they are robust
            # NetworkX internally handles integer node IDs fine, but for GML, string IDs can be safer.
            # However, since we use integers internally, let's stick to that and ensure GML handles it.
            # nx.write_gml and nx.read_gml should handle integer node labels correctly.
            self.graph.add_node(node_id, text=chunk, label=f"Chunk {node_id}") # Added label for GML
            node_ids.append(node_id)
            self.node_counter += 1
        return node_ids

    def add_sequential_edges(self, node_ids: list[int]):
        """
        Adds sequential edges between the given list of node IDs.
        An edge is created from node_ids[i] to node_ids[i+1].

        Args:
            node_ids (list[int]): A list of node IDs, assumed to be in order.
        """
        if not node_ids or len(node_ids) < 2:
            return

        for i in range(len(node_ids) - 1):
            from_node = node_ids[i]
            to_node = node_ids[i+1]
            if self.graph.has_node(from_node) and self.graph.has_node(to_node):
                self.graph.add_edge(from_node, to_node, type="sequential")
            else:
                # This case should ideally not happen if node_ids come from add_nodes_from_text_chunks
                print(f"Warning: Node(s) not found when trying to add sequential edge: {from_node} -> {to_node}")


    def get_graph(self) -> nx.DiGraph:
        return self.graph

    def save_graph_gml(self, file_path: str):
        """
        Saves the graph to a file in GML format.

        Args:
            file_path (str): The path to save the GML file.
        """
        try:
            nx.write_gml(self.graph, file_path)
            print(f"Graph saved to {file_path}")
        except Exception as e:
            print(f"Error saving graph to {file_path}: {e}")

    def load_graph_gml(self, file_path: str):
        """
        Loads a graph from a GML file.
        This will replace the current graph in the builder.
        It also attempts to infer the next node_counter based on max node ID in the loaded graph.

        Args:
            file_path (str): The path to the GML file.
        """
        try:
            self.graph = nx.read_gml(file_path, label='label') # Use 'label' for node labels if needed
            # GML typically reads node IDs as strings if they were written as such.
            # If nodes were integers, they might be read as strings. Need to handle this.
            # Let's test how read_gml handles integer nodes.
            # If nodes are read as strings '0', '1', etc., we need to convert them back or adjust.
            # For now, assume read_gml handles it, or node IDs are strings from the start.

            # Attempt to set node_counter to prevent ID clashes if more nodes are added.
            # This assumes node IDs are integers or string representations of integers.
            max_id = -1
            parsed_ids = []
            for node_str_id in self.graph.nodes():
                try:
                    # GML standard typically means node IDs are strings in the file.
                    # nx.read_gml might convert them to int if they look like int.
                    # Let's be safe and try to parse, then re-map if necessary.
                    # For simplicity, let's assume node IDs are integers and GML handles this.
                    # If nx.read_gml reads them as strings:
                    # mapping = {str(i): i for i in range(self.node_counter)}
                    # self.graph = nx.relabel_nodes(self.graph, mapping)

                    # Let's assume node IDs in GML are integers or correctly converted by read_gml.
                    # If node IDs are strings like "n0", "n1", this simple max_id won't work.
                    # The current add_nodes_from_text_chunks uses integer node_ids.
                    # nx.write_gml(G, path, stringizer=str) can be used to ensure string IDs.
                    # nx.read_gml(path, destringizer=int) for the reverse.
                    # For now, let's assume NetworkX handles integer node IDs correctly for GML.

                    node_id = int(node_str_id) # GML might read node IDs as strings
                    parsed_ids.append(node_id)
                    if node_id > max_id:
                        max_id = node_id
                except ValueError:
                    # Handle cases where node ID is not a simple integer string
                    # This could happen if node IDs are complex strings.
                    # For now, we assume simple integer node IDs.
                    print(f"Warning: Could not parse node ID '{node_str_id}' to integer for counter update.")


            if parsed_ids and all(isinstance(nid, int) for nid in parsed_ids):
                 # If all node IDs are integers, relabel graph to use these integers
                if any(isinstance(nid, str) for nid in self.graph.nodes()): # if any node id is string
                    mapping = {str(nid) : nid for nid in parsed_ids}
                    self.graph = nx.relabel_nodes(self.graph, mapping, copy=True)


            self.node_counter = max_id + 1 if max_id != -1 else 0
            print(f"Graph loaded from {file_path}. Node counter set to {self.node_counter}")
        except Exception as e:
            print(f"Error loading graph from {file_path}: {e}")
            # Ensure graph is in a consistent state (empty) if loading fails
            self.graph = nx.DiGraph()
            self.node_counter = 0


if __name__ == '__main__':
    builder = GraphBuilder()

    sample_chunks = [
        "Chunk 1: The beginning.",
        "Chunk 2: The middle part.",
        "Chunk 3: The end."
    ]

    node_ids = builder.add_nodes_from_text_chunks(sample_chunks)
    builder.add_sequential_edges(node_ids)

    graph = builder.get_graph()
    print("Original Graph:")
    for node in graph.nodes(data=True):
        print(f"  Node {node[0]}: {node[1]}")
    for edge in graph.edges(data=True):
        print(f"  Edge {edge[0]}->{edge[1]}: {edge[2]}")

    # --- Test Save and Load ---
    gml_file_path = "test_graph.gml"

    # Save
    builder.save_graph_gml(gml_file_path)

    # Create a new builder to load the graph
    loader_builder = GraphBuilder()
    loader_builder.load_graph_gml(gml_file_path)

    loaded_graph = loader_builder.get_graph()
    print("\nLoaded Graph:")
    if loaded_graph.number_of_nodes() > 0:
        for node in loaded_graph.nodes(data=True):
            # Node IDs from read_gml might be strings, ensure consistency if they were ints
            print(f"  Node {node[0]}: {node[1]}")
        for edge in loaded_graph.edges(data=True):
            # Edge node IDs also might be strings
            print(f"  Edge {edge[0]}->{edge[1]}: {edge[2]}")
        print(f"Node counter in loader_builder after load: {loader_builder.node_counter}")
    else:
        print("  Loaded graph is empty or loading failed.")

    # Test adding more nodes to the loaded graph
    if loaded_graph.number_of_nodes() > 0:
        print("\nAdding more nodes to loaded graph:")
        more_chunks_after_load = ["Chunk 4: After loading.", "Chunk 5: Penultimate."]
        new_node_ids = loader_builder.add_nodes_from_text_chunks(more_chunks_after_load)
        loader_builder.add_sequential_edges(new_node_ids)

        # Optionally, connect the last node of the loaded graph to the first new node
        # This requires knowing the last node ID of the previously loaded graph.
        # Assuming node IDs are integers and sequential from 0.
        if loaded_graph.nodes: # Check if graph is not empty
            # Find max existing node ID to connect from
            # Max ID was used to set node_counter, so previous max_id was loader_builder.node_counter - len(new_node_ids) -1
            # This logic is getting complex, assuming simple sequential integer IDs from 0.
            # Let's assume the last node of the *original* set of nodes before this new addition.
            # The node_ids list from the original load isn't directly available here.
            # A robust way would be to query the graph for the node with the highest ID before adding new ones.
            # For simplicity in example:
            # last_node_of_loaded_part = loader_builder.node_counter - len(new_node_ids) -1

            # Simpler: get the node IDs that existed before adding new_node_ids
            # This requires node_counter to be correctly set.
            # The new_node_ids start from the current node_counter.
            # So, the node just before the first of new_node_ids is new_node_ids[0] - 1.
            if new_node_ids and new_node_ids[0] > 0 :
                 # Check if there's a node with ID new_node_ids[0] - 1
                prev_node_id_to_connect = new_node_ids[0] -1
                if loaded_graph.has_node(prev_node_id_to_connect): # Check if node exists
                    loader_builder.graph.add_edge(prev_node_id_to_connect, new_node_ids[0], type="sequential_join_after_load")


        print("Graph after adding more nodes (post-load):")
        for node in loader_builder.graph.nodes(data=True):
            print(f"  Node {node[0]}: {node[1]}")
        for edge in loader_builder.graph.edges(data=True):
            print(f"  Edge {edge[0]}->{edge[1]}: {edge[2]}")
        print(f"Node counter now: {loader_builder.node_counter}")


    # Clean up the dummy GML file
    if os.path.exists(gml_file_path):
        os.remove(gml_file_path)
        print(f"\nCleaned up {gml_file_path}")
