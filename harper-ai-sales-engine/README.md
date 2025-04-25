# Harper AI Sales Engine

An AI-powered insurance brokerage system designed to transform the commercial insurance market by automating processes that currently run on pre-internet systems.

## Overview

This project implements an end-to-end AI-driven sales engine for commercial insurance, capable of guiding customers through the entire application process from lead to binded policy. The system uses state-of-the-art AI technologies to create natural and efficient customer interactions across multiple channels.

## Architecture

The Harper AI Sales Engine consists of several interconnected components:

### Core Components

- **Voice AI System**: Handles real-time voice conversations with customers for up to 15+ minutes
- **Multi-Channel Communication**: Manages interactions across voice, email, text messages, chat, and web forms
- **Document Parser**: Extracts data from insurance forms and documents
- **Recommendation Engine**: Determines optimal insurance carriers based on customer data
- **AI Agents**: Orchestrates follow-up communications and information collection
- **Lead Scoring**: Prioritizes leads for the underwriting queue
- **Customer Portal**: Allows customers to track applications in real-time
- **Harper Hub Integration**: Handles human-in-the-loop escalation paths

### Technology Stack

- **Languages**: TypeScript/Node.js and Python
- **AI/ML Frameworks**:
  - Mastra and LangGraph for AI agent orchestration
  - Model Context Protocol (MCP) for LLM interaction management
  - LlamaParser for document extraction
  - OpenAI Function Calling API for web-based agent actions
- **Communication Infrastructure**:
  - LiveKit for real-time voice AI interactions
  - Twilio for telephony infrastructure
  - OpenPhone for voice transcripts
- **Data Storage**:
  - PostgreSQL for relational data
  - Redis for high-performance caching
  - Vector store with hybrid lexical-semantic search
  - Zep AI for graph-based conversation memory
- **Core Engineering**:
  - Temporal workers for distributed compute offloading

## Repository Structure

```
harper-ai-sales-engine/
├── config/                   # Configuration management
├── core/                     # Shared libraries and core logic
│   ├── node-shared/          # Shared TypeScript modules
│   ├── python-shared/        # Shared Python modules 
│   └── data-models/          # Data schemas and models
├── docs/                     # Documentation
├── infra/                    # Infrastructure as Code
├── scripts/                  # Utility scripts
├── services/                 # Individual services
│   ├── voice-ai/             # Voice conversation system
│   ├── agents/               # AI agent orchestration
│   ├── customer-portal/      # Customer-facing web application
│   ├── recommendation-engine/# Insurance carrier recommendations
│   ├── lead-scoring/         # Lead prioritization
│   ├── document-parser/      # Document parsing and extraction
│   └── harper-hub-integration/# Operational platform integration
└── tests/                    # End-to-end and integration tests
```

## Getting Started

### Prerequisites

- Node.js v18+
- Python 3.10+
- Docker and Docker Compose
- PostgreSQL
- Redis

### Installation

1. Clone the repository
   ```
   git clone git@github.com:harper-insurance/harper-ai-sales-engine.git
   cd harper-ai-sales-engine
   ```

2. Install Node.js dependencies
   ```
   npm install
   ```

3. Install Python dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Start development environment
   ```
   docker-compose -f infra/docker-compose.yml up -d
   ```

6. Start individual services as needed
   ```
   cd services/customer-portal
   npm run dev
   ```

## Development Guidelines

- Follow the included linting and formatting rules
- Write tests for all new features
- Document API endpoints and data models
- Follow the Git workflow described in the contribution guidelines

## License

Proprietary - All rights reserved

## Contact

For any questions or issues, please contact the development team.
