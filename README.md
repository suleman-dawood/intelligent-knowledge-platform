# Intelligent Knowledge Aggregation Platform

A comprehensive multi-agent system for gathering, processing, analyzing, and visualizing knowledge from diverse sources.

## Overview

The Intelligent Knowledge Aggregation Platform is a distributed, multi-agent system designed to collect information from various sources, extract meaningful insights, build knowledge representations, and visualize connections between concepts and entities.

## Architecture

The platform consists of multiple specialized agents, each responsible for a specific aspect of the knowledge processing pipeline:

### Agents

- **Scraper Agent**: Extracts content from websites, PDFs, academic sources, and other data sources.
- **Processor Agent**: Analyzes and extracts meaning from content, including text processing, concept extraction, entity recognition, and sentiment analysis.
- **Knowledge Agent**: Builds and maintains the knowledge graph, handles relation extraction, and performs knowledge validation.
- **Learning Agent**: Improves the knowledge model through continual learning, feedback analysis, and knowledge enhancement.
- **UI Agent**: Handles frontend interactions, providing WebSocket connections and API endpoints for the frontend.

### Components

- **Coordinator**: Manages communication between agents and distributes tasks.
- **Message Broker**: Facilitates asynchronous communication between components.
- **Knowledge Graph Database**: Stores entities, relationships, and metadata.
- **Frontend**: React-based interface for exploring and visualizing the knowledge graph.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- Docker and Docker Compose (for production deployment)
- Neo4j or other graph database

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/intelligent-knowledge-platform.git
   cd intelligent-knowledge-platform
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```
   cd frontend
   npm install
   ```

### Running the Platform

1. Start the coordinator and agents:
   ```
   python coordinator/main.py
   ```

2. Start the frontend:
   ```
   cd frontend
   npm run dev
   ```

3. Access the platform at http://localhost:3000

## Development

### Project Structure

```
intelligent-knowledge-platform/
├── agents/                  # Multi-agent system components
│   ├── scraper/             # Content extraction
│   ├── processor/           # Content analysis
│   ├── knowledge/           # Knowledge graph management
│   ├── learning/            # Learning and enhancement
│   └── ui/                  # UI and API
├── coordinator/             # Agent coordination
├── data_storage/            # Data storage adapters
├── frontend/                # Next.js frontend
└── docker/                  # Docker configuration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Neo4j for graph database
- Hugging Face for NLP models
- React and Next.js for the frontend framework 