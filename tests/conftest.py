# tests/conftest.py
# This file can be used for shared pytest fixtures in the future.
# For example, loading the spaCy model once for the entire test session.

# import pytest
# from kag_builder.entity_extraction import load_model, MODEL_NAME

# @pytest.fixture(scope="session")
# def spacy_nlp_model():
#     print(f"Attempting to load spaCy model '{MODEL_NAME}' for test session...")
#     nlp = load_model()
#     if nlp is None:
#         pytest.skip(f"Failed to load spaCy model '{MODEL_NAME}', many tests will be skipped.")
#     return nlp
