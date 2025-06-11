# kag_builder/entity_extraction.py

import spacy

# Placeholder for loading the spaCy model.
# In a real scenario, the model would be loaded once and reused.
NLP = None
MODEL_NAME = "en_core_sci_lg" # As defined in requirements

def load_model():
    """Loads the spaCy model.

    Returns:
        spacy.Language: The loaded spaCy language model, or None if loading fails.
    """
    global NLP
    if NLP is None:
        try:
            NLP = spacy.load(MODEL_NAME)
            # print(f"Successfully loaded spaCy model: {MODEL_NAME}") # Keep console clean for library use
        except OSError:
            # print(f"Error: Could not load spaCy model '{MODEL_NAME}'.")
            # print(f"Please ensure the model is installed, e.g., by running:")
            # print(f"  pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_lg-0.5.3.tar.gz")
            # print(f"Or ensure it's downloaded if you installed spacy separately and then downloaded the model:")
            # print(f"  python -m spacy download {MODEL_NAME.replace('-', '_')}")
            NLP = None # Ensure NLP remains None if loading failed
        except Exception as e:
            # print(f"An unexpected error occurred while loading the model: {e}")
            NLP = None
    return NLP

def extract_entities(text: str, text_chunk_id: str = "unknown_chunk") -> list:
    """
    Extracts biomedical entities from a given text string.

    Args:
        text (str): The input text to process.
        text_chunk_id (str): An identifier for the source text chunk (for future indexing).

    Returns:
        list: A list of dictionaries, where each dictionary represents an entity
              and contains 'text', 'label' (entity type), 'start_char', 'end_char',
              and 'text_chunk_id'.
              Returns an empty list if the model isn't loaded or no entities are found.
    """
    nlp_model = load_model()
    if not nlp_model:
        # print("Entity extraction cannot proceed as the spaCy model is not loaded.")
        return []

    doc = nlp_model(text)
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char,
            "text_chunk_id": text_chunk_id # For mutual indexing
        })

    # if not entities:
    #     print(f"No entities found in text: '{text[:100]}...'")
    # else:
    #     print(f"Extracted {len(entities)} entities.")

    return entities

if __name__ == '__main__':
    # This is for basic testing of this module.
    # IMPORTANT: This __main__ block assumes you have run:
    # pip install -r requirements.txt
    # which includes spacy and en_core_sci_lg.
    # If the model is not found, it will print an error and skip tests.

    print("Attempting to run entity extraction test...")

    # Attempt to load the model first (normally done implicitly by extract_entities)
    # This also allows us to see the model loading message if it's the first time.
    if load_model():
        print(f"spaCy model '{MODEL_NAME}' loaded successfully for __main__ test.")

        sample_text_1 = "Aspirin is commonly used for pain relief and to prevent blood clots."
        print(f"\nProcessing text: '{sample_text_1}'")
        extracted_entities_1 = extract_entities(sample_text_1, "sample_doc_1_chunk_1")
        if extracted_entities_1:
            print("\nExtracted Entities (1):")
            for entity in extracted_entities_1:
                print(entity)
        else:
            print("No entities extracted for sample_text_1.")

        sample_text_2 = ("Interleukin-6 (IL-6) is a pro-inflammatory cytokine and Mycophenolate mofetil "
                         "is an immunosuppressive drug. TP53 is a tumor suppressor gene.")
        print(f"\nProcessing text: '{sample_text_2}'")
        extracted_entities_2 = extract_entities(sample_text_2, "sample_doc_1_chunk_2")
        if extracted_entities_2:
            print("\nExtracted Entities (2):")
            for entity in extracted_entities_2:
                print(entity)
        else:
            print("No entities extracted for sample_text_2.")

        sample_text_3 = "Diabetes Mellitus Type 2 is often treated with Metformin. BRCA1 is associated with Breast Cancer."
        print(f"\nProcessing text: '{sample_text_3}'")
        extracted_entities_3 = extract_entities(sample_text_3, "sample_doc_2_chunk_1")
        if extracted_entities_3:
            print("\nExtracted Entities (3):")
            for entity in extracted_entities_3:
                print(entity)
        else:
            print("No entities extracted for sample_text_3.")

        # Test with a sentence that might not have scispaCy entities
        sample_text_4 = "The patient reported to the clinic with a headache."
        print(f"\nProcessing text: '{sample_text_4}'")
        extracted_entities_4 = extract_entities(sample_text_4, "sample_doc_3_chunk_1")
        if extracted_entities_4:
            print("\nExtracted Entities (4):")
            for entity in extracted_entities_4:
                print(entity)
        else:
            print("No entities extracted for sample_text_4 (as expected for some general sentences).")

    else:
        print(f"\nSkipping __main__ entity extraction examples as spaCy model '{MODEL_NAME}' failed to load.")
        print("Please ensure you have installed all dependencies from requirements.txt, including the model tar.gz file.")

    print("\nEntity extraction module basic test finished.")
