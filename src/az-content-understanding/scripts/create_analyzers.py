import os
import uuid

from pathlib import Path
from dotenv import find_dotenv, load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from content_understanding_client import AzureContentUnderstandingClient

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

analyzer_configs = [
    {
        "id": "doc-analyzer" + str(uuid.uuid4()),
        "template_path": "../../analyzer_templates/content_document.json",
        "location": Path("../../analyzer_templates/sample_layout.pdf"),
    },
    {
        "id": "image-analyzer" + str(uuid.uuid4()),
        "template_path": "../../analyzer_templates/image_chart_diagram_understanding.json",
        "location": Path("../../analyzer_templates/sample_report.pdf"),
    },
]

# Iterate through each config and create an analyzer
for analyzer in analyzer_configs:
    analyzer_id = analyzer["id"]
    template_path = analyzer["template_path"]

    try:

        # Create the analyzer using the content understanding client
        response = client.begin_create_analyzer(
            analyzer_id=analyzer_id, analyzer_template_path=template_path
        )
        result = client.poll_result(response)
        print(f"Successfully created analyzer: {analyzer_id}")

    except Exception as e:
        print(f"Failed to create analyzer: {analyzer_id}")
        print(f"Error: {e}")
