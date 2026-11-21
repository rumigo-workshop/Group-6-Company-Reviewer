# Company Reviewer - Tests Package (`packages/tests`)

This package contains test suites and validation utilities for the Company Reviewer project, specifically the Anthropic Claude API integration used in the research analysis pipeline.

## What the Tests Verify

1. **Environment Configuration & Missing Key Detection (`TestAnthropicKeyValidation`)**:
   - Verifies that `ANTHROPIC_API_KEY` is checked before making API calls.
   - Fails clearly with an actionable message if `ANTHROPIC_API_KEY` is unset, blank, or left as the placeholder (`your_anthropic_api_key_here`).
   - Does not expose the key in logs or error traces.

2. **Live Anthropic API Integration (`TestAnthropicIntegration`)**:
   - Connects to Anthropic's Claude API using the official `anthropic` SDK.
   - Distinguishes clearly between failure modes:
     - **Authentication failure (401)**: Key is invalid, expired, revoked, or rejected.
     - **Permission denied (403)**: Key lacks access to the requested model.
     - **Rate limits (429)**: Quota or concurrency limits exceeded.
     - **Network errors**: DNS, proxy, timeout, or unreachable endpoint.
     - **Server errors (5xx)**: Upstream Anthropic outages.
   - Sends a minimal payload (`max_tokens: 10`, lightweight prompt) using `claude-3-haiku-20240307` to minimize token consumption and API cost.
   - Asserts that Claude returns a successful, non-empty response.

> **Note**: The integration test makes a real HTTP request to Anthropic's API and may incur a minimal API cost (approx. ~10 tokens).

---

## Configuration

Set `ANTHROPIC_API_KEY` in the project root `.env` file or export it in your shell environment:

```bash
# In c:\Rumigo\Group-6-Company-Reviewer\.env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

Optional configuration:
```bash
# Override the Claude model used for testing (default: claude-3-haiku-20240307)
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

---

## Prerequisites & Installation

Ensure Python 3.10+ is installed. Install the test dependencies:

```bash
pip install -r packages/tests/requirements.txt
```

---

## Running the Tests

From the project root (`c:\Rumigo\Group-6-Company-Reviewer`):

### 1. Run all tests (including live API integration)
```bash
pytest packages/tests -v
```

### 2. Run only the key validation tests (no API call, fast local check)
```bash
pytest packages/tests -k "KeyValidation" -v
```

### 3. Run only the live integration test
```bash
pytest packages/tests -k "Integration" -v
```
