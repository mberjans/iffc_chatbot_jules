class PerplexityError(Exception):
    """Base class for all Perplexity API client errors."""
    pass

class PerplexityAPIError(PerplexityError):
    """Raised for general API errors."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"(Status {self.status_code}) {self.message}"
        return self.message

class PerplexityAuthenticationError(PerplexityAPIError):
    """Raised for authentication errors (401)."""
    def __init__(self, message: str = "Authentication failed. Check your API key.", status_code: int = 401):
        super().__init__(message, status_code)

class PerplexityRateLimitError(PerplexityAPIError):
    """Raised for rate limit errors (429)."""
    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", status_code: int = 429):
        super().__init__(message, status_code)

class PerplexityServerError(PerplexityAPIError):
    """Raised for server-side errors (5xx)."""
    def __init__(self, message: str = "Perplexity API server error.", status_code: int = None):
        super().__init__(message, status_code)
