# tests/test_relation_extraction.py
import unittest
from kag_builder.relation_extraction import extract_relations_cooccurrence

class TestRelationExtraction(unittest.TestCase):

    def test_extract_relations_basic_cooccurrence(self):
        sample_entities = [
            {'text': 'Aspirin', 'label': 'CHEMICAL', 'start_char': 0, 'end_char': 7, 'text_chunk_id': 'chunk1'},
            {'text': 'pain relief', 'label': 'MEDICAL_CONDITION', 'start_char': 28, 'end_char': 39, 'text_chunk_id': 'chunk1'}
        ]
        relations = extract_relations_cooccurrence(sample_entities, "chunk1")
        self.assertEqual(len(relations), 1)
        if len(relations) == 1:
            rel = relations[0]
            self.assertEqual(rel['entity1_text'], 'Aspirin')
            self.assertEqual(rel['entity2_text'], 'pain relief')
            self.assertEqual(rel['type'], 'CO-OCCURS_WITH')
            self.assertEqual(rel['text_chunk_id'], 'chunk1')

    def test_no_relations_for_single_entity(self):
        sample_entities = [
            {'text': 'Aspirin', 'label': 'CHEMICAL', 'start_char': 0, 'end_char': 7, 'text_chunk_id': 'chunk1'}
        ]
        relations = extract_relations_cooccurrence(sample_entities, "chunk1")
        self.assertEqual(len(relations), 0)

    def test_no_relations_for_no_entities(self):
        sample_entities = []
        relations = extract_relations_cooccurrence(sample_entities, "chunk1")
        self.assertEqual(len(relations), 0)

if __name__ == '__main__':
    unittest.main()
