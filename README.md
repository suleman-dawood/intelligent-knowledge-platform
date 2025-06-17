# Intelligent Knowledge Aggregation Platform

A comprehensive multi-agent system for gathering, processing, analyzing, and visualizing knowledge from diverse sources using advanced AI capabilities.

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**: [Download](https://www.python.org/downloads/)
- **Node.js 16+**: [Download](https://nodejs.org/en/download/)
- **Docker Desktop**: [Download](https://www.docker.com/products/docker-desktop/) (recommended)
- **DeepSeek API Key**: [Get Free Key](https://platform.deepseek.com/) (REQUIRED)

### 🎯 One-Command Setup
```bash
# Clone and setup everything
git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
cd intelligent-knowledge-platform
chmod +x setup.sh && ./setup.sh
```

### 🔑 Configure API Key
1. Get your free DeepSeek API key from [platform.deepseek.com](https://platform.deepseek.com/)
2. Add it to your `.env` file:
```bash
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

### 🐳 Start Infrastructure
```bash
# Start all database services
docker compose up -d

# Verify all services are running
docker compose ps
```

### 🎮 Launch Platform
```bash
# Terminal 1: Start backend
source venv/bin/activate
python run_local.py

# Terminal 2: Start frontend  
cd frontend && npm run dev
```

### 🌐 Access Platform
- **Frontend**: http://localhost:3000
- **API**: http://localhost:3100
- **Neo4j Browser**: http://localhost:7474 (neo4j/password)
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

---

## 📋 Overview

The Intelligent Knowledge Aggregation Platform is a distributed, multi-agent system that:
- 🔍 **Extracts** content from websites, PDFs, and academic sources
- 🧠 **Analyzes** using advanced AI (DeepSeek LLM integration)
- 🕸️ **Builds** knowledge graphs with entities and relationships
- 📊 **Visualizes** complex knowledge networks
- 🔎 **Enables** semantic search and exploration

## 🏗️ Architecture

### Core Components
- **🤖 Multi-Agent System**: Specialized agents for different tasks
- **🧠 DeepSeek LLM**: Advanced AI for entity recognition and analysis
- **🕸️ Knowledge Graph**: Neo4j for storing relationships
- **📄 Document Store**: MongoDB for content storage
- **🔍 Vector Search**: Weaviate for semantic similarity
- **⚡ Real-time**: RabbitMQ for async communication
- **🎨 Modern UI**: Next.js React frontend

### Agent Types
- **🕷️ Scraper Agent**: Web, PDF, and academic content extraction
- **⚙️ Processor Agent**: AI-powered text analysis and NLP
- **🧠 Knowledge Agent**: Graph building and relationship extraction
- **📚 Learning Agent**: Continuous improvement and feedback
- **🖥️ UI Agent**: Frontend API and WebSocket connections

---

## 🛠️ Installation & Setup

### Method 1: Automated Setup (Recommended)

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

### Method 2: Manual Setup

#### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
cd intelligent-knowledge-platform

# Copy environment template
cp config.env.example .env

# Edit .env with your DeepSeek API key
nano .env
```

#### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

#### 4. Infrastructure Setup

**Option A: Docker (Recommended)**
```bash
docker compose up -d
```

**Option B: Local Installation**
- Neo4j: [Download](https://neo4j.com/download/)
- MongoDB: [Download](https://www.mongodb.com/try/download/community)
- Redis: [Download](https://redis.io/download)
- RabbitMQ: [Download](https://www.rabbitmq.com/download.html)

---

## 🚀 Running the Platform

### Development Mode
```bash
# Start infrastructure (if not already running)
docker compose up -d

# Start backend (Terminal 1)
source venv/bin/activate
python run_local.py

# Start frontend (Terminal 2)
cd frontend && npm run dev
```

### Production Mode
```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start with production settings
python run_local.py --production
```

### Custom Configuration
```bash
# Start with specific agent counts
python run_local.py --scraper-agents=2 --processor-agents=2 --knowledge-agents=1
```

---

## 💡 Usage Guide

### Adding Content
1. Navigate to **Search** page
2. Click **"Add Content"** button
3. Submit URL, PDF file, or raw text
4. System automatically processes and analyzes content

### Exploring Knowledge Graph
1. Go to **Explore** page
2. Interactive graph visualization with D3.js
3. Click nodes to view details and connections
4. Use zoom and pan for navigation

### Searching Knowledge
1. Use **Search** page for semantic queries
2. Results include entities, concepts, and documents
3. Click results to explore relationships
4. Advanced filtering and sorting options

### Real-time Updates
- WebSocket connection provides live updates
- See processing status in real-time
- New knowledge appears automatically in visualizations

---

## 🔧 Configuration

### Required Environment Variables
```bash
# REQUIRED: DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# API Configuration
API_HOST=0.0.0.0
API_PORT=3100

# Database URLs (Docker defaults)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
MONGODB_URI=mongodb://localhost:27017/
REDIS_HOST=localhost
REDIS_PORT=6379
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```

### Cloud Services (Optional)
For production deployment, consider cloud alternatives:

| Service | Purpose | Free Tier | Sign Up |
|---------|---------|-----------|---------|
| **MongoDB Atlas** | Document Database | 512MB | [cloud.mongodb.com](https://cloud.mongodb.com/) |
| **Neo4j AuraDB** | Graph Database | Available | [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura/) |
| **Redis Cloud** | Cache | 30MB | [redis.com/try-free](https://redis.com/try-free/) |
| **CloudAMQP** | Message Broker | Available | [cloudamqp.com](https://www.cloudamqp.com/) |
| **Weaviate Cloud** | Vector Database | Available | [console.weaviate.cloud](https://console.weaviate.cloud/) |

---

## 🏭 Production Deployment

### Docker Deployment
```bash
# Production docker-compose
docker compose -f docker-compose.prod.yml up -d

# Scale specific services
docker compose up -d --scale processor_agent=3
```

### Cloud Platforms

#### Heroku
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set DEEPSEEK_API_KEY=your_key
git push heroku main
```

#### Railway
```bash
# Connect to Railway
railway login
railway init
railway up
```

#### AWS/GCP/Azure
- Use container services (ECS, Cloud Run, Container Instances)
- Set up managed databases
- Configure environment variables

---

## 🧪 Development

### Project Structure
```
intelligent-knowledge-platform/
├── agents/                  # Multi-agent system
│   ├── scraper/            # Content extraction
│   ├── processor/          # AI analysis
│   ├── knowledge/          # Graph management
│   ├── learning/           # Continuous learning
│   └── ui/                 # API endpoints
├── coordinator/            # Agent coordination
├── frontend/               # Next.js UI
│   ├── src/app/           # App router pages
│   ├── src/components/    # UI components
│   └── src/lib/           # Utilities
├── data/                  # Data storage
└── docker/               # Docker configs
```

### Key Features Implemented

#### 🧠 Advanced AI Integration
- **DeepSeek LLM**: Entity recognition, sentiment analysis, summarization
- **Multi-method NLP**: NLTK + LLM for enhanced accuracy
- **Confidence Scoring**: Weighted results from multiple sources

#### 📄 Real Content Processing
- **PDF Processing**: PyPDF2 + pdfplumber for comprehensive extraction
- **Academic Papers**: arXiv API + Google Scholar integration
- **Web Scraping**: BeautifulSoup with rate limiting and error handling

#### 🕸️ Knowledge Graph Features
- **Entity Extraction**: AI-powered with confidence scoring
- **Relationship Discovery**: Automatic relationship extraction
- **Graph Visualization**: Interactive D3.js visualization
- **Semantic Search**: Vector-based similarity search

#### ⚡ Performance & Reliability
- **Async Processing**: Non-blocking operations
- **Error Handling**: Comprehensive error management
- **Rate Limiting**: Respectful API usage
- **Caching**: Redis for performance optimization

### Testing
```bash
# Run validation
python validate_env.py

# Check service health
docker compose ps

# View logs
docker compose logs -f
```

### API Documentation
- **OpenAPI/Swagger**: Available at `/docs` when running
- **WebSocket Events**: Real-time communication protocol
- **GraphQL**: Available for complex queries

---

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make changes and test thoroughly
5. Submit pull request

### Code Style
- **Python**: Black formatting, flake8 linting
- **TypeScript**: ESLint + Prettier
- **Commits**: Conventional commit messages

---

## 📊 Monitoring & Troubleshooting

### Health Checks
```bash
# Validate environment
python validate_env.py

# Check service status
docker compose ps

# View service logs
docker compose logs -f [service_name]
```

### Common Issues

#### Services Not Starting
```bash
# Check Docker is running
docker --version

# Restart services
docker compose down && docker compose up -d
```

#### API Connection Issues
```bash
# Verify DeepSeek API key
curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" https://api.deepseek.com/v1/models
```

#### Frontend Build Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📈 Performance & Scaling

### Optimization Tips
- **Agent Scaling**: Increase agent counts for higher throughput
- **Database Indexing**: Optimize Neo4j and MongoDB queries
- **Caching Strategy**: Implement Redis caching for frequent queries
- **Load Balancing**: Use multiple API instances

### Monitoring
- **Metrics**: Built-in performance tracking
- **Logging**: Structured logging with different levels
- **Health Endpoints**: Service health monitoring

---

## 🎯 Roadmap

### Current Features ✅
- Multi-agent architecture with real AI integration
- PDF and academic paper processing
- Knowledge graph visualization
- Real-time updates via WebSockets
- Docker containerization
- Comprehensive error handling

### Planned Features 🚧
- **User Authentication**: Multi-user support
- **Advanced Analytics**: Usage metrics and insights
- **Batch Processing**: Bulk document processing
- **API Documentation**: Auto-generated docs
- **Mobile App**: React Native companion
- **Enterprise Features**: SSO, audit logs, compliance

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **DeepSeek**: Advanced LLM capabilities
- **Neo4j**: Graph database technology
- **MongoDB**: Document storage
- **Next.js**: Modern React framework
- **D3.js**: Data visualization
- **Docker**: Containerization platform

---

## 🆘 Support

### Getting Help
- **Documentation**: This README covers most scenarios
- **Issues**: [GitHub Issues](https://github.com/suleman-dawood/intelligent-knowledge-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/suleman-dawood/intelligent-knowledge-platform/discussions)

### Quick Links
- **DeepSeek API**: [platform.deepseek.com](https://platform.deepseek.com/)
- **Docker Desktop**: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)
- **Neo4j Browser**: http://localhost:7474
- **RabbitMQ Management**: http://localhost:15672

---

**Ready to explore knowledge like never before? 🚀**

```bash
git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
cd intelligent-knowledge-platform
chmod +x setup.sh && ./setup.sh
``` 