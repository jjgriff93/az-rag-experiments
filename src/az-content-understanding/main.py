import json
import logging
import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langchain import hub
from langchain.schema import Document
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, MessagesState, StateGraph
from typing_extensions import List
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from clients import get_vector_store


load_dotenv()

credential = DefaultAzureCredential()
token_provider = get_bearer_token_provider(
    credential, "https://cognitiveservices.azure.com/.default"
)

llm = AzureChatOpenAI(
    api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION", "2024-12-01-preview"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    azure_ad_token_provider=token_provider,
    temperature=0.7,
)

vector_store = get_vector_store()


class State(MessagesState):
    context: List[Document]


@tool(response_format="content_and_artifact")
def retrieve(query: str):
    """Retrieve information related to a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


# Step 1: Generate an AIMessage that may include a tool-call to be sent.
def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response]}


# Step 2: Execute the retrieval.
tools = ToolNode([retrieve])


# Step 3: Generate a response using the retrieved content.
def generate(state: MessagesState):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{docs_content}"
    )
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    context = []
    for tool_message in tool_messages:
        context.extend(tool_message.artifact)

    return {"messages": [response], "context": context}


# Setup rag graph
def setup_rag_graph():
    graph_builder = StateGraph(MessagesState)

    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    graph = graph_builder.compile()
    return graph


# Trigger conversational search
def conversational_search(graph, query):
    for step in graph.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()


def main():
    rag_graph = setup_rag_graph()
    while True:
        query = input("Enter your query: ")
        if query == "":
            break
        conversational_search(rag_graph, query)


if __name__ == "__main__":
    main()
