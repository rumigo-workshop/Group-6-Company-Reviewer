"""
Integration and validation tests for Anthropic Claude API.

Verifies:
1. Clear failure when ANTHROPIC_API_KEY is missing or empty.
2. Clear failure when ANTHROPIC_API_KEY is rejected (authentication error).
3. Clear error reporting for network or rate limit issues.
4. Successful non-empty response when a valid key is provided.
"""

import os
import pytest
from packages.tests.anthropic_client import (
    get_anthropic_api_key,
    call_claude_lightweight,
    AnthropicAuthError,
    AnthropicNetworkError,
    AnthropicRateLimitError,
    AnthropicPermissionError,
    AnthropicStatusError,
    AnthropicIntegrationError,
    PLACEHOLDER_KEY,
)


class TestAnthropicKeyValidation:
    """Validation tests for environment configuration without calling external API."""

    def test_missing_api_key_fails_clearly(self, monkeypatch):
        """Verify that get_anthropic_api_key fails clearly when key is missing."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError) as excinfo:
            get_anthropic_api_key()

        error_msg = str(excinfo.value)
        assert "ANTHROPIC_API_KEY is missing or empty" in error_msg
        assert "Please configure ANTHROPIC_API_KEY" in error_msg

    def test_empty_api_key_fails_clearly(self, monkeypatch):
        """Verify that get_anthropic_api_key fails clearly when key is whitespace/empty."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
        with pytest.raises(ValueError) as excinfo:
            get_anthropic_api_key()

        error_msg = str(excinfo.value)
        assert "ANTHROPIC_API_KEY is missing or empty" in error_msg

    def test_placeholder_api_key_fails_clearly(self, monkeypatch):
        """Verify that placeholder key from .env.example is flagged as invalid."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", PLACEHOLDER_KEY)
        with pytest.raises(ValueError) as excinfo:
            get_anthropic_api_key()

        error_msg = str(excinfo.value)
        assert "placeholder value" in error_msg


class TestAnthropicIntegration:
    """
    Real API integration tests for Anthropic Claude.
    Makes actual network requests using the credentials from the environment.
    """

    def test_anthropic_claude_live_call(self):
        """
        Calls Anthropic Claude API using ANTHROPIC_API_KEY from environment/.env.
        Fails clearly if:
        - Key is missing or empty.
        - Key is rejected by Anthropic (401 authentication error).
        - Permission denied (403).
        - Rate limit or network error occurs.
        Passes if a valid non-empty response is returned.
        """
        __tracebackhide__ = True

        # Step 1: Validate key presence without retaining it in locals
        try:
            _ = get_anthropic_api_key()
        except ValueError as err:
            pytest.fail(f"API Key Configuration Error: {err}")

        # Step 2: Make lightweight request to Anthropic Claude
        try:
            response_text = call_claude_lightweight(
                prompt="Respond with only the word 'OK'.",
                max_tokens=10,
            )
            # Step 3: Verify response is valid and non-empty
            assert response_text is not None, "Claude returned None response"
            assert len(response_text) > 0, "Claude returned empty response"
            print(f"\n[Anthropic Integration] Successfully received response: {response_text!r}")

        except AnthropicAuthError as err:
            pytest.fail(f"Anthropic Authentication Failed (Key Rejected): {err}")
        except AnthropicPermissionError as err:
            pytest.fail(f"Anthropic Permission Denied: {err}")
        except AnthropicRateLimitError as err:
            pytest.fail(f"Anthropic Rate Limit Exceeded: {err}")
        except AnthropicNetworkError as err:
            pytest.fail(f"Anthropic Network/Connection Error: {err}")
        except AnthropicStatusError as err:
            pytest.fail(f"Anthropic HTTP Error: {err}")
        except AnthropicIntegrationError as err:
            pytest.fail(f"Anthropic Integration Error: {err}")
        except Exception as err:
            pytest.fail(f"Unexpected error during Anthropic API call: {type(err).__name__}: {err}")
