import unittest
from unittest.mock import patch, MagicMock
import requests.exceptions

# Assuming perplexity_client is in the parent directory or installed
# If perplexity_client is in the parent directory, you might need to adjust sys.path
# For this environment, we'll assume it's discoverable.
from perplexity_client.client import PerplexityAPIClient
from perplexity_client.exceptions import (
    PerplexityAuthenticationError,
    PerplexityAPIError, # For other 4xx errors if we add tests for them
    PerplexityRateLimitError, # For 429 errors if we add tests for them
    PerplexityServerError # For 5xx errors if we add tests for them
)

class TestPerplexityAPIClient(unittest.TestCase):

    def test_initialization(self):
        """Test that the client initializes correctly."""
        api_key = "test_api_key_123"
        client = PerplexityAPIClient(api_key=api_key)
        self.assertEqual(client._api_key, api_key)

    @patch('requests.post')
    def test_chat_completion_success(self, mock_post):
        """Test a successful chat completion call."""
        # Configure the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test-id", "choices": [{"message": {"content": "Hello there!"}}]}
        # raise_for_status() should do nothing for a 200 status
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        api_key = "test_api_key_success"
        client = PerplexityAPIClient(api_key=api_key)

        model = "sonar-medium-chat"
        messages = [{"role": "user", "content": "Hello"}]
        expected_payload = {
            "model": model,
            "messages": messages
        }
        expected_url = "https://api.perplexity.ai/chat/completions"
        expected_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = client.chat_completion(model=model, messages=messages)

        # Assertions
        mock_post.assert_called_once_with(
            expected_url,
            headers=expected_headers,
            json=expected_payload
        )
        self.assertEqual(response, mock_response.json.return_value)

    @patch('requests.post')
    def test_chat_completion_auth_error(self, mock_post):
        """Test that a 401 error raises PerplexityAuthenticationError."""
        # Configure the mock response for 401
        mock_response = MagicMock()
        mock_response.status_code = 401
        # Perplexity API might return a JSON body with an error message
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

        # Set up raise_for_status to raise HTTPError with this mock_response
        http_error = requests.exceptions.HTTPError(response=mock_response)
        http_error.response = mock_response # Ensure the response is attached
        mock_response.raise_for_status.side_effect = http_error

        mock_post.return_value = mock_response

        api_key = "invalid_api_key"
        client = PerplexityAPIClient(api_key=api_key)

        model = "sonar-medium-chat"
        messages = [{"role": "user", "content": "Hello"}]

        with self.assertRaises(PerplexityAuthenticationError) as context:
            client.chat_completion(model=model, messages=messages)

        # Optionally, check the exception message and status code
        self.assertEqual(context.exception.status_code, 401)
        # The message check depends on how you set it up in _make_request
        # If it uses the 'message' from the error JSON:
        self.assertIn("Invalid API key", str(context.exception.message))

    @patch('requests.post')
    def test_chat_completion_rate_limit_error(self, mock_post):
        """Test that a 429 error raises PerplexityRateLimitError."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}
        http_error = requests.exceptions.HTTPError(response=mock_response)
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = PerplexityAPIClient(api_key="test_api_key")
        with self.assertRaises(PerplexityRateLimitError) as context:
            client.chat_completion(model="test-model", messages=[{"role": "user", "content": "Hello"}])
        self.assertEqual(context.exception.status_code, 429)
        self.assertIn("Rate limit exceeded", str(context.exception.message))

    @patch('requests.post')
    def test_chat_completion_other_client_error(self, mock_post):
        """Test that a 400 error raises PerplexityAPIError."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": {"message": "Bad request"}}
        http_error = requests.exceptions.HTTPError(response=mock_response)
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = PerplexityAPIClient(api_key="test_api_key")
        with self.assertRaises(PerplexityAPIError) as context: # Not PerplexityAuthenticationError
            client.chat_completion(model="test-model", messages=[{"role": "user", "content": "Hello"}])
        self.assertEqual(context.exception.status_code, 400)
        self.assertNotIn(context.exception.__class__, [PerplexityAuthenticationError, PerplexityRateLimitError, PerplexityServerError])
        self.assertIn("Bad request", str(context.exception.message))

    @patch('requests.post')
    def test_chat_completion_server_error(self, mock_post):
        """Test that a 500 error raises PerplexityServerError."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": {"message": "Internal server error"}}
        http_error = requests.exceptions.HTTPError(response=mock_response)
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response

        client = PerplexityAPIClient(api_key="test_api_key")
        with self.assertRaises(PerplexityServerError) as context:
            client.chat_completion(model="test-model", messages=[{"role": "user", "content": "Hello"}])
        self.assertEqual(context.exception.status_code, 500)
        self.assertIn("Internal server error", str(context.exception.message))

    @patch('requests.post')
    def test_chat_completion_network_error(self, mock_post):
        """Test that a network error (e.g., Timeout) raises PerplexityAPIError."""
        mock_post.side_effect = requests.exceptions.Timeout("Simulated network timeout")

        client = PerplexityAPIClient(api_key="test_api_key")
        with self.assertRaises(PerplexityAPIError) as context:
            client.chat_completion(model="test-model", messages=[{"role": "user", "content": "Hello"}])
        self.assertIn("Request failed: Simulated network timeout", str(context.exception))
        # Ensure it's the base PerplexityAPIError and not a more specific HTTP-related one
        self.assertEqual(context.exception.__class__, PerplexityAPIError)


    @patch('requests.post')
    def test_chat_completion_non_json_response(self, mock_post):
        """Test handling of a non-JSON response from the API."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Configure json() to raise JSONDecodeError
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Simulated JSON decode error", "doc", 0)
        # raise_for_status() should do nothing for a 200 status
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        client = PerplexityAPIClient(api_key="test_api_key")
        with self.assertRaises(PerplexityAPIError) as context:
            client.chat_completion(model="test-model", messages=[{"role": "user", "content": "Hello"}])

        self.assertIn("Failed to decode JSON response from API.", str(context.exception))
        # Ensure it's the base PerplexityAPIError and not a more specific HTTP-related one
        self.assertEqual(context.exception.__class__, PerplexityAPIError)


if __name__ == '__main__':
    unittest.main()
