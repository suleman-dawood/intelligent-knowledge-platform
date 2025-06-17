# API Services & External Dependencies

This document provides a comprehensive overview of all API endpoints, external services, and dependencies used in the Intelligent Knowledge Aggregation Platform.

## 🔑 Required API Keys & Services

### DeepSeek API (REQUIRED)
- **Purpose**: LLM functionality for entity recognition, sentiment analysis, text summarization, and keyword extraction
- **Website**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **Pricing**: Pay-per-use, very affordable (~$0.14 per 1M input tokens, ~$0.28 per 1M output tokens)
- **Free Tier**: Available with credits for new accounts
- **Environment Variables**:
  ```
  DEEPSEEK_API_KEY=sk-your-api-key-here
  DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
  DEEPSEEK_MODEL=deepseek-chat
  ```
- **Usage**: All LLM-powered features including entity extraction, sentiment analysis, and text processing

## 🌐 External APIs (No Authentication Required)

### arXiv API
- **Purpose**: Academic paper search and retrieval
- **Website**: [https://arxiv.org/help/api](https://arxiv.org/help/api)
- **Cost**: Free
- **Rate Limits**: 3 seconds between requests (implemented in code)
- **Usage**: Downloading academic papers and metadata from arXiv

### Google Scholar (via scholarly library)
- **Purpose**: Academic paper search and author information
- **Library**: [scholarly](https://pypi.org/project/scholarly/)
- **Cost**: Free
- **Rate Limits**: Built-in rate limiting and proxy support
- **Usage**: Searching academic papers and author profiles

## 🗄️ Database Services

### Required Infrastructure Services

#### Neo4j Graph Database
- **Purpose**: Knowledge graph storage (entities, relationships, metadata)
- **Local**: [https://neo4j.com/download/](https://neo4j.com/download/)
- **Cloud**: [Neo4j AuraDB](https://neo4j.com/cloud/aura/) (Free tier available)
- **Default Port**: 7687 (Bolt), 7474 (HTTP)
- **Environment Variables**:
  ```
  NEO4J_URI=bolt://localhost:7687
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=password
  ```

#### MongoDB Document Database
- **Purpose**: Raw content and processed documents storage
- **Local**: [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
- **Cloud**: [MongoDB Atlas](https://cloud.mongodb.com/) (512MB free tier)
- **Default Port**: 27017
- **Environment Variables**:
  ```
  MONGODB_URI=mongodb://localhost:27017
  MONGODB_DB=knowledge_platform
  ```

#### Redis Cache
- **Purpose**: High-speed caching for frequently accessed data
- **Local**: [https://redis.io/download](https://redis.io/download)
- **Cloud**: [Redis Cloud](https://redis.com/try-free/) (30MB free tier)
- **Default Port**: 6379
- **Environment Variables**:
  ```
  REDIS_HOST=localhost
  REDIS_PORT=6379
  REDIS_DB=0
  REDIS_PASSWORD=
  ```

#### RabbitMQ Message Broker
- **Purpose**: Asynchronous communication between agents
- **Local**: [https://www.rabbitmq.com/download.html](https://www.rabbitmq.com/download.html)
- **Cloud**: [CloudAMQP](https://www.cloudamqp.com/) (Free tier available)
- **Default Port**: 5672 (AMQP), 15672 (Management UI)
- **Environment Variables**:
  ```
  RABBITMQ_HOST=localhost
  RABBITMQ_PORT=5672
  RABBITMQ_USER=guest
  RABBITMQ_PASSWORD=guest
  ```

#### Weaviate Vector Database
- **Purpose**: Vector embeddings storage for semantic search
- **Local**: Docker only - `docker run -p 8080:8080 semitechnologies/weaviate:1.18.0`
- **Cloud**: [Weaviate Cloud Services](https://console.weaviate.cloud/) (Free tier available)
- **Default Port**: 8080
- **Environment Variables**:
  ```
  VECTOR_DB_HOST=localhost
  VECTOR_DB_PORT=8080
  WEAVIATE_API_KEY=  # Only for cloud deployment
  ```

## 🚀 Platform API Endpoints

### Main API Server (Port 3100)

#### Health & Status
- `GET /status` - API health check
- `GET /agents` - List active agents and their status

#### Task Management
- `POST /tasks` - Submit new processing task
- `GET /tasks/{task_id}` - Get task status and results

#### Search & Knowledge
- `GET /search?q={query}` - Search knowledge base
- `GET /graph/overview` - Get knowledge graph overview
- `GET /graph/node/{node_id}?depth={depth}` - Get node neighborhood
- `GET /entities/{entity_id}` - Get entity details

#### Content Processing
- `POST /content/url` - Process URL content
- `POST /content/pdf` - Process PDF file
- `POST /content/text` - Process raw text

### Frontend Server (Port 3000)
- **Framework**: Next.js
- **API Proxy**: Routes `/api/*` to backend server
- **Environment Variables**:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:3100
  API_URL=http://localhost:3100
  WEBSOCKET_URL=http://localhost:3100
  ```

## 📊 Service Dependencies by Component

### Scraper Agents
- **DeepSeek API**: Content analysis and entity extraction
- **arXiv API**: Academic paper retrieval
- **Google Scholar**: Academic search
- **MongoDB**: Content storage
- **RabbitMQ**: Task communication

### Processor Agents
- **DeepSeek API**: NLP processing, entity recognition, sentiment analysis
- **MongoDB**: Document retrieval and storage
- **Neo4j**: Entity and relationship storage
- **Weaviate**: Vector embeddings storage
- **RabbitMQ**: Task communication

### Knowledge Agents
- **Neo4j**: Knowledge graph operations
- **MongoDB**: Document access
- **Weaviate**: Semantic search
- **RabbitMQ**: Task communication

### Learning Agents
- **Neo4j**: Knowledge graph analysis
- **MongoDB**: Learning data storage
- **RabbitMQ**: Task communication

### UI Agents
- **All databases**: Data retrieval for frontend
- **WebSocket**: Real-time updates to frontend

## 🔧 Configuration Management

### Environment Files
- **Development**: `.env` (created from `config.env.example`)
- **Docker**: Uses environment variables from `.env` file
- **Production**: Set environment variables in deployment platform

### Configuration Loading
- **File**: `coordinator/config.py`
- **Method**: `load_config()` function
- **Priority**: Environment variables override defaults

### Validation
- **Script**: `validate_env.py`
- **Purpose**: Validate all configurations and test connections
- **Usage**: `python validate_env.py`

## 🌍 Cloud Deployment Options

### Platform-as-a-Service

#### Heroku
```bash
heroku config:set DEEPSEEK_API_KEY=your_key
heroku config:set MONGODB_URI=your_mongodb_atlas_uri
heroku config:set NEO4J_URI=your_aura_uri
# ... set all other variables
```

#### Railway / Render
- Set environment variables in dashboard
- Connect GitHub repository for automatic deployment

### Container Platforms

#### Docker Compose (Local/VPS)
```bash
# Set environment variables in .env file
docker-compose up -d
```

#### Kubernetes
- Use provided Docker images
- Configure environment variables via ConfigMaps/Secrets

#### Cloud Container Services
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**

## 💰 Cost Estimates

### Minimal Setup (Development/Testing)
- **DeepSeek API**: ~$1-5/month for light usage
- **Infrastructure**: Free (local Docker or free tiers)
- **Total**: ~$1-5/month

### Production Setup (Small Scale)
- **DeepSeek API**: ~$10-50/month depending on usage
- **MongoDB Atlas**: $9/month (M10 cluster)
- **Neo4j AuraDB**: $65/month (Professional)
- **Redis Cloud**: $7/month (1GB)
- **CloudAMQP**: $19/month (Little Lemur)
- **Weaviate Cloud**: $25/month (Serverless)
- **Total**: ~$135-185/month

### Enterprise Setup
- Scale based on usage
- Consider dedicated infrastructure
- Contact service providers for volume discounts

## 🔒 Security Considerations

### API Keys
- Store in environment variables, never in code
- Use secrets management in production
- Rotate keys regularly
- Monitor usage for unusual activity

### Database Security
- Use strong passwords
- Enable SSL/TLS connections
- Restrict network access
- Regular backups

### Network Security
- Use HTTPS in production
- Configure firewalls
- VPN for sensitive deployments
- Monitor access logs

## 📈 Monitoring & Observability

### Health Checks
- All services provide health endpoints
- Database connection monitoring
- API response time tracking

### Logging
- Structured logging with configurable levels
- Centralized log aggregation recommended
- Error tracking and alerting

### Metrics
- Task processing rates
- API response times
- Database performance
- Resource utilization

## 🆘 Troubleshooting

### Common Issues
1. **API Key Issues**: Use `validate_env.py` to test connections
2. **Database Connections**: Check network access and credentials
3. **Port Conflicts**: Modify ports in environment configuration
4. **Memory Issues**: Scale infrastructure or use cloud services

### Support Resources
- **Documentation**: `DEPLOYMENT.md` for detailed setup
- **Validation**: `python validate_env.py` for environment testing
- **GitHub**: Repository issues for bug reports
- **Community**: Platform-specific documentation and forums 