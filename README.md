# Intelligent Knowledge Aggregation Platform

An advanced personal knowledge management system using a multi-agent architecture to scrape, process, analyze, and present information from diverse sources. The platform creates a dynamic knowledge graph that evolves with user interaction, providing personalized learning recommendations and content synthesis.

## Project Overview

This platform uses a multi-agent architecture to:
- Scrape content from various sources (web pages, PDFs, videos, etc.)
- Process and analyze content to extract key concepts and relationships
- Build a dynamic knowledge graph connecting related concepts
- Provide personalized learning recommendations
- Present information through an interactive user interface

## Architecture

### Core Components

- **Agent Orchestration System**: Coordinates all agents and manages task distribution
- **Specialized Agents**: Dedicated to specific tasks (scraping, processing, knowledge management, etc.)
- **Knowledge Storage**: Multiple databases for different data types (graph, vector, document)
- **Communication Layer**: Enables agent interaction through message queues and event streams
- **API Layer**: Exposes platform functionality to the frontend and external services
- **Frontend**: Interactive visualization and navigation of the knowledge graph

## Setup

### Prerequisites

- Python 3.10+
- Node.js 16+
- Docker and Docker Compose (for containerized deployment)
- Neo4j (for knowledge graph storage)
- MongoDB (for document storage)
- RabbitMQ (for message queuing)

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

3. Copy environment variables template:
   ```
   cp env.example .env
   ```
   Then edit `.env` to set your configuration values.

4. Start services with Docker Compose (optional):
   ```
   docker-compose up -d
   ```

5. Run the coordinator:
   ```
   python -m coordinator.main
   ```

### Local Development

For local development without Docker, you can use the provided runner script:

```bash
# Run the coordinator and one scraper agent
python run_local.py

# Run with specific agent configuration
python run_local.py --scraper-agents 2 --processor-agents 1

# Run only specific agents without the coordinator
python run_local.py --no-coordinator --scraper-agents 1
```

### Running with Docker Compose

For a complete deployment with all services:

```bash
# Build and start all services
docker-compose up --build

# Start only specific services
docker-compose up coordinator scraper_agents mongodb rabbitmq

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Development

### Project Structure

```
intelligent_knowledge_platform/
├── coordinator/             # Coordinator module
│   ├── __init__.py
│   ├── main.py              # Main coordinator entry point
│   ├── agent_manager.py     # Agent lifecycle management
│   ├── task_queue.py        # Task management
│   ├── message_broker.py    # Communication layer
│   ├── api.py               # FastAPI endpoints
│   ├── config.py            # Configuration management
│   └── utils.py             # Utility functions
├── agents/                  # Agent implementations
│   ├── scraper/             # Web scraping agents
│   │   ├── agent.py         # Main scraper agent
│   │   ├── web_scraper.py   # Web page scraper
│   │   ├── pdf_scraper.py   # PDF scraper
│   │   └── academic_scraper.py # Academic paper scraper
│   ├── processor/           # Content processing agents (to be implemented)
│   ├── knowledge/           # Knowledge graph agents (to be implemented)
│   ├── learning/            # Recommendation agents (to be implemented)
│   └── ui/                  # UI generation agents (to be implemented)
├── frontend/                # Next.js frontend (to be implemented)
├── docker/                  # Docker configurations
│   ├── coordinator/         # Coordinator Dockerfile
│   └── agents/              # Agent Dockerfiles
├── data/                    # Data storage
│   ├── neo4j/               # Neo4j data
│   ├── mongodb/             # MongoDB data
│   └── vector_db/           # Vector database data
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker Compose configuration
├── run_local.py             # Local runner script
├── env.example              # Environment variables template
└── README.md                # Project documentation
```

### Running Tests

```
pytest
```

## API Usage

Once the coordinator is running, you can interact with the platform through its API:

```bash
# Get system status
curl http://localhost:8000/status

# Submit a web scraping task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"task_type": "scrape_web", "task_data": {"url": "https://example.com"}}'

# Get task status
curl http://localhost:8000/tasks/{task_id}
```

## License

MIT

## Contributors

Your Name (@yourusername) 