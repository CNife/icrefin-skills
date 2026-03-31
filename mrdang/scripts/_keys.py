# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Secure API key loading for MR Dang scripts.

Priority: environment variable > .env file (current working directory)
Never prints or exposes key values — errors use masked representations.
"""

import os
from pathlib import Path


def _load_dotenv() -> dict[str, str]:
    """Parse .env file from current working directory.

    Only supports simple KEY=VALUE lines (no shell interpolation, no quotes needed).
    Returns empty dict if file doesn't exist.
    """
    env_path = Path.cwd() / ".env"
    if not env_path.is_file():
        return {}

    result: dict[str, str] = {}
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key:
                result[key] = value
    return result


def get_tushare_token() -> str:
    """Get Tushare API token.

    Search order:
    1. TUSHARE_TOKEN environment variable
    2. TUSHARE_API_KEY environment variable
    3. .env file in current working directory

    Raises ValueError if no token found.
    """
    # Check environment variables first
    token = os.environ.get("TUSHARE_TOKEN") or os.environ.get("TUSHARE_API_KEY")
    if token:
        return token

    # Fall back to .env file
    dotenv = _load_dotenv()
    token = dotenv.get("TUSHARE_TOKEN") or dotenv.get("TUSHARE_API_KEY")
    if token:
        return token

    raise ValueError(
        "Tushare token not found. Set TUSHARE_TOKEN or TUSHARE_API_KEY "
        "as an environment variable, or add it to a .env file in the "
        f"current directory ({Path.cwd()})."
    )


def get_jina_api_key() -> str | None:
    """Get Jina API key (optional, increases rate limits).

    Search order:
    1. JINA_API_KEY environment variable
    2. .env file in current working directory

    Returns None if not found (Jina search works without a key, with lower limits).
    """
    key = os.environ.get("JINA_API_KEY")
    if key:
        return key

    dotenv = _load_dotenv()
    return dotenv.get("JINA_API_KEY")
