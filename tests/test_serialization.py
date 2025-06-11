# tests/test_serialization.py
import unittest
import networkx as nx
import os
from kag_builder.serialization import save_kg, load_kg, save_mutual_index, load_mutual_index

class TestSerialization(unittest.TestCase):
    test_graph_file = "test_graph.graphml"
    test_index_file = "test_index.json"

    def tearDown(self):
        # Clean up created files after each test method
        if os.path.exists(self.test_graph_file):
            os.remove(self.test_graph_file)
        if os.path.exists(self.test_index_file):
            os.remove(self.test_index_file)

    def test_save_and_load_kg(self):
        g = nx.MultiDiGraph()
        g.add_node("Node1", attr1="value1")
        g.add_edge("Node1", "Node2", type="LINK")

        save_kg(g, self.test_graph_file)
        self.assertTrue(os.path.exists(self.test_graph_file))

        loaded_g = load_kg(self.test_graph_file)
        self.assertIsNotNone(loaded_g)
        self.assertEqual(loaded_g.number_of_nodes(), 2) # Node2 is implicitly created
        self.assertEqual(loaded_g.number_of_edges(), 1)
        self.assertEqual(loaded_g.nodes["Node1"]["attr1"], "value1")

    def test_save_and_load_mutual_index(self):
        dummy_index = {"chunk1": ["Node1"]}
        save_mutual_index(dummy_index, self.test_index_file)
        self.assertTrue(os.path.exists(self.test_index_file))

        loaded_index = load_mutual_index(self.test_index_file)
        self.assertIsNotNone(loaded_index)
        self.assertEqual(loaded_index["chunk1"], ["Node1"])

    def test_load_kg_file_not_found(self):
        loaded_g = load_kg("non_existent_file.graphml")
        self.assertIsNone(loaded_g)

    def test_load_index_file_not_found(self):
        loaded_index = load_mutual_index("non_existent_index.json")
        self.assertIsNone(loaded_index)

if __name__ == '__main__':
    unittest.main()
