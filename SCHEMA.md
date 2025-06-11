# Biomedical Knowledge Graph Schema

This document outlines the preliminary schema for the biomedical Knowledge Graph (KG).

## Entities

Entities are the primary nodes in our KG.

1.  **Disease:**
    *   Description: Represents pathological conditions or illnesses.
    *   Examples: "Diabetes Mellitus Type 2", "Alzheimer's Disease", "COVID-19"
    *   Attributes: `name` (str), `cui` (str, e.g., UMLS CUI), `synonyms` (list of str)

2.  **Drug/Compound:**
    *   Description: Represents therapeutic substances or chemical compounds.
    *   Examples: "Metformin", "Aspirin", "Remdesivir"
    *   Attributes: `name` (str), `drugbank_id` (str), `mechanism_of_action` (str)

3.  **Gene/Protein:**
    *   Description: Represents genes, proteins, and related genetic elements.
    *   Examples: "BRCA1", "TP53", "Insulin Receptor"
    *   Attributes: `symbol` (str), `ncbi_gene_id` (str), `function_summary` (str)

4.  **Symptom:**
    *   Description: Represents subjective or objective evidence of a disease or disorder.
    *   Examples: "Fever", "Cough", "Fatigue"
    *   Attributes: `name` (str), `hpo_id` (str, Human Phenotype Ontology ID)

5.  **MedicalProcedure:**
    *   Description: Represents diagnostic or therapeutic procedures.
    *   Examples: "Biopsy", "X-ray", "Chemotherapy"
    *   Attributes: `name` (str), `snomed_ct_id` (str)

6.  **Anatomy/BodyPart:**
    *   Description: Represents parts of an organism.
    *   Examples: "Lung", "Heart", "Brain"
    *   Attributes: `name` (str), `uberon_id` (str)

7.  **Pathway:**
    *   Description: Represents biological pathways.
    *   Examples: "Glycolysis", "MAPK signaling pathway"
    *   Attributes: `name` (str), `reactome_id` (str)

## Relationships

Relationships are the edges connecting entities in our KG.

1.  **TREATS (Drug/Compound -> Disease):**
    *   Description: Indicates that a drug or compound is used to treat a disease.
    *   Example: (Metformin) -[TREATS]-> (Diabetes Mellitus Type 2)

2.  **CAUSES (Disease/Drug/Compound -> Symptom/Disease):**
    *   Description: Indicates that an entity causes a specific symptom or another disease (e.g., side effect).
    *   Example: (Smoking) -[CAUSES]-> (Lung Cancer); (Drug X) -[CAUSES]-> (Nausea)

3.  **ASSOCIATED_WITH (Gene/Protein <-> Disease):**
    *   Description: Indicates a known association between a gene/protein and a disease. This is a bidirectional relationship.
    *   Example: (BRCA1) -[ASSOCIATED_WITH]-> (Breast Cancer)

4.  **INTERACTS_WITH (Gene/Protein <-> Gene/Protein | Drug/Compound <-> Gene/Protein | Drug/Compound <-> Drug/Compound):**
    *   Description: Represents interactions between genes/proteins, drugs and genes/proteins, or drug-drug interactions. This is typically bidirectional.
    *   Example: (Protein A) -[INTERACTS_WITH]-> (Protein B); (Drug X) -[INTERACTS_WITH]-> (CYP3A4)

5.  **MANIFESTS_AS (Disease -> Symptom):**
    *   Description: Indicates that a disease presents with a particular symptom.
    *   Example: (Influenza) -[MANIFESTS_AS]-> (Fever)

6.  **DIAGNOSES (MedicalProcedure -> Disease):**
    *   Description: Indicates that a medical procedure is used to diagnose a disease.
    *   Example: (Biopsy) -[DIAGNOSES]-> (Cancer)

7.  **LOCATED_IN (Gene/Protein/Disease -> Anatomy/BodyPart):**
    *   Description: Indicates the anatomical location relevant to a gene, protein, or disease.
    *   Example: (Pneumonia) -[LOCATED_IN]-> (Lung)

8.  **PARTICIPATES_IN (Gene/Protein -> Pathway):**
    *   Description: Indicates that a gene or protein is involved in a biological pathway.
    *   Example: (Hexokinase) -[PARTICIPATES_IN]-> (Glycolysis)

9.  **INHIBITS/ACTIVATES (Drug/Compound -> Gene/Protein/Pathway):**
    *   Description: Describes the modulatory effect of a drug or compound on a gene, protein, or pathway.
    *   Example: (Drug Y) -[INHIBITS]-> (Enzyme Z); (Compound Q) -[ACTIVATES]-> (Signaling Pathway X)

This schema is preliminary and can be expanded as the project evolves. Attributes for entities and specific properties for relationships can also be further detailed.
