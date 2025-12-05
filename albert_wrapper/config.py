"""Configuration for Albert API."""

from dataclasses import dataclass

@dataclass
class APIConfig:
    """Configuration for the API connection"""
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0