import unittest
import networkx as nx
import os
from src.graph_builder import GraphBuilder # Assuming src is discoverable

class TestGraphBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = GraphBuilder()
        self.test_gml_file = "test_graph_builder.gml"

    def tearDown(self):
        if os.path.exists(self.test_gml_file):
            os.remove(self.test_gml_file)

    def test_initial_graph_is_empty_digraph(self):
        self.assertIsNotNone(self.builder.graph)
        self.assertIsInstance(self.builder.graph, nx.DiGraph)
        self.assertEqual(self.builder.graph.number_of_nodes(), 0)
        self.assertEqual(self.builder.graph.number_of_edges(), 0)
        self.assertEqual(self.builder.node_counter, 0)

    def test_add_nodes_from_text_chunks(self):
        chunks = ["First chunk.", "Second chunk."]
        node_ids = self.builder.add_nodes_from_text_chunks(chunks)

        self.assertEqual(len(node_ids), 2)
        self.assertEqual(self.builder.graph.number_of_nodes(), 2)
        self.assertEqual(self.builder.node_counter, 2)

        self.assertEqual(self.builder.graph.nodes[node_ids[0]]['text'], "First chunk.")
        self.assertEqual(self.builder.graph.nodes[node_ids[0]]['label'], "Chunk 0")
        self.assertEqual(self.builder.graph.nodes[node_ids[1]]['text'], "Second chunk.")
        self.assertEqual(self.builder.graph.nodes[node_ids[1]]['label'], "Chunk 1")

        # Test adding more nodes
        more_chunks = ["Third chunk."]
        more_node_ids = self.builder.add_nodes_from_text_chunks(more_chunks)
        self.assertEqual(len(more_node_ids), 1)
        self.assertEqual(self.builder.graph.number_of_nodes(), 3)
        self.assertEqual(self.builder.node_counter, 3)
        self.assertEqual(self.builder.graph.nodes[more_node_ids[0]]['text'], "Third chunk.")
        self.assertEqual(self.builder.graph.nodes[more_node_ids[0]]['label'], "Chunk 2")


    def test_add_nodes_from_empty_chunks(self):
        node_ids = self.builder.add_nodes_from_text_chunks([])
        self.assertEqual(len(node_ids), 0)
        self.assertEqual(self.builder.graph.number_of_nodes(), 0)
        self.assertEqual(self.builder.node_counter, 0)

    def test_add_sequential_edges(self):
        chunks = ["A", "B", "C"]
        node_ids = self.builder.add_nodes_from_text_chunks(chunks)
        self.builder.add_sequential_edges(node_ids)

        self.assertEqual(self.builder.graph.number_of_edges(), 2)
        self.assertTrue(self.builder.graph.has_edge(node_ids[0], node_ids[1]))
        self.assertEqual(self.builder.graph.edges[node_ids[0], node_ids[1]]['type'], "sequential")
        self.assertTrue(self.builder.graph.has_edge(node_ids[1], node_ids[2]))
        self.assertEqual(self.builder.graph.edges[node_ids[1], node_ids[2]]['type'], "sequential")

    def test_add_sequential_edges_no_nodes(self):
        self.builder.add_sequential_edges([])
        self.assertEqual(self.builder.graph.number_of_edges(), 0)

    def test_add_sequential_edges_single_node(self):
        node_ids = self.builder.add_nodes_from_text_chunks(["Single"])
        self.builder.add_sequential_edges(node_ids)
        self.assertEqual(self.builder.graph.number_of_edges(), 0)

    def test_add_sequential_edges_non_existent_nodes(self):
        # This test is tricky because add_sequential_edges checks for node existence.
        # It prints a warning but doesn't raise an error.
        # We can check that no edges are added.
        self.builder.add_nodes_from_text_chunks(["A"]) # node 0
        self.builder.add_sequential_edges([0, 1]) # Edge from existing 0 to non-existing 1
        self.assertEqual(self.builder.graph.number_of_edges(), 0)

        self.builder.add_sequential_edges([5, 6]) # Edge between two non-existing nodes
        self.assertEqual(self.builder.graph.number_of_edges(), 0)


    def test_save_and_load_graph_gml(self):
        chunks = ["SaveData1", "SaveData2"]
        node_ids = self.builder.add_nodes_from_text_chunks(chunks)
        self.builder.add_sequential_edges(node_ids)

        self.builder.save_graph_gml(self.test_gml_file)
        self.assertTrue(os.path.exists(self.test_gml_file))

        loader = GraphBuilder()
        loader.load_graph_gml(self.test_gml_file)

        loaded_g = loader.graph
        self.assertEqual(loaded_g.number_of_nodes(), 2)
        self.assertEqual(loaded_g.number_of_edges(), 1)

        # NetworkX GML reader might read node IDs as strings,
        # but our loader attempts to convert them back to int and relabel.
        # Let's check based on the integer node IDs we expect.
        # Original node_ids were 0 and 1.

        # Verify nodes (assuming integer node IDs after load)
        # The label attribute is what we set as "Chunk X"
        # The text attribute is the actual chunk content.
        # GML stores node IDs as 'id' in the GML file. nx.read_gml uses this.
        # Our loader relabels to ensure integer node IDs if they were strings.

        # Check node 0 (original node_ids[0])
        self.assertIn(0, loaded_g.nodes)
        self.assertEqual(loaded_g.nodes[0]['text'], "SaveData1")
        self.assertEqual(loaded_g.nodes[0]['label'], "Chunk 0")

        # Check node 1 (original node_ids[1])
        self.assertIn(1, loaded_g.nodes)
        self.assertEqual(loaded_g.nodes[1]['text'], "SaveData2")
        self.assertEqual(loaded_g.nodes[1]['label'], "Chunk 1")

        # Check edge
        self.assertTrue(loaded_g.has_edge(0, 1))
        self.assertEqual(loaded_g.edges[0, 1]['type'], "sequential")

        # Check node counter in loader
        self.assertEqual(loader.node_counter, 2) # Should be max_id + 1

    def test_load_non_existent_gml_file(self):
        # Suppress print output for cleaner test results
        # import io
        # from contextlib import redirect_stderr
        # f = io.StringIO()
        # with redirect_stderr(f):
        #     self.builder.load_graph_gml("non_existent.gml")
        # self.assertIn("Error loading graph", f.getvalue())

        self.builder.load_graph_gml("non_existent.gml") # Error message will be printed
        self.assertEqual(self.builder.graph.number_of_nodes(), 0) # Graph should be reset
        self.assertEqual(self.builder.node_counter, 0)

    def test_load_invalid_gml_file(self):
        with open(self.test_gml_file, "w") as f:
            f.write("this is not gml content")

        self.builder.load_graph_gml(self.test_gml_file)
        self.assertEqual(self.builder.graph.number_of_nodes(), 0)
        self.assertEqual(self.builder.node_counter, 0)

    def test_adding_nodes_after_loading(self):
        chunks1 = ["A", "B"]
        node_ids1 = self.builder.add_nodes_from_text_chunks(chunks1) # Nodes 0, 1
        self.builder.add_sequential_edges(node_ids1)
        self.builder.save_graph_gml(self.test_gml_file)

        loader = GraphBuilder()
        loader.load_graph_gml(self.test_gml_file) # Loads nodes 0, 1. node_counter becomes 2.

        self.assertEqual(loader.node_counter, 2)

        chunks2 = ["C", "D"]
        node_ids2 = loader.add_nodes_from_text_chunks(chunks2) # Should create nodes 2, 3

        self.assertEqual(node_ids2, [2, 3])
        self.assertEqual(loader.graph.number_of_nodes(), 4)
        self.assertEqual(loader.node_counter, 4)
        self.assertEqual(loader.graph.nodes[2]['text'], "C")
        self.assertEqual(loader.graph.nodes[3]['text'], "D")

        loader.add_sequential_edges(node_ids2) # Edge 2->3
        self.assertTrue(loader.graph.has_edge(2,3))

        # Check that old edge 0->1 still exists
        self.assertTrue(loader.graph.has_edge(0,1))


if __name__ == '__main__':
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    src_path = os.path.join(project_root, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    global GraphBuilder # Re-import for safety
    from graph_builder import GraphBuilder

    unittest.main()
