import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


def generate_embeddings(chunks: list[str], model_name: str = "all-MiniLM-L6-v2") -> np.ndarray:
  """
  Generates embeddings for a list of text chunks using a SentenceTransformer model.

  Args:
    chunks: A list of text chunks to embed.
    model_name: The name of the SentenceTransformer model to use.
                Defaults to "all-MiniLM-L6-v2".

  Returns:
    A NumPy array containing the embeddings for the input chunks.
  """
  model = SentenceTransformer(model_name)
  embeddings = model.encode(chunks)
  return np.array(embeddings)


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
  """
  Builds a FAISS index from a NumPy array of embeddings.

  Args:
    embeddings: A NumPy array of embeddings.

  Returns:
    A FAISS index.
  """
  dimension = embeddings.shape[1]
  index = faiss.IndexFlatL2(dimension)
  index.add(embeddings)
  return index


def save_faiss_index(index: faiss.Index, path: str):
  """
  Saves a FAISS index to a file.

  Args:
    index: The FAISS index to save.
    path: The path to save the index to.
  """
  faiss.write_index(index, path)


def load_faiss_index(path: str) -> faiss.Index:
  """
  Loads a FAISS index from a file.

  Args:
    path: The path to load the index from.

  Returns:
    The loaded FAISS index.
  """
  index = faiss.read_index(path)
  return index
