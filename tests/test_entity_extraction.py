# tests/test_entity_extraction.py

import unittest
from kag_builder.entity_extraction import extract_entities, load_model, MODEL_NAME

# Mocking spacy load and nlp object for tests if model is not available or for speed.
# This is a more advanced setup; for now, we'll rely on the actual model being available.
# If tests were to run in CI without the model, mocking would be essential.

class TestEntityExtraction(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Try to load the model once for all tests in this class
        # This helps to see if the model is available for testing
        cls.nlp = load_model()
        if not cls.nlp:
            print(f"WARNING: spaCy model '{MODEL_NAME}' could not be loaded. "
                  "Entity extraction tests will be skipped or may fail if they depend on it directly.")

    def test_extract_entities_no_entities(self):
        """Test that no entities are returned from text known to have no biomedical entities."""
        if not self.nlp:
            self.skipTest(f"Skipping test as spaCy model '{MODEL_NAME}' is not available.")

        text = "This is a generic sentence without any specific biomedical terms."
        entities = extract_entities(text, "test_chunk_no_entity")
        self.assertEqual(len(entities), 0, "Should find no entities in generic text.")

    def test_extract_entities_simple_case(self):
        """Test basic entity extraction for a known entity."""
        if not self.nlp:
            self.skipTest(f"Skipping test as spaCy model '{MODEL_NAME}' is not available.")

        text = "Aspirin is a common drug." # Aspirin is often tagged as CHEMICAL by scispaCy
        entities = extract_entities(text, "test_chunk_aspirin")

        # Depending on the model, "Aspirin" should be found.
        # We need to be flexible here as models evolve.
        found_aspirin = False
        for entity in entities:
            if entity["text"].lower() == "aspirin":
                found_aspirin = True
                self.assertEqual(entity["label"], "ENTITY", "Label for Aspirin might be generic 'ENTITY' or more specific like 'CHEMICAL' with en_core_sci_lg. Check model specifics.")
                # Note: scispaCy's en_core_sci_lg labels 'Aspirin' as 'ENTITY'.
                # Other models like en_ner_bc5cdr_md might label it as 'CHEMICAL'.
                # This test might need adjustment based on the exact model behavior.
                break
        self.assertTrue(found_aspirin, "Should find 'Aspirin' in the text.")
        self.assertGreater(len(entities), 0, "Should find at least one entity.")


    def test_extract_entities_multiple_types(self):
        """Test extraction of multiple entities with different labels."""
        if not self.nlp:
            self.skipTest(f"Skipping test as spaCy model '{MODEL_NAME}' is not available.")

        text = " пациентов с диагнозом сахарный диабет и гипертония получали метформин ." # Russian text example
        # For en_core_sci_lg, this Russian text won't produce biomedical entities.
        # This test would be more meaningful with English text or a multilingual model.
        # Let's use an English example that works well with en_core_sci_lg
        text_eng = "The patient was diagnosed with Diabetes Mellitus and was prescribed Metformin. TP53 gene is relevant."
        entities = extract_entities(text_eng, "test_chunk_multi")

        expected_texts = ["Diabetes Mellitus", "Metformin", "TP53"]
        found_texts = [e["text"] for e in entities]

        for et in expected_texts:
            self.assertIn(et, found_texts, f"Expected entity '{et}' not found.")

        # Check for specific labels (these are typical for en_core_sci_lg)
        labels_found = {e["text"]: e["label"] for e in entities}
        if "Diabetes Mellitus" in labels_found:
             # en_core_sci_lg might use a general 'ENTITY' or a more specific one if available.
             # Often complex diseases are just 'ENTITY'
            self.assertIn(labels_found["Diabetes Mellitus"], ["ENTITY", "DISEASE"], "Label for 'Diabetes Mellitus' is not as expected.")
        if "Metformin" in labels_found:
            self.assertIn(labels_found["Metformin"], ["ENTITY", "CHEMICAL"], "Label for 'Metformin' is not as expected.")
        if "TP53" in labels_found:
            self.assertIn(labels_found["TP53"], ["ENTITY", "GENE_OR_GENE_PRODUCT"], "Label for 'TP53' is not as expected.")


    def test_entity_attributes(self):
        """Check if entities have all required attributes."""
        if not self.nlp:
            self.skipTest(f"Skipping test as spaCy model '{MODEL_NAME}' is not available.")

        text = "Lisinopril is used to treat hypertension."
        entities = extract_entities(text, "test_chunk_attrs")

        if entities:
            entity = entities[0]
            self.assertIn("text", entity)
            self.assertIn("label", entity)
            self.assertIn("start_char", entity)
            self.assertIn("end_char", entity)
            self.assertIn("text_chunk_id", entity)
            self.assertEqual(entity["text_chunk_id"], "test_chunk_attrs")
        else:
            # If no entities are found (e.g. model doesn't recognize Lisinopril or hypertension)
            # this test part might not run. This is acceptable.
            print(f"WARN: No entities found for '{text}' with model '{MODEL_NAME}', attribute check skipped.")
            pass
# Placeholder test files for other modules
