# Placeholder for spaCy setup and model check
# This script will be used to verify that spaCy and the
# en_core_sci_lg model can be loaded correctly.

import spacy

def check_spacy_model():
    model_name = "en_core_sci_lg"
    try:
        nlp = spacy.load(model_name)
        print(f"Successfully loaded spaCy model: {model_name}")

        # Test with a sample sentence
        # doc = nlp("Spinal muscular atrophy (SMA) is a rare genetic neuromuscular disorder.")
        # print("Entities in sample sentence:")
        # for ent in doc.ents:
        #     print(f"- {ent.text} ({ent.label_})")

    except OSError:
        print(f"Could not load spaCy model: {model_name}.")
        print(f"Please ensure you have downloaded it, e.g., via:")
        print(f"python -m spacy download {model_name.replace('-', '_')}") # spacy download uses underscore
        print(f"Or ensure the URL in requirements.txt for the .tar.gz file is correct and accessible.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # The following lines are commented out because the model might not be downloaded yet.
    # To run this check, uncomment these lines after installing requirements.
    # print("Attempting to load spaCy model...")
    # check_spacy_model()
    print("Placeholder script `check_spacy.py` created.")
    print("Uncomment the lines in __main__ to test after installing requirements.")
    pass
