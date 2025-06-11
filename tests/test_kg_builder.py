import unittest
from unittest.mock import patch, MagicMock, call

# Assuming modules are importable
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import kg_builder # to access the module-level kg_instance
from kg_builder import (
    Entity, Relationship, # Assuming these are defined or imported in kg_builder
    add_entities_to_graph,
    add_relationships_to_graph,
    build_or_update_graph
)

# Sample data for testing
SAMPLE_ENTITIES_KG: list[Entity] = [
    {"id": "e1", "label": "PERSON", "text": "Alice", "attributes": {}},
    {"id": "e2", "label": "ORGANIZATION", "text": "Google", "attributes": {}}
]
SAMPLE_RELATIONSHIPS_KG: list[Relationship] = [
    {"id": "r1", "source_entity_id": "e1", "target_entity_id": "e2", "label": "WORKS_AT", "attributes": {}}
]

class TestKgBuilder(unittest.TestCase):

    def setUp(self):
        # Patch the global 'kg_instance' in the kg_builder module
        self.mock_kg_patcher = patch('kg_builder.kg_instance', autospec=True)
        self.mock_kg_instance = self.mock_kg_patcher.start()

        # Configure default return values for mock methods
        self.mock_kg_instance.add_node = MagicMock(side_effect=lambda entity: entity.get("id", "new_id"))
        self.mock_kg_instance.add_edge = MagicMock(side_effect=lambda rel: rel.get("id", "new_rel_id"))
        self.mock_kg_instance.clear_session_tracking = MagicMock()


    def tearDown(self):
        self.mock_kg_patcher.stop()

    def test_add_entities_to_graph_success(self):
        result_ids = add_entities_to_graph(SAMPLE_ENTITIES_KG)

        expected_calls = [call(entity) for entity in SAMPLE_ENTITIES_KG]
        self.mock_kg_instance.add_node.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(len(result_ids), len(SAMPLE_ENTITIES_KG))
        self.assertEqual(result_ids, [e["id"] for e in SAMPLE_ENTITIES_KG])


    def test_add_entities_to_graph_empty_list(self):
        result_ids = add_entities_to_graph([])
        self.mock_kg_instance.add_node.assert_not_called()
        self.assertEqual(result_ids, [])

    def test_add_entities_to_graph_kg_error(self):
        self.mock_kg_instance.add_node.side_effect = Exception("Simulated DB Error")
        result_ids = add_entities_to_graph(SAMPLE_ENTITIES_KG)

        # add_node should still be called for each entity
        self.assertEqual(self.mock_kg_instance.add_node.call_count, len(SAMPLE_ENTITIES_KG))
        self.assertEqual(result_ids, []) # Expect empty list as errors occur

    def test_add_entities_to_graph_kg_unavailable(self):
        with patch('kg_builder.kg_instance', None):
            result_ids = add_entities_to_graph(SAMPLE_ENTITIES_KG)
            self.assertEqual(result_ids, [])
            self.mock_kg_instance.add_node.assert_not_called()


    def test_add_relationships_to_graph_success(self):
        result_ids = add_relationships_to_graph(SAMPLE_RELATIONSHIPS_KG)

        expected_calls = [call(rel) for rel in SAMPLE_RELATIONSHIPS_KG]
        self.mock_kg_instance.add_edge.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(len(result_ids), len(SAMPLE_RELATIONSHIPS_KG))
        self.assertEqual(result_ids, [r["id"] for r in SAMPLE_RELATIONSHIPS_KG])

    def test_add_relationships_to_graph_empty_list(self):
        result_ids = add_relationships_to_graph([])
        self.mock_kg_instance.add_edge.assert_not_called()
        self.assertEqual(result_ids, [])

    def test_add_relationships_to_graph_kg_error_missing_node(self):
        # Simulate a ValueError for missing nodes, as in the original mock
        self.mock_kg_instance.add_edge.side_effect = ValueError("Source node not found")
        result_ids = add_relationships_to_graph(SAMPLE_RELATIONSHIPS_KG)

        self.assertEqual(self.mock_kg_instance.add_edge.call_count, len(SAMPLE_RELATIONSHIPS_KG))
        self.assertEqual(result_ids, []) # Errors lead to empty result list

    def test_add_relationships_to_graph_kg_general_error(self):
        self.mock_kg_instance.add_edge.side_effect = Exception("Simulated DB Error")
        result_ids = add_relationships_to_graph(SAMPLE_RELATIONSHIPS_KG)

        self.assertEqual(self.mock_kg_instance.add_edge.call_count, len(SAMPLE_RELATIONSHIPS_KG))
        self.assertEqual(result_ids, [])

    def test_add_relationships_to_graph_kg_unavailable(self):
         with patch('kg_builder.kg_instance', None):
            result_ids = add_relationships_to_graph(SAMPLE_RELATIONSHIPS_KG)
            self.assertEqual(result_ids, [])
            self.mock_kg_instance.add_edge.assert_not_called()


    def test_build_or_update_graph_success(self):
        # Make add_node and add_edge return the IDs as expected
        self.mock_kg_instance.add_node.side_effect = lambda e: e['id']
        self.mock_kg_instance.add_edge.side_effect = lambda r: r['id']

        expected_node_ids = [e["id"] for e in SAMPLE_ENTITIES_KG]
        expected_edge_ids = [r["id"] for r in SAMPLE_RELATIONSHIPS_KG]

        results = build_or_update_graph(SAMPLE_ENTITIES_KG, SAMPLE_RELATIONSHIPS_KG)

        self.mock_kg_instance.clear_session_tracking.assert_called_once()
        self.assertEqual(self.mock_kg_instance.add_node.call_count, len(SAMPLE_ENTITIES_KG))
        self.assertEqual(self.mock_kg_instance.add_edge.call_count, len(SAMPLE_RELATIONSHIPS_KG))
        self.assertEqual(results["added_nodes"], expected_node_ids)
        self.assertEqual(results["added_edges"], expected_edge_ids)

    def test_build_or_update_graph_entities_fail(self):
        self.mock_kg_instance.add_node.side_effect = Exception("Node addition error")
        # Relationships should still be attempted if entities partially succeed or fail individually
        # but add_entities_to_graph will return [], so add_relationships_to_graph will process based on that.
        # The current implementation of add_entities_to_graph returns [] on error.

        results = build_or_update_graph(SAMPLE_ENTITIES_KG, SAMPLE_RELATIONSHIPS_KG)

        self.mock_kg_instance.clear_session_tracking.assert_called_once()
        self.assertEqual(self.mock_kg_instance.add_node.call_count, len(SAMPLE_ENTITIES_KG))
        # add_relationships_to_graph will still be called, but might not add anything if dependent on nodes
        # that "failed" to add (though our mock doesn't directly link them for this test unless we make it so)
        self.assertEqual(self.mock_kg_instance.add_edge.call_count, len(SAMPLE_RELATIONSHIPS_KG))
        self.assertEqual(results["added_nodes"], [])
        # If add_edge also fails or depends on failed nodes, this could also be []
        self.assertEqual(results["added_edges"], [r["id"] for r in SAMPLE_RELATIONSHIPS_KG]) # Assuming add_edge itself doesn't fail here

    def test_build_or_update_graph_relationships_fail(self):
        self.mock_kg_instance.add_edge.side_effect = Exception("Edge addition error")

        results = build_or_update_graph(SAMPLE_ENTITIES_KG, SAMPLE_RELATIONSHIPS_KG)

        self.mock_kg_instance.clear_session_tracking.assert_called_once()
        self.assertEqual(self.mock_kg_instance.add_node.call_count, len(SAMPLE_ENTITIES_KG))
        self.assertEqual(self.mock_kg_instance.add_edge.call_count, len(SAMPLE_RELATIONSHIPS_KG))
        self.assertEqual(results["added_nodes"], [e["id"] for e in SAMPLE_ENTITIES_KG])
        self.assertEqual(results["added_edges"], [])


    def test_build_or_update_graph_kg_unavailable(self):
        with patch('kg_builder.kg_instance', None):
            results = build_or_update_graph(SAMPLE_ENTITIES_KG, SAMPLE_RELATIONSHIPS_KG)
            self.assertEqual(results, {"added_nodes": [], "added_edges": []})
            self.mock_kg_instance.clear_session_tracking.assert_not_called() # Original mock won't be called
            self.mock_kg_instance.add_node.assert_not_called()
            self.mock_kg_instance.add_edge.assert_not_called()


if __name__ == '__main__':
    import logging
    logging.disable(logging.CRITICAL)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
