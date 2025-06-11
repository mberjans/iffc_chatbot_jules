# tests/test_kg_construction.py
import unittest
import networkx as nx
from kag_builder.kg_construction import create_kg

class TestKgConstruction(unittest.TestCase):

    def test_create_kg_empty(self):
        graph = create_kg([], [])
        self.assertIsNotNone(graph)
        self.assertTrue(isinstance(graph, nx.MultiDiGraph))
        self.assertEqual(graph.number_of_nodes(), 0)
        self.assertEqual(graph.number_of_edges(), 0)

    def test_create_kg_nodes_and_edges(self):
        entities = [
            {'text': 'DrugA', 'label': 'CHEMICAL', 'text_chunk_id': 'c1'},
            {'text': 'DiseaseX', 'label': 'DISEASE', 'text_chunk_id': 'c1'}
        ]
        relations = [
            {'entity1_text': 'DrugA', 'entity2_text': 'DiseaseX', 'type': 'TREATS', 'text_chunk_id': 'c1'}
        ]
        graph = create_kg(entities, relations)
        self.assertEqual(graph.number_of_nodes(), 2)
        self.assertEqual(graph.number_of_edges(), 1)
        self.assertTrue(graph.has_node('DrugA'))
        self.assertTrue(graph.has_node('DiseaseX'))
        self.assertTrue(graph.has_edge('DrugA', 'DiseaseX'))

        # Check node attributes
        self.assertEqual(graph.nodes['DrugA']['label'], 'CHEMICAL')
        self.assertEqual(graph.nodes['DrugA']['text_chunk_id'], 'c1')

        # Check edge attributes (key 0 for the first edge)
        edge_data = graph.get_edge_data('DrugA', 'DiseaseX')[0]
        self.assertEqual(edge_data['type'], 'TREATS')
        self.assertEqual(edge_data['text_chunk_id'], 'c1')

if __name__ == '__main__':
    unittest.main()
