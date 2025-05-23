#!/bin/bash

# Clear the contents of the .env file
> .env

# Append new values to the .env file
echo "AZURE_AI_SERVICE_ENDPOINT=$(azd env get-value AZURE_AI_SERVICE_ENDPOINT)" >> .env
echo "AZURE_OPENAI_ENDPOINT=$(azd env get-value AZURE_OPENAI_ENDPOINT)" >> .env
echo "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=$(azd env get-value AZURE_OPENAI_CHAT_DEPLOYMENT_NAME)" >> .env
echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=$(azd env get-value AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME)" >> .env
echo "AZURE_SEARCH_ENDPOINT=$(azd env get-value AZURE_SEARCH_ENDPOINT)" >> .env
