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
- **Message Broker (RabbitMQ)**: Facilitates asynchronous communication between components.
- **Knowledge Graph Database (Neo4j)**: Stores entities, relationships, and metadata.
- **Document Database (MongoDB)**: Stores raw content and processed documents.
- **Vector Database (Weaviate)**: Stores and retrieves vector embeddings for semantic search.
- **In-Memory Cache (Redis)**: Caches frequently accessed data for performance.
- **Frontend**: React/Next.js-based interface for exploring and visualizing the knowledge graph.

## Getting Started

### 🔑 Required API Keys & Accounts

| Service | Required | Free Tier | Purpose | Sign Up Link |
|---------|----------|-----------|---------|--------------|
| **DeepSeek** | ✅ Yes | Yes | LLM for entity recognition, sentiment analysis | [platform.deepseek.com](https://platform.deepseek.com/) |

### 🌐 Optional Cloud Services (for production)

| Service | Purpose | Free Tier | Sign Up Link |
|---------|---------|-----------|--------------|
| **MongoDB Atlas** | Cloud database | 512MB | [cloud.mongodb.com](https://cloud.mongodb.com/) |
| **Neo4j AuraDB** | Cloud graph database | Available | [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/) |
| **Redis Cloud** | Cloud cache | 30MB | [redis.com/try-free](https://redis.com/try-free/) |
| **CloudAMQP** | Cloud message broker | Available | [cloudamqp.com](https://www.cloudamqp.com/) |
| **Weaviate Cloud** | Cloud vector database | Available | [console.weaviate.cloud](https://console.weaviate.cloud/) |

### Prerequisites

#### Required Software
- **Python 3.10+**: [Download](https://www.python.org/downloads/)
- **Node.js 16+**: [Download](https://nodejs.org/en/download/)
- **Git**: [Download](https://git-scm.com/downloads)

#### Infrastructure (Choose one)
- **Option A**: Docker Desktop [Download](https://www.docker.com/products/docker-desktop/) (recommended for beginners)
- **Option B**: Local installation of MongoDB, Neo4j, Redis, RabbitMQ, and Weaviate

### Installation

#### 🚀 Quick Setup (Recommended)

**Linux/Mac:**
```bash
git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
cd intelligent-knowledge-platform
chmod +x setup.sh && ./setup.sh
```

**Windows:**
```cmd
git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
cd intelligent-knowledge-platform
setup.bat
```

The setup script will:
- Check prerequisites (Python 3.10+, Node.js 16+)
- Create virtual environment and install dependencies
- Set up configuration files
- Guide you through getting your DeepSeek API key

#### 📋 Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
   cd intelligent-knowledge-platform
   ```

2. **Set up environment:**
   ```bash
   cp config.env.example .env
   ```
   **IMPORTANT:** Get your DeepSeek API key from [https://platform.deepseek.com/](https://platform.deepseek.com/) and add it to `.env`:
   ```
   DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
   ```

3. **Install Python dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies:**
   ```bash
   cd frontend && npm install && cd ..
   ```

#### Docker Deployment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/intelligent-knowledge-platform.git
   cd intelligent-knowledge-platform
   ```

2. Modify the `docker-compose.yml` file if needed.

3. Build and start the containers:
   ```
   docker-compose up -d
   ```

### Running the Platform

#### Local Development

1. Start the coordinator and agents:
   ```
   python run_local.py --scraper-agents=1 --processor-agents=1 --knowledge-agents=1 --learning-agents=1 --ui-agents=1
   ```

2. Start the frontend:
   ```
   cd frontend
   npm run dev
   ```

3. Access the platform at http://localhost:3000

#### Docker Deployment

1. Once the containers are running, access the platform at http://localhost:3000
2. Access the RabbitMQ management UI at http://localhost:15672 (default credentials: guest/guest)
3. Access the Neo4j browser at http://localhost:7474 (default credentials: neo4j/password)

## Using the Platform

### Adding Content

1. Navigate to the Search page
2. Use the "Add Content" button to submit a URL, PDF, or text for processing
3. The system will automatically extract content, process it, and add it to the knowledge graph

### Exploring the Knowledge Graph

1. Go to the Explore page to visualize the knowledge graph
2. Click on nodes to view details and explore connections
3. Use the search functionality to find specific entities or concepts

### Searching Knowledge

1. Use the Search page to search for information across the knowledge graph
2. Results will include relevant entities, concepts, and documents
3. Click on results to see details and explore related information

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
│   ├── src/                 # Frontend source code
│   │   ├── app/             # Next.js app router
│   │   ├── components/      # Reusable UI components
│   │   └── lib/             # Frontend utilities
├── data/                    # Data storage directory
└── docker/                  # Docker configuration
```

### Available Agent Types

- **Scraper Agent**: Implemented with web, PDF, and academic scraping capabilities
- **Processor Agent**: Text processing, concept extraction, entity recognition, and sentiment analysis
- **Knowledge Agent**: Knowledge graph building, relation extraction, and knowledge validation
- **Learning Agent**: Feedback analysis, knowledge enhancement, and model training
- **UI Agent**: API endpoints, WebSockets, search, and visualization management

### Adding New Agent Types

1. Create a new directory under `agents/`
2. Implement the agent interface with a main agent class
3. Add any specialized modules needed
4. Update the `coordinator/agent_manager.py` to recognize the new agent type
5. Update the `run_local.py` script to support starting the new agent type

## Troubleshooting

### Common Issues

1. **Connection Issues**: Ensure all services (MongoDB, Neo4j, Redis, RabbitMQ) are running and accessible. Check the connection parameters in your `.env` file.

2. **Agent Startup Failures**: Check the logs for error messages. Common issues include missing dependencies or configuration errors.

3. **Task Processing Errors**: Tasks might fail due to invalid input data or missing dependencies. Check the task queue status and error messages.

4. **Frontend Connectivity**: Ensure the UI agent is running and the frontend is configured with the correct API and WebSocket URLs.

### Debugging

- Use `LOG_LEVEL=DEBUG` in your `.env` file for more detailed logs
- Check coordinator and agent logs for error messages
- Use the RabbitMQ management interface to inspect queues and messages
- Monitor the Neo4j and MongoDB databases for unexpected data or performance issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Neo4j for graph database
- DeepSeek for LLM capabilities
- React and Next.js for the frontend framework 