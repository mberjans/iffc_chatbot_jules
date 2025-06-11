import yaml
import logging
import os
from typing import Dict, Any, Optional, TypedDict, List

# Configure basic logging for the loader itself
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger(__name__)

# Define TypedDicts for structured configuration
# This makes accessing config values safer and more explicit

class APIKeysConfig(TypedDict, total=False):
    huggingface_hub_token: Optional[str]
    openai_api_key: Optional[str]

class ModelConfig(TypedDict, total=False):
    provider: str
    model_name: str
    task: Optional[str] # For HF pipelines mainly
    model_kwargs: Optional[Dict[str, Any]]

class LLMModelsConfig(TypedDict, total=False):
    default_llm: ModelConfig
    # Allow for other named LLM configurations
    # Example: another_llm: ModelConfig

class EmbeddingModelsConfig(TypedDict, total=False):
    default_embedding: ModelConfig
    # Allow for other named embedding configurations
    # Example: another_embedding: ModelConfig

class VectorDBConfig(TypedDict, total=False):
    provider: str
    path: str
    collection_name: str

class DataPathsConfig(TypedDict, total=False):
    xml_input_directory: str
    processed_output_directory: str

class GeneralSettingsConfig(TypedDict, total=False):
    log_level: str
    chunk_size: int
    chunk_overlap: int

class AppConfig(TypedDict, total=False):
    api_keys: APIKeysConfig
    llm_models: Dict[str, ModelConfig] # More flexible: allows multiple named models
    embedding_models: Dict[str, ModelConfig] # More flexible
    vector_database: VectorDBConfig
    data_paths: DataPathsConfig
    settings: GeneralSettingsConfig

# Global variable to hold the loaded configuration
# Initialize with default empty structures or None
CONFIG: Optional[AppConfig] = None

DEFAULT_CONFIG_FILE = "config.yaml"

def load_config(config_path: str = DEFAULT_CONFIG_FILE) -> AppConfig:
    """
    Loads configuration from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        AppConfig: A dictionary (TypedDict) containing the configuration.

    Raises:
        FileNotFoundError: If the config file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
        ValueError: If essential configuration sections are missing.
    """
    global CONFIG

    logger.info(f"Attempting to load configuration from: {config_path}")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            raw_config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration file {config_path}: {e}")
        raise

    if not raw_config:
        logger.error(f"Configuration file {config_path} is empty or invalid.")
        raise ValueError(f"Configuration file {config_path} is empty or invalid.")

    # Basic validation for essential sections (can be expanded)
    required_sections = [
        "llm_models",
        "embedding_models",
        "vector_database",
        "data_paths",
        "settings"
    ]
    for section in required_sections:
        if section not in raw_config:
            msg = f"Missing essential configuration section '{section}' in {config_path}."
            logger.error(msg)
            raise ValueError(msg)
        if not isinstance(raw_config[section], dict) or not raw_config[section]:
            msg = f"Configuration section '{section}' must be a non-empty dictionary in {config_path}."
            logger.error(msg)
            raise ValueError(msg)

    # Validate specific model configurations (e.g., default_llm and default_embedding must exist)
    if "default_llm" not in raw_config["llm_models"]:
        msg = "Missing 'default_llm' configuration under 'llm_models'."
        logger.error(msg)
        raise ValueError(msg)
    if "default_embedding" not in raw_config["embedding_models"]:
        msg = "Missing 'default_embedding' configuration under 'embedding_models'."
        logger.error(msg)
        raise ValueError(msg)

    # Type casting for safety, though TypedDict doesn't enforce at runtime without tools like mypy
    CONFIG = AppConfig(**raw_config) # type: ignore

    # Resolve API keys: prioritize environment variables, then config file
    if CONFIG.get("api_keys"):
        if "huggingface_hub_token" not in CONFIG["api_keys"] or not CONFIG["api_keys"]["huggingface_hub_token"]:
            CONFIG["api_keys"]["huggingface_hub_token"] = os.getenv("HUGGINGFACE_HUB_TOKEN")
        if "openai_api_key" not in CONFIG["api_keys"] or not CONFIG["api_keys"]["openai_api_key"]:
            CONFIG["api_keys"]["openai_api_key"] = os.getenv("OPENAI_API_KEY")
    else: # Ensure api_keys section exists even if empty in yaml
        CONFIG["api_keys"] = {
            "huggingface_hub_token": os.getenv("HUGGINGFACE_HUB_TOKEN"),
            "openai_api_key": os.getenv("OPENAI_API_KEY")
        }


    logger.info(f"Configuration loaded successfully from {config_path}.")

    # Apply log level from config if present
    log_level_str = CONFIG.get("settings", {}).get("log_level", "INFO").upper()
    if hasattr(logging, log_level_str):
        root_logger = logging.getLogger() # Get the root logger
        root_logger.setLevel(getattr(logging, log_level_str))
        logger.info(f"Root logger level set to {log_level_str} from config.")
    else:
        logger.warning(f"Invalid log_level '{log_level_str}' in config. Using default INFO.")

    return CONFIG


