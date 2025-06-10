import requests
from requests.exceptions import HTTPError, RequestException, JSONDecodeError
from .exceptions import (
    PerplexityAPIError,
    PerplexityAuthenticationError,
    PerplexityRateLimitError,
    PerplexityServerError,
)

class PerplexityAPIClient:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def chat_completion(self, model: str, messages: list, **kwargs) -> dict:
        """
        Generates a chat completion using the Perplexity API.

        Args:
            model: The model to use (e.g., "sonar-medium-chat").
            messages: A list of message objects, e.g., [{"role": "user", "content": "Hello"}].
            **kwargs: Additional optional parameters for the API.

        Returns:
            The API response as a dictionary.
        """
        payload = {
            "model": model,
            "messages": messages,
        }
        payload.update(kwargs)
        return self._make_request(payload)

    def _make_request(self, payload: dict) -> dict:
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            status_code = e.response.status_code
            message = str(e) # Default message
            try:
                # Attempt to get a more specific message from the response body
                error_payload = e.response.json()
                if isinstance(error_payload, dict) and "message" in error_payload:
                    message = error_payload["message"]
            except JSONDecodeError:
                pass # Stick with the default message if JSON decoding fails

            if status_code == 401:
                raise PerplexityAuthenticationError(message=message, status_code=status_code)
            elif status_code == 429:
                raise PerplexityRateLimitError(message=message, status_code=status_code)
            elif 400 <= status_code < 500:
                raise PerplexityAPIError(message=message, status_code=status_code)
            elif status_code >= 500:
                raise PerplexityServerError(message=message, status_code=status_code)
            else: # Should not happen with raise_for_status, but as a fallback
                raise PerplexityAPIError(message=f"Unexpected HTTP error: {message}", status_code=status_code)
        except JSONDecodeError:
            raise PerplexityAPIError("Failed to decode JSON response from API.")
        except RequestException as e:
            raise PerplexityAPIError(f"Request failed: {e}")
