import json
import logging
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast
from dataclasses import dataclass

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from content_understanding_client import AzureContentUnderstandingClient


def main():
    load_dotenv()

    credential = DefaultAzureCredential()
    token_provider = get_bearer_token_provider(
        credential, "https://cognitiveservices.azure.com/.default"
    )

    client = AzureContentUnderstandingClient(
        os.getenv("AZURE_AI_SERVICE_ENDPOINT", ""),
        api_version=os.getenv("AZURE_AI_SERVICE_API_VERSION", "2024-12-01-preview"),
        token_provider=token_provider,
        x_ms_useragent="azure-ai-content-understanding-python/content_extraction",
    )
    response = client.begin_analyze(
        os.getenv("ANALYZER_ID", ""), os.getenv("FILE_LOCATION", "")
    )
    result = client.poll_result(
        response,
        timeout_seconds=60 * 60,
        polling_interval_seconds=1,
    )
    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
