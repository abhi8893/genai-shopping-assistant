# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]


## [v0.1.0] - TBD

## 1st Release

FastAPI web service that exposes the multi-agent GenAI Shopping Assistant via REST API. This first release provides HTTP endpoints for conversational shopping interactions, backed by the core `shopping-assistant` package agents.

## Features

- 🌐 **REST API Endpoints**: Health check, service info, and primary `/chat` endpoint for conversational interactions
- 🔀 **Multi-Agent Routing**: Leverages `shopping-assistant` package agents for product search, shopping actions, and customer service
- 🔍 **Semantic Product Search**: (via chat agent) Natural language product discovery via Weaviate
- 🛒 **Shopping Operations**: (via chat agent) Cart management (add/remove items, view cart) via ecom-backend integration
- 📋 **Thread-based Conversations**: Support for multi-turn conversations with `user_id` and `thread_id` parameters
- 📦 **Core Package Integration**: Built on top of `shopping-assistant` package for agent orchestration
- 🔌 **Auxiliary Service Dependencies**: Requires ecom-backend for cart operations and Weaviate for product search

## NOTE

- Streaming chat is not supported in this release — responses are returned as complete messages
- This service leverages the multi-agent architecture from the `shopping-assistant` package (see [packages/shopping-assistant/CHANGELOG.md](../../packages/shopping-assistant/CHANGELOG.md) for core functionality details)
- Requires `shopping-assistant` package, Weaviate, and ecom-backend service to be running

