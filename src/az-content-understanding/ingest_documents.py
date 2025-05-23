import os
import json
from pathlib import Path
import sys

from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain.schema import Document
from langchain_text_splitters import (
    Language,
    MarkdownTextSplitter,
    RecursiveCharacterTextSplitter,
)
from clients import AzureContentUnderstandingClient, get_vector_store


acu_client = AzureContentUnderstandingClient()

# Load analyzer_configs from analyzers.json
with open("analyzers.json", "r") as f:
    analyzer_configs = json.load(f)

    # Iterate through each config and create an analyzer
    for analyzer in analyzer_configs:
        analyzer_id = analyzer["id"]
        template_path = analyzer["template_path"]

        try:
            # Create the analyzer using the content understanding client
            response = acu_client.begin_create_analyzer(
                analyzer_id=analyzer_id, analyzer_template_path=template_path
            )
            result = acu_client.poll_result(response)
            print(f"Successfully created analyzer: {analyzer_id}")

        except Exception as e:
            print(f"Failed to create analyzer: {analyzer_id}")
            print(f"Error: {e}")


# convert json content to markdown chunks
def process_json_content(content, file_location: str):
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN, chunk_size=500, chunk_overlap=100
    )
    # RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(
        [Document(page_content=content[0]["markdown"])]
    )

    return all_splits


analyzer_content_string_splits = []

# Iterate through every file in the data folder, ignoring hidden files
data_dir = Path(__file__).parent.parent.parent / "data"
for file_path in data_dir.iterdir():
    if file_path.is_file() and not file_path.name.startswith("."):

        for analyzer in analyzer_configs:
            analyzer_id = analyzer["id"]
            file_location = str(file_path.resolve())

            # Analyze content
            print(f"Analyzing {file_location} with analyzer {analyzer_id}")
            response = acu_client.begin_analyze(analyzer_id, file_location)
            result = acu_client.poll_result(response)

            json.dump(result, sys.stdout, indent=2)
            string_splits = process_json_content(
                result["result"]["contents"], file_location=file_location
            )

            print(f"Split {file_location} into {str(len(string_splits))} chunks.")
            analyzer_content_string_splits.extend(string_splits)

# Embed and index the docs in vector store:
get_vector_store().add_documents(documents=analyzer_content_string_splits)
