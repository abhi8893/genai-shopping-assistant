# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]


## [v0.1.0.rc.0] - 2026-03-07

## 1st Release

The core multi-agent LLM system that powers the GenAI Shopping Assistant. This first release delivers a complete conversational shopping experience through specialized agents orchestrated with LangGraph, enabling intelligent product discovery, cart management, and customer support in a single package.

## Features

- 🤖 **Multi-Agent Architecture**: Four specialized agents orchestrated by LangGraph — `RouterAgent` for intelligent routing, `ProductSearchAgent` for discovery, `ShoppingActionsAgent` for cart operations, and `CustomerServiceAgent` for support
- 🔍 **Semantic Product Search**: Intelligent product discovery via Weaviate vector database with natural language query parsing and category/price range filtering
- 🛒 **Cart Management**: Shopping workflow — add/remove items, view cart, manage quantities integrating with `EcomAPIClient`
- 💬 **Dual Interface**: Chat via interactive CLI or modern Gradio web UI for seamless conversational shopping
- 📊 **Built-in Observability**: Optional Langfuse integration for comprehensive LLM tracing and OpenTelemetry logging with automatic OpenAI Agents SDK instrumentation
- 📦 **Main Component**: Serves as the core of the `shopping-assistant` service, integrating ecom-backend for operations and Weaviate for search
- 🔌 **Easy Integration**: Designed to work seamlessly with auxiliary services (`ecom-backend` for commerce, `weaviate` for vectors) and observability platform (`langfuse`)

## NOTE

- This package is the main component of the `shopping-assistant` service
- Currently, only OpenAI is supported as LLM provider
- Currently, since the `ecom-backend` service does not bundle a client library, and it is externally maintained in this package (`shopping-assistant`) as `shopping_assistant/external/ecom_api_client`


