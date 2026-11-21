"""
Anthropic Claude API client and environment validation helper.
Used by integration tests and research pipeline services.
"""

import os
from pathlib import Path
from typing import Optional
import anthropic
import dotenv

DEFAULT_MODEL = "claude-3-haiku-20240307"
PLACEHOLDER_KEY = "your_anthropic_api_key_here"

_ENV_LOADED = False


class AnthropicIntegrationError(Exception):
    """Base exception for Anthropic integration errors."""
    pass


class AnthropicAuthError(AnthropicIntegrationError):
    """Raised when Anthropic rejects the API key (401 / authentication failure)."""
    pass


class AnthropicPermissionError(AnthropicIntegrationError):
    """Raised when Anthropic rejects access due to permissions (403)."""
    pass


class AnthropicRateLimitError(AnthropicIntegrationError):
    """Raised when Anthropic rate limit is exceeded (429)."""
    pass


class AnthropicNetworkError(AnthropicIntegrationError):
    """Raised on connection / network failures when reaching Anthropic API."""
    pass


class AnthropicStatusError(AnthropicIntegrationError):
    """Raised when Anthropic returns an unexpected HTTP status code."""
    pass


def load_project_env() -> None:
    """
    Loads environment variables from .env located at repo root or parent directories.
    Does not overwrite already set environment variables.
    """
    # Look for .env in current directory and parent directories
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        env_file = parent / ".env"
        if env_file.is_file():
            dotenv.load_dotenv(dotenv_path=env_file, override=False)
            return

    # Fallback to standard dotenv search
    dotenv.load_dotenv(override=False)


# Auto-load environment once at module import
load_project_env()


def get_anthropic_api_key() -> str:
    """
    Retrieves ANTHROPIC_API_KEY from environment.
    Fails clearly with ValueError if missing, empty, or set to placeholder.
    Never exposes or returns partial secrets in error messages.
    """
    __tracebackhide__ = True
    key = os.getenv("ANTHROPIC_API_KEY")

    if not key or not key.strip():
        raise ValueError(
            "ANTHROPIC_API_KEY is missing or empty. "
            "Please configure ANTHROPIC_API_KEY in your environment or root .env file."
        )

    clean_key = key.strip()
    if clean_key == PLACEHOLDER_KEY:
        raise ValueError(
            "ANTHROPIC_API_KEY is set to placeholder value ('your_anthropic_api_key_here'). "
            "Please replace it with a valid Anthropic API key in your .env file."
        )

    return clean_key


def call_claude_lightweight(
    model: Optional[str] = None,
    prompt: str = "Ping",
    max_tokens: int = 10,
    api_key_override: Optional[str] = None,
) -> str:
    """
    Executes a minimal, lightweight request to Anthropic Claude to verify connectivity.
    Uses a small token budget (default 10 tokens) to minimize API cost.

    Differentiates between:
    - Authentication errors (invalid/rejected key)
    - Permission errors (insufficient permissions / forbidden)
    - Rate limit errors (429)
    - Network/connection errors
    - Other API status errors

    Returns the string text response from Claude.
    """
    __tracebackhide__ = True

    resolved_key = api_key_override or get_anthropic_api_key()
    target_model = model or os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)

    try:
        client = anthropic.Anthropic(api_key=resolved_key)
        # Clear local reference to avoid leaving it in stack
        del resolved_key
        response = client.messages.create(
            model=target_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text content safely
        text_pieces = []
        for block in response.content:
            if getattr(block, "type", None) == "text":
                text_pieces.append(block.text)

        result_text = "".join(text_pieces).strip()
        if not result_text:
            raise AnthropicIntegrationError("Anthropic returned an empty text response.")

        return result_text

    except anthropic.AuthenticationError as e:
        raise AnthropicAuthError(
            "Anthropic API key was rejected (Authentication Error 401). "
            "The key is invalid, revoked, or formatted incorrectly. "
            f"Details: {e.message}"
        ) from None
    except anthropic.PermissionDeniedError as e:
        raise AnthropicPermissionError(
            "Anthropic API request was forbidden (Permission Denied 403). "
            "Check account permissions and model access. "
            f"Details: {e.message}"
        ) from None
    except anthropic.RateLimitError as e:
        raise AnthropicRateLimitError(
            f"Anthropic API rate limit exceeded (429). Details: {e.message}"
        ) from None
    except anthropic.APIConnectionError as e:
        raise AnthropicNetworkError(
            f"Network error connecting to Anthropic API endpoint: {e}"
        ) from None
    except anthropic.APIStatusError as e:
        raise AnthropicStatusError(
            f"Anthropic API returned error status {e.status_code}: {e.message}"
        ) from None
    except anthropic.APIError as e:
        raise AnthropicIntegrationError(
            f"Anthropic API error ({type(e).__name__}): {e}"
        ) from None
