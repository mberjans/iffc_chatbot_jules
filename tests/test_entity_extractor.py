import unittest
from unittest.mock import patch, MagicMock

# Assuming modules are importable (e.g., project root in PYTHONPATH)
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module and classes to be tested/mocked
import entity_extractor
from entity_extractor import (
    Entity, Relationship,
    extract_entities_from_chunk,
    extract_relationships_from_chunk,
    extract_entities_and_relationships
)

# Example entities and relationships for consistent test data
SAMPLE_ENTITIES: list[Entity] = [
    {"id": "e1", "label": "PERSON", "text": "Alice", "attributes": None},
    {"id": "e2", "label": "ORGANIZATION", "text": "Google", "attributes": None}
]
SAMPLE_RELATIONSHIPS: list[Relationship] = [
    {"id": "r1", "source_entity_id": "e1", "target_entity_id": "e2", "label": "WORKS_AT", "attributes": {"confidence": 0.9}}
]

class TestEntityExtractor(unittest.TestCase):

    def setUp(self):
        # This will mock the global 'lightrag_client' instance in the entity_extractor module
        # for the duration of each test method.
        self.mock_client_patcher = patch('entity_extractor.lightrag_client', autospec=True)
        self.mock_lightrag_client = self.mock_client_patcher.start()

        # Ensure that the mock client is not None by default for most tests
        self.mock_lightrag_client.extract_entities = MagicMock(return_value=SAMPLE_ENTITIES)
        self.mock_lightrag_client.extract_relationships = MagicMock(return_value=SAMPLE_RELATIONSHIPS)

    def tearDown(self):
        self.mock_client_patcher.stop()

    def test_extract_entities_from_chunk_success(self):
        text_chunk = "Alice works at Google."
        entities = extract_entities_from_chunk(text_chunk)

        self.mock_lightrag_client.extract_entities.assert_called_once_with(text_chunk)
        self.assertEqual(entities, SAMPLE_ENTITIES)

    def test_extract_entities_from_chunk_api_error(self):
        self.mock_lightrag_client.extract_entities.side_effect = Exception("Simulated API Error")
        text_chunk = "Some text that causes an error."
        entities = extract_entities_from_chunk(text_chunk)

        self.mock_lightrag_client.extract_entities.assert_called_once_with(text_chunk)
        self.assertEqual(entities, []) # Expect empty list on error

    def test_extract_entities_from_chunk_client_unavailable(self):
        # Temporarily set the mocked client to None for this test
        with patch('entity_extractor.lightrag_client', None):
            text_chunk = "Alice works at Google."
            entities = extract_entities_from_chunk(text_chunk)
            self.assertEqual(entities, [])
            # The mocked client's methods should not have been called
            self.mock_lightrag_client.extract_entities.assert_not_called()


    def test_extract_relationships_from_chunk_success(self):
        text_chunk = "Alice works at Google."
        # Assume entities are already extracted
        entities = SAMPLE_ENTITIES
        relationships = extract_relationships_from_chunk(text_chunk, entities)

        self.mock_lightrag_client.extract_relationships.assert_called_once_with(text_chunk, entities)
        self.assertEqual(relationships, SAMPLE_RELATIONSHIPS)

    def test_extract_relationships_from_chunk_no_entities(self):
        text_chunk = "Some text."
        entities: list[Entity] = [] # No entities provided
        relationships = extract_relationships_from_chunk(text_chunk, entities)

        self.mock_lightrag_client.extract_relationships.assert_not_called()
        self.assertEqual(relationships, [])

    def test_extract_relationships_from_chunk_api_error(self):
        self.mock_lightrag_client.extract_relationships.side_effect = Exception("Simulated API Error")
        text_chunk = "Some text."
        entities = SAMPLE_ENTITIES
        relationships = extract_relationships_from_chunk(text_chunk, entities)

        self.mock_lightrag_client.extract_relationships.assert_called_once_with(text_chunk, entities)
        self.assertEqual(relationships, []) # Expect empty list on error

    def test_extract_relationships_from_chunk_client_unavailable(self):
        with patch('entity_extractor.lightrag_client', None):
            text_chunk = "Alice works at Google."
            entities = SAMPLE_ENTITIES
            relationships = extract_relationships_from_chunk(text_chunk, entities)
            self.assertEqual(relationships, [])
            self.mock_lightrag_client.extract_relationships.assert_not_called()


    def test_extract_entities_and_relationships_success(self):
        text_chunk = "Alice works at Google."
        expected_result = {"entities": SAMPLE_ENTITIES, "relationships": SAMPLE_RELATIONSHIPS}

        result = extract_entities_and_relationships(text_chunk)

        self.mock_lightrag_client.extract_entities.assert_called_once_with(text_chunk)
        self.mock_lightrag_client.extract_relationships.assert_called_once_with(text_chunk, SAMPLE_ENTITIES)
        self.assertEqual(result, expected_result)

    def test_extract_entities_and_relationships_entities_fail(self):
        self.mock_lightrag_client.extract_entities.return_value = [] # Simulate no entities found or error
        # Ensure relationship extraction is not called if no entities are found
        self.mock_lightrag_client.extract_relationships.reset_mock()

        text_chunk = "Text where no entities are found."
        expected_result = {"entities": [], "relationships": []}
        result = extract_entities_and_relationships(text_chunk)

        self.mock_lightrag_client.extract_entities.assert_called_once_with(text_chunk)
        self.mock_lightrag_client.extract_relationships.assert_not_called() # Crucial check
        self.assertEqual(result, expected_result)

    def test_extract_entities_and_relationships_relationships_fail(self):
        # Entities are found, but relationship extraction fails
        self.mock_lightrag_client.extract_relationships.return_value = []
        self.mock_lightrag_client.extract_relationships.side_effect = Exception("Relationship API Error")

        text_chunk = "Alice works at Google, but relationship extraction fails."
        # Even if relationship extraction fails, entities should be returned.
        expected_result = {"entities": SAMPLE_ENTITIES, "relationships": []}
        result = extract_entities_and_relationships(text_chunk)

        self.mock_lightrag_client.extract_entities.assert_called_once_with(text_chunk)
        self.mock_lightrag_client.extract_relationships.assert_called_once_with(text_chunk, SAMPLE_ENTITIES)
        self.assertEqual(result, expected_result)

    def test_extract_entities_and_relationships_client_unavailable(self):
        with patch('entity_extractor.lightrag_client', None):
            text_chunk = "Some text."
            result = extract_entities_and_relationships(text_chunk)
            expected_result = {"entities": [], "relationships": []}
            self.assertEqual(result, expected_result)
            self.mock_lightrag_client.extract_entities.assert_not_called()
            self.mock_lightrag_client.extract_relationships.assert_not_called()

if __name__ == '__main__':
    # Disable logging for cleaner test output
    import logging
    logging.disable(logging.CRITICAL)
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