def get_config() -> AppConfig:
    """
    Returns the loaded configuration.
    Loads it if it hasn't been loaded yet using the default path.
    """
    if CONFIG is None:
        logger.info("Configuration not yet loaded. Loading with default path.")
        try:
            load_config()
        except Exception as e:
            # Log the error but allow the program to decide how to handle a missing/bad config
            logger.critical(f"Failed to load default configuration: {e}. CONFIG will be None.")
            # Depending on strictness, could raise here or return a default/empty config.
            # For now, allow CONFIG to remain None if critical failure.
            raise  # Re-raise the exception so the caller knows it failed.
    if CONFIG is None: # Should only happen if load_config above failed critically and didn't raise
        raise RuntimeError("Configuration could not be loaded and is None.")
    return CONFIG

if __name__ == "__main__":
    logger.info("Running config_loader.py as a script for testing.")

    # Test 1: Load default config.yaml
    try:
        config = load_config() # Loads into global CONFIG and returns it
        logger.info(f"Successfully loaded default config. Log level from config: {config.get('settings', {}).get('log_level')}")

        # Print some loaded values
        if config:
            logger.info(f"Default LLM Provider: {config['llm_models']['default_llm'].get('provider')}")
            logger.info(f"Default LLM Model: {config['llm_models']['default_llm'].get('model_name')}")
            logger.info(f"Default Embedding Provider: {config['embedding_models']['default_embedding'].get('provider')}")
            logger.info(f"Default Embedding Model: {config['embedding_models']['default_embedding'].get('model_name')}")
            logger.info(f"Vector DB Path: {config['vector_database'].get('path')}")
            logger.info(f"Chunk Size: {config.get('settings', {}).get('chunk_size')}")

            # Test get_config()
            retrieved_config = get_config()
            assert retrieved_config is config # Should be the same object
            logger.info("get_config() returned the loaded configuration successfully.")

            # Test API key resolution (assuming env vars are not set for this test)
            logger.info(f"HF Token from config/env: {retrieved_config.get('api_keys', {}).get('huggingface_hub_token')}")
            logger.info(f"OpenAI Key from config/env: {retrieved_config.get('api_keys', {}).get('openai_api_key')}")


    except Exception as e:
        logger.error(f"Test 1 Failed: Error loading default config.yaml: {e}", exc_info=True)

    # Test 2: Load non-existent config file
    logger.info("\n--- Test 2: Attempting to load a non-existent config file ---")
    try:
        load_config("non_existent_config.yaml")
    except FileNotFoundError:
        logger.info("Test 2 Passed: Correctly caught FileNotFoundError for non_existent_config.yaml.")
    except Exception as e:
        logger.error(f"Test 2 Failed: Unexpected error: {e}", exc_info=True)

    # Test 3: Create and load a minimal valid config
    minimal_config_content = """
llm_models:
  default_llm:
    provider: "test_provider"
    model_name: "test_llm_model"
embedding_models:
  default_embedding:
    provider: "test_emb_provider"
    model_name: "test_emb_model"
vector_database:
  provider: "test_db"
  path: "./test_db_path"
  collection_name: "test_coll"
data_paths:
  xml_input_directory: "./test_xml"
  processed_output_directory: "./test_proc"
settings:
  log_level: "DEBUG"
  chunk_size: 100
  chunk_overlap: 10
"""
    minimal_config_file = "minimal_test_config.yaml"
    with open(minimal_config_file, "w", encoding="utf-8") as f:
        f.write(minimal_config_content)

    logger.info(f"\n--- Test 3: Attempting to load '{minimal_config_file}' ---")
    try:
        # Reset global CONFIG for this test by setting it to None, forcing a reload
        CONFIG = None
        min_config = load_config(minimal_config_file)
        assert min_config is not None
        assert min_config['settings']['log_level'] == "DEBUG"
        assert min_config['llm_models']['default_llm']['model_name'] == "test_llm_model"
        logger.info(f"Test 3 Passed: Successfully loaded '{minimal_config_file}'. Log level: {min_config['settings']['log_level']}")
        # Check if root logger level was updated (it should be if this test runs after default)
        # Note: The root logger level is sticky. Once set to DEBUG, it stays DEBUG unless set higher.
        current_root_level = logging.getLogger().getEffectiveLevel()
        logger.info(f"Current root logger level after loading minimal_config: {logging.getLevelName(current_root_level)}")

    except Exception as e:
        logger.error(f"Test 3 Failed: Error loading {minimal_config_file}: {e}", exc_info=True)
    finally:
        if os.path.exists(minimal_config_file):
            os.remove(minimal_config_file)

    # Test 4: Create and load an invalid config (missing section)
    invalid_config_content = """
llm_models: # embedding_models section is missing
  default_llm:
    provider: "test_provider"
    model_name: "test_llm_model"
"""
    invalid_config_file = "invalid_test_config.yaml"
    with open(invalid_config_file, "w", encoding="utf-8") as f:
        f.write(invalid_config_content)

    logger.info(f"\n--- Test 4: Attempting to load '{invalid_config_file}' (missing sections) ---")
    try:
        CONFIG = None # Reset
        load_config(invalid_config_file)
    except ValueError as e:
        logger.info(f"Test 4 Passed: Correctly caught ValueError for missing section: {e}")
    except Exception as e:
        logger.error(f"Test 4 Failed: Unexpected error: {e}", exc_info=True)
    finally:
        if os.path.exists(invalid_config_file):
            os.remove(invalid_config_file)

    logger.info("\nConfig loader tests finished.")
