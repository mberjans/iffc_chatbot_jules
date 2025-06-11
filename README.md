# Perplexity API Client

Python client for the Perplexity AI API.

## Features

- Make chat completion requests to the Perplexity API.
- Handles authentication and common API errors.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from perplexity_client import PerplexityAPIClient
from perplexity_client.exceptions import PerplexityAPIError, PerplexityAuthenticationError

# Replace with your actual API key from https://docs.perplexity.ai/docs/getting-started
# It's best practice to store this as an environment variable (e.g., PPLX_API_KEY)
# and load it using os.environ.get("PPLX_API_KEY")
API_KEY = "YOUR_PPLX_API_KEY"

try:
    if API_KEY == "YOUR_PPLX_API_KEY" or not API_KEY:
        print("Please replace 'YOUR_PPLX_API_KEY' with your actual Perplexity API key.")
        print("You can obtain an API key from https://docs.perplexity.ai/docs/getting-started")
        # For a real application, you might raise an error here or exit.
        # For this example, we'll just print a message.
        # exit() # Uncomment to make it stop execution if key is not set.

    client = PerplexityAPIClient(api_key=API_KEY)

    messages = [
        {"role": "system", "content": "Be precise and concise."},
        {"role": "user", "content": "How many stars are in our galaxy?"}
    ]
    # For available models, see Perplexity documentation. Examples:
    # "sonar-small-chat", "sonar-medium-chat", "sonar-small-online", "sonar-medium-online"
    # "codellama-70b-instruct", "mistral-7b-instruct", "mixtral-8x7b-instruct"
    model = "sonar-medium-chat"

    if API_KEY != "YOUR_PPLX_API_KEY": # Only proceed if a dummy key isn't being used
        response = client.chat_completion(model=model, messages=messages)
        print("API Response:")
        # The response object is a dictionary. You'll typically want to access specific parts of it,
        # for example, the content of the assistant's reply:
        if response and 'choices' in response and response['choices']:
             print(response['choices'][0]['message']['content'])
        else:
             print(response) # Print the full response if the structure is unexpected


        # Example of using optional parameters
        # messages_for_options = [
        #     {"role": "user", "content": "Explain quantum computing in simple terms."}
        # ]
        # response_with_options = client.chat_completion(
        #     model=model,
        #     messages=messages_for_options,
        #     temperature=0.7,
        #     max_tokens=150,
        #     # Other options like:
        #     # frequency_penalty=0.5,
        #     # presence_penalty=0.5,
        #     # return_citations=True,
        #     # return_search_results=True,
        # )
        # print("\nResponse with options:")
        # if response_with_options and 'choices' in response_with_options and response_with_options['choices']:
        #     print(response_with_options['choices'][0]['message']['content'])
        # else:
        #     print(response_with_options)

except PerplexityAuthenticationError:
    print("Authentication failed. Please check your API key. Ensure it's correctly set and valid.")
except PerplexityAPIError as e:
    print(f"An API error occurred: {e.message} (Status code: {e.status_code})")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

```

## Client Interface

### `PerplexityAPIClient(api_key: str)`
Initializes the client with your Perplexity API key.

### `client.chat_completion(model: str, messages: list, **kwargs)`
Sends a chat completion request to the Perplexity API.

*   `model` (str): The model to use (e.g., `"sonar-medium-chat"`).
*   `messages` (list): A list of message objects. Each message object should have a `role` (e.g., `"system"`, `"user"`, `"assistant"`) and `content` (str).
*   `**kwargs`: Optional parameters supported by the Perplexity API, such as:
    *   `temperature` (float)
    *   `max_tokens` (int)
    *   (Refer to the official Perplexity API documentation for a full list.)

Returns a dictionary containing the API response.

### Exceptions

The client can raise the following custom exceptions (defined in `perplexity_client.exceptions`):

*   `PerplexityError(Exception)`: Base error class.
*   `PerplexityAPIError(PerplexityError)`: For general API errors.
    *   `message` (str): Error message.
    *   `status_code` (int): HTTP status code.
*   `PerplexityAuthenticationError(PerplexityAPIError)`: For authentication failures (401).
*   `PerplexityRateLimitError(PerplexityAPIError)`: For rate limit exceeded errors (429).
*   `PerplexityServerError(PerplexityAPIError)`: For Perplexity server-side errors (5xx).

## Running Tests

```bash
python -m unittest discover -s tests
```