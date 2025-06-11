import unittest
from unittest.mock import patch, MagicMock, call

# Assuming modules are importable
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import embedding_store # To access module-level clients
from embedding_store import (
    Entity, Relationship, # Assuming these are defined or imported
    _create_entity_description,
    _create_relationship_description,
    store_embeddings
)

# Sample data for testing
SAMPLE_ENTITY_ES: Entity = {"id": "e1", "label": "PERSON", "text": "Alice", "attributes": {"age": 30}}
SAMPLE_RELATIONSHIP_ES: Relationship = {
    "id": "r1", "source_entity_id": "e1", "target_entity_id": "e2",
    "label": "WORKS_FOR", "attributes": {"role": "Engineer"}
}
# For relationship description context
ENTITIES_MAP_ES: dict[str, Entity] = {
    "e1": SAMPLE_ENTITY_ES,
    "e2": {"id": "e2", "label": "ORGANIZATION", "text": "AcmeCorp", "attributes": {}}
}
MOCK_EMBEDDING_VECTOR = [0.1, 0.2, 0.3, 0.4, 0.5]

class TestEmbeddingStore(unittest.TestCase):

    def setUp(self):
        # Patch module-level clients
        self.mock_embed_model_patcher = patch('embedding_store.embedding_model_client', autospec=True)
        self.mock_vector_db_patcher = patch('embedding_store.vector_db_client', autospec=True)

        self.mock_embedding_model = self.mock_embed_model_patcher.start()
        self.mock_vector_db = self.mock_vector_db_patcher.start()

        # Configure default mock behaviors
        self.mock_embedding_model.embed = MagicMock(return_value=MOCK_EMBEDDING_VECTOR)
        self.mock_embedding_model.embed_batch = MagicMock(return_value=[MOCK_EMBEDDING_VECTOR])
        self.mock_vector_db.add_item = MagicMock()
        self.mock_vector_db.add_items = MagicMock()

    def tearDown(self):
        self.mock_embed_model_patcher.stop()
        self.mock_vector_db_patcher.stop()

    def test_create_entity_description(self):
        desc = _create_entity_description(SAMPLE_ENTITY_ES)
        self.assertIn("Entity: Alice", desc)
        self.assertIn("Type: PERSON", desc)
        self.assertIn('"age": 30', desc)

        desc_no_attrs = _create_entity_description({"id": "e2", "label": "LOCATION", "text": "Paris", "attributes": None})
        self.assertIn("Entity: Paris", desc_no_attrs)
        self.assertNotIn("Attributes:", desc_no_attrs)

        desc_empty_attrs = _create_entity_description({"id": "e3", "label": "EVENT", "text": "Concert", "attributes": {}})
        self.assertIn("Attributes: {}", desc_empty_attrs)


    def test_create_relationship_description(self):
        desc = _create_relationship_description(SAMPLE_RELATIONSHIP_ES, ENTITIES_MAP_ES)
        self.assertIn("Relationship: 'Alice' WORKS_FOR 'AcmeCorp'", desc)
        self.assertIn("ID: r1", desc)
        self.assertIn('"role": "Engineer"', desc)

    def test_create_relationship_description_missing_entities_in_map(self):
        incomplete_map = {"e1": SAMPLE_ENTITY_ES} # Missing e2
        desc = _create_relationship_description(SAMPLE_RELATIONSHIP_ES, incomplete_map)
        self.assertIn("Relationship: 'Alice' WORKS_FOR 'Unknown Target Entity'", desc)

        empty_map = {}
        desc_empty = _create_relationship_description(SAMPLE_RELATIONSHIP_ES, empty_map)
        self.assertIn("Relationship: 'Unknown Source Entity' WORKS_FOR 'Unknown Target Entity'", desc_empty)


    def test_store_embeddings_entities_only(self):
        entities_to_store = [SAMPLE_ENTITY_ES]
        self.mock_embedding_model.embed_batch.return_value = [MOCK_EMBEDDING_VECTOR]

        results = store_embeddings(entities=entities_to_store)

        self.mock_embedding_model.embed_batch.assert_called_once()
        # Check that the input to embed_batch was a list containing the description of SAMPLE_ENTITY_ES
        call_args = self.mock_embedding_model.embed_batch.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertIn("Entity: Alice", call_args[0])

        self.mock_vector_db.add_items.assert_called_once()
        db_call_args = self.mock_vector_db.add_items.call_args[0][0]
        self.assertEqual(len(db_call_args), 1)
        self.assertEqual(db_call_args[0]["id"], f"entity_{SAMPLE_ENTITY_ES['id']}")
        self.assertEqual(db_call_args[0]["vector"], MOCK_EMBEDDING_VECTOR)
        self.assertEqual(db_call_args[0]["metadata"]["type"], "entity")

        self.assertEqual(results, {"entities_processed": 1, "relationships_processed": 0})

    def test_store_embeddings_relationships_only(self):
        relationships_to_store = [SAMPLE_RELATIONSHIP_ES]
        self.mock_embedding_model.embed_batch.return_value = [MOCK_EMBEDDING_VECTOR]

        results = store_embeddings(relationships=relationships_to_store, entities_map_for_relationships=ENTITIES_MAP_ES)

        self.mock_embedding_model.embed_batch.assert_called_once()
        call_args = self.mock_embedding_model.embed_batch.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertIn("Relationship: 'Alice' WORKS_FOR 'AcmeCorp'", call_args[0])

        self.mock_vector_db.add_items.assert_called_once()
        db_call_args = self.mock_vector_db.add_items.call_args[0][0]
        self.assertEqual(len(db_call_args), 1)
        self.assertEqual(db_call_args[0]["id"], f"relationship_{SAMPLE_RELATIONSHIP_ES['id']}")
        self.assertEqual(db_call_args[0]["vector"], MOCK_EMBEDDING_VECTOR)
        self.assertEqual(db_call_args[0]["metadata"]["type"], "relationship")

        self.assertEqual(results, {"entities_processed": 0, "relationships_processed": 1})

    def test_store_embeddings_both_entities_and_relationships(self):
        entities_to_store = [SAMPLE_ENTITY_ES]
        relationships_to_store = [SAMPLE_RELATIONSHIP_ES]
        # embed_batch will be called twice, once for entities, once for relationships
        self.mock_embedding_model.embed_batch.side_effect = [
            [MOCK_EMBEDDING_VECTOR], # For entities
            [[0.5, 0.6, 0.7, 0.8, 0.9]]  # For relationships
        ]

        results = store_embeddings(
            entities=entities_to_store,
            relationships=relationships_to_store,
            entities_map_for_relationships=ENTITIES_MAP_ES
        )

        self.assertEqual(self.mock_embedding_model.embed_batch.call_count, 2)
        self.mock_vector_db.add_items.assert_called_once() # add_items is called once with all items

        db_call_args = self.mock_vector_db.add_items.call_args[0][0]
        self.assertEqual(len(db_call_args), 2) # One entity, one relationship
        self.assertEqual(db_call_args[0]["id"], f"entity_{SAMPLE_ENTITY_ES['id']}")
        self.assertEqual(db_call_args[1]["id"], f"relationship_{SAMPLE_RELATIONSHIP_ES['id']}")

        self.assertEqual(results, {"entities_processed": 1, "relationships_processed": 1})


    def test_store_embeddings_embedding_error(self):
        self.mock_embedding_model.embed_batch.side_effect = Exception("Embedding API Error")
        entities_to_store = [SAMPLE_ENTITY_ES]

        results = store_embeddings(entities=entities_to_store)

        self.mock_embedding_model.embed_batch.assert_called_once()
        self.mock_vector_db.add_items.assert_not_called() # Should not be called if embedding fails
        self.assertEqual(results, {"entities_processed": 0, "relationships_processed": 0})

    def test_store_embeddings_vector_db_error(self):
        self.mock_vector_db.add_items.side_effect = Exception("VectorDB API Error")
        entities_to_store = [SAMPLE_ENTITY_ES]
        self.mock_embedding_model.embed_batch.return_value = [MOCK_EMBEDDING_VECTOR]

        results = store_embeddings(entities=entities_to_store)

        self.mock_embedding_model.embed_batch.assert_called_once()
        self.mock_vector_db.add_items.assert_called_once() # It's called, but then it errors
        # The counts reflect items *processed* for embedding, not necessarily successfully stored if DB fails
        self.assertEqual(results, {"entities_processed": 1, "relationships_processed": 0})


    def test_store_embeddings_clients_unavailable(self):
        with patch('embedding_store.embedding_model_client', None), \
             patch('embedding_store.vector_db_client', None):

            results = store_embeddings(entities=[SAMPLE_ENTITY_ES])
            self.assertEqual(results, {"entities_processed": 0, "relationships_processed": 0})
            self.mock_embedding_model.embed_batch.assert_not_called()
            self.mock_vector_db.add_items.assert_not_called()

    def test_store_embeddings_empty_inputs(self):
        results = store_embeddings(entities=[], relationships=[])
        self.mock_embedding_model.embed_batch.assert_not_called()
        self.mock_vector_db.add_items.assert_not_called()
        self.assertEqual(results, {"entities_processed": 0, "relationships_processed": 0})

        results_none = store_embeddings(entities=None, relationships=None)
        self.mock_embedding_model.embed_batch.assert_not_called()
        self.mock_vector_db.add_items.assert_not_called()
        self.assertEqual(results_none, {"entities_processed": 0, "relationships_processed": 0})


    def test_store_embeddings_relationships_no_map_provided(self):
        relationships_to_store = [SAMPLE_RELATIONSHIP_ES]
        self.mock_embedding_model.embed_batch.return_value = [MOCK_EMBEDDING_VECTOR]

        # entities_map_for_relationships is deliberately omitted
        results = store_embeddings(relationships=relationships_to_store)

        self.mock_embedding_model.embed_batch.assert_called_once()
        call_args = self.mock_embedding_model.embed_batch.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        # Check that the description was made with "Unknown" entity texts
        self.assertIn("Relationship: 'Unknown Source Entity' WORKS_FOR 'Unknown Target Entity'", call_args[0])

        self.mock_vector_db.add_items.assert_called_once()
        self.assertEqual(results, {"entities_processed": 0, "relationships_processed": 1})


if __name__ == '__main__':
    import logging
    logging.disable(logging.CRITICAL)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
