# kag_builder/relation_extraction.py

from itertools import combinations

# A very simple placeholder for NLP processing, specifically sentence splitting.
# In a more mature system, this would come from spaCy or another NLP library.
# For now, we'll assume text is passed sentence by sentence or use a simple split.
# from spacy.lang.en import English

# nlp_sentencizer = English()
# nlp_sentencizer.add_pipe("sentencizer")

def extract_relations_cooccurrence(entities: list, text_chunk_id: str = "unknown_chunk", window_size: int = -1) -> list:
    """
    Extracts potential relationships between entities based on co-occurrence within sentences.

    Args:
        entities (list): A list of entity dictionaries, as produced by entity_extraction.py.
                         Each entity dict should have 'text', 'label', 'start_char', 'end_char'.
        text_chunk_id (str): An identifier for the source text chunk.
        window_size (int): The maximum number of tokens between two entities to be considered
                           a co-occurrence. If -1, co-occurrence within the same sentence is used
                           (implicitly, assuming entities are grouped by sentence or the list
                           corresponds to a single sentence). For now, this implementation
                           assumes entities provided are from the same "context" (e.g., sentence).

    Returns:
        list: A list of dictionaries, where each dictionary represents a potential relationship
              and contains 'entity1_text', 'entity1_label', 'entity2_text', 'entity2_label',
              'type' (e.g., 'CO-OCCURS_WITH'), and 'text_chunk_id'.
    """
    relations = []

    # This basic version assumes the list of entities is already from a relevant context (e.g., one sentence).
    # A more advanced version would take the raw text, use NLP to split into sentences,
    # then process entities per sentence.
    # For now, we simply look for pairs in the provided list.

    if len(entities) < 2:
        return []

    # Generate all unique pairs of entities
    for ent1, ent2 in combinations(entities, 2):
        # Simple co-occurrence: if two entities appear, they might be related.
        # The 'type' is generic here; specific relation classification is a more complex task.
        relations.append({
            "entity1_text": ent1["text"],
            "entity1_label": ent1["label"],
            "entity2_text": ent2["text"],
            "entity2_label": ent2["label"],
            "type": "CO-OCCURS_WITH", # Placeholder relationship type
            "text_chunk_id": text_chunk_id
        })

    return relations

if __name__ == '__main__':
    print("Attempting to run relation extraction test...")

    # Sample entities (typically this would come from extract_entities)
    sample_entities_1 = [
        {'text': 'Aspirin', 'label': 'CHEMICAL', 'start_char': 0, 'end_char': 7, 'text_chunk_id': 'chunk1'},
        {'text': 'pain relief', 'label': 'MEDICAL_CONDITION', 'start_char': 28, 'end_char': 39, 'text_chunk_id': 'chunk1'},
        {'text': 'blood clots', 'label': 'MEDICAL_CONDITION', 'start_char': 55, 'end_char': 66, 'text_chunk_id': 'chunk1'}
    ]

    print(f"\nProcessing entities: {sample_entities_1}")
    extracted_relations_1 = extract_relations_cooccurrence(sample_entities_1, "chunk1")
    if extracted_relations_1:
        print("\nExtracted Relations (1):")
        for rel in extracted_relations_1:
            print(rel)
    else:
        print("No relations extracted for sample_entities_1.")

    sample_entities_2 = [
        {'text': 'Interleukin-6', 'label': 'GENE_OR_GENE_PRODUCT', 'start_char': 0, 'end_char': 13, 'text_chunk_id': 'chunk2'},
        {'text': 'Mycophenolate mofetil', 'label': 'CHEMICAL', 'start_char': 52, 'end_char': 75, 'text_chunk_id': 'chunk2'},
        {'text': 'TP53', 'label': 'GENE_OR_GENE_PRODUCT', 'start_char': 108, 'end_char': 112, 'text_chunk_id': 'chunk2'}
    ]
    print(f"\nProcessing entities: {sample_entities_2}")
    extracted_relations_2 = extract_relations_cooccurrence(sample_entities_2, "chunk2")
    if extracted_relations_2:
        print("\nExtracted Relations (2):")
        for rel in extracted_relations_2:
            print(rel)
    else:
        print("No relations extracted for sample_entities_2.")

    # Example with only one entity
    sample_entities_3 = [
        {'text': 'Metformin', 'label': 'CHEMICAL', 'start_char': 0, 'end_char': 9, 'text_chunk_id': 'chunk3'}
    ]
    print(f"\nProcessing entities: {sample_entities_3}")
    extracted_relations_3 = extract_relations_cooccurrence(sample_entities_3, "chunk3")
    if extracted_relations_3:
        print("\nExtracted Relations (3):")
        for rel in extracted_relations_3:
            print(rel)
    else:
        print("No relations extracted for sample_entities_3 (as expected).")

    # Example with no entities
    sample_entities_4 = []
    print(f"\nProcessing entities: {sample_entities_4}")
    extracted_relations_4 = extract_relations_cooccurrence(sample_entities_4, "chunk4")
    if extracted_relations_4:
        print("\nExtracted Relations (4):")
        for rel in extracted_relations_4:
            print(rel)
    else:
        print("No relations extracted for sample_entities_4 (as expected).")

    print("\nRelation extraction module basic test finished.")
