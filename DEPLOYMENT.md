# Deployment Guide

This guide provides comprehensive instructions for deploying the Intelligent Knowledge Aggregation Platform in various environments.

## 📋 Prerequisites

### Required Accounts & API Keys

#### 🤖 **DeepSeek API (REQUIRED)**
- **Purpose**: LLM functionality for entity recognition, sentiment analysis, and text processing
- **Sign up**: [https://platform.deepseek.com/](https://platform.deepseek.com/)
- **Pricing**: Pay-per-use model, very affordable
- **Setup**: 
  1. Create account
  2. Navigate to API Keys section
  3. Generate new API key
  4. Add to `DEEPSEEK_API_KEY` in environment

### Required Software (Local Development)

#### Core Requirements
- **Python 3.10+**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Node.js 16+**: [https://nodejs.org/en/download/](https://nodejs.org/en/download/)
- **Git**: [https://git-scm.com/downloads](https://git-scm.com/downloads/)

#### Database Services (Choose Local or Cloud)

##### Option 1: Local Development (Docker)
```bash
# Install Docker Desktop
# Windows/Mac: https://www.docker.com/products/docker-desktop/
# Linux: https://docs.docker.com/engine/install/

# Start all required services
docker-compose up -d
```

##### Option 2: Local Development (Native Installation)

**Neo4j Graph Database**
- Download: [https://neo4j.com/download/](https://neo4j.com/download/)
- Installation: Follow platform-specific instructions
- Default credentials: `neo4j/password`

**MongoDB Document Database**
- Download: [https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
- Installation: Follow platform-specific instructions
- Default port: `27017`

**Redis Cache**
- Download: [https://redis.io/download](https://redis.io/download)
- Windows: [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
- Default port: `6379`

**RabbitMQ Message Broker**
- Download: [https://www.rabbitmq.com/download.html](https://www.rabbitmq.com/download.html)
- Default credentials: `guest/guest`
- Management UI: `http://localhost:15672`

**Weaviate Vector Database**
- Docker only: `docker run -p 8080:8080 semitechnologies/weaviate:1.18.0`
- Or use Weaviate Cloud (see cloud options below)

## 🚀 Quick Start (Local Development)

### 1. Clone Repository
```bash
git clone https://github.com/suleman-dawood/intelligent-knowledge-platform.git
cd intelligent-knowledge-platform
```

### 2. Environment Setup
```bash
# Copy environment template
cp config.env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

**Required Configuration:**
```bash
# MUST SET: Get from https://platform.deepseek.com/
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
```

### 3. Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 5. Start Services

#### Option A: Docker (Recommended for beginners)
```bash
# Start all infrastructure services
docker-compose up -d

# Wait for services to be ready (2-3 minutes)
# Check status: docker-compose ps
```

#### Option B: Local Services
Start each service individually according to their documentation.

### 6. Run the Platform
```bash
# Start the coordinator and agents
python run_local.py --scraper-agents=1 --processor-agents=1 --knowledge-agents=1 --learning-agents=1 --ui-agents=1

# In another terminal, start the frontend
cd frontend
npm run dev
```

### 7. Access the Platform
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API**: [http://localhost:3100](http://localhost:3100)
- **RabbitMQ Management**: [http://localhost:15672](http://localhost:15672) (guest/guest)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474) (neo4j/password)

## ☁️ Cloud Deployment Options

### Cloud Database Services

#### **MongoDB Atlas (Cloud MongoDB)**
- **Sign up**: [https://cloud.mongodb.com/](https://cloud.mongodb.com/)
- **Free tier**: 512MB storage
- **Setup**:
  1. Create cluster
  2. Create database user
  3. Whitelist IP addresses
  4. Get connection string
  5. Set `MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/knowledge_platform`

#### **Neo4j AuraDB (Cloud Neo4j)**
- **Sign up**: [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/)
- **Free tier**: Available
- **Setup**:
  1. Create instance
  2. Download credentials
  3. Set `NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io`

#### **Redis Cloud**
- **Sign up**: [https://redis.com/try-free/](https://redis.com/try-free/)
- **Free tier**: 30MB
- **Setup**:
  1. Create database
  2. Get endpoint and password
  3. Set `REDIS_HOST` and `REDIS_PASSWORD`

#### **CloudAMQP (Cloud RabbitMQ)**
- **Sign up**: [https://www.cloudamqp.com/](https://www.cloudamqp.com/)
- **Free tier**: Available
- **Setup**:
  1. Create instance
  2. Get connection details
  3. Set `RABBITMQ_HOST`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`

#### **Weaviate Cloud Services (WCS)**
- **Sign up**: [https://console.weaviate.cloud/](https://console.weaviate.cloud/)
- **Free tier**: Available
- **Setup**:
  1. Create cluster
  2. Get cluster URL
  3. Set `VECTOR_DB_HOST` and `WEAVIATE_API_KEY`

### Platform-as-a-Service Deployment

#### **Heroku**
```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login and create app
heroku login
heroku create your-app-name

# Set environment variables
heroku config:set DEEPSEEK_API_KEY=your_key
heroku config:set MONGODB_URI=your_mongodb_atlas_uri
# ... set all other required vars

# Deploy
git push heroku main
```

#### **Railway**
- **Sign up**: [https://railway.app/](https://railway.app/)
- Connect GitHub repository
- Set environment variables in dashboard
- Deploy automatically

#### **Render**
- **Sign up**: [https://render.com/](https://render.com/)
- Connect GitHub repository
- Configure environment variables
- Deploy web service

### Container Deployment

#### **Docker Hub**
```bash
# Build and push images
docker build -t your-username/knowledge-platform .
docker push your-username/knowledge-platform

# Use in production with docker-compose
```

#### **AWS ECS/EKS**
- Use provided Dockerfile and docker-compose.yml
- Configure AWS credentials
- Set up load balancer and auto-scaling

#### **Google Cloud Run**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/knowledge-platform
gcloud run deploy --image gcr.io/PROJECT-ID/knowledge-platform --platform managed
```

## 🔧 Configuration Reference

### Environment Variables

| Variable | Required | Description | Default | Example |
|----------|----------|-------------|---------|---------|
| `DEEPSEEK_API_KEY` | ✅ Yes | DeepSeek API key | - | `sk-123...` |
| `DEEPSEEK_BASE_URL` | No | DeepSeek API base URL | `https://api.deepseek.com/v1` | - |
| `DEEPSEEK_MODEL` | No | Model to use | `deepseek-chat` | - |
| `API_HOST` | No | API server host | `localhost` | `0.0.0.0` |
| `API_PORT` | No | API server port | `3100` | `8080` |
| `NEO4J_URI` | No | Neo4j connection | `bolt://localhost:7687` | `neo4j+s://xxx.databases.neo4j.io` |
| `NEO4J_USER` | No | Neo4j username | `neo4j` | `neo4j` |
| `NEO4J_PASSWORD` | No | Neo4j password | `password` | `your_password` |
| `MONGODB_URI` | No | MongoDB connection | `mongodb://localhost:27017` | `mongodb+srv://...` |
| `MONGODB_DB` | No | MongoDB database | `knowledge_platform` | - |
| `REDIS_HOST` | No | Redis host | `localhost` | `redis.cloud.com` |
| `REDIS_PORT` | No | Redis port | `6379` | `6379` |
| `REDIS_PASSWORD` | No | Redis password | - | `your_password` |
| `RABBITMQ_HOST` | No | RabbitMQ host | `localhost` | `amqp.cloudamqp.com` |
| `RABBITMQ_PORT` | No | RabbitMQ port | `5672` | `5672` |
| `RABBITMQ_USER` | No | RabbitMQ user | `guest` | `your_user` |
| `RABBITMQ_PASSWORD` | No | RabbitMQ password | `guest` | `your_password` |
| `VECTOR_DB_HOST` | No | Weaviate host | `localhost` | `cluster.weaviate.network` |
| `VECTOR_DB_PORT` | No | Weaviate port | `8080` | `443` |

### Frontend Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | No | Public API URL | `http://localhost:3100` |
| `API_URL` | No | Server-side API URL | `http://localhost:3100` |
| `WEBSOCKET_URL` | No | WebSocket URL | `http://localhost:3100` |

## 🔍 Verification & Testing

### Health Checks
```bash
# Check API health
curl http://localhost:3100/status

# Check database connections
curl http://localhost:3100/agents

# Frontend health
curl http://localhost:3000
```

### Service Status
```bash
# Docker services
docker-compose ps

# Individual service logs
docker-compose logs coordinator
docker-compose logs neo4j
```

### Test the Platform
1. Open [http://localhost:3000](http://localhost:3000)
2. Go to Search page
3. Submit a test query
4. Check if results are returned
5. Go to Explore page to see knowledge graph

## 🛠️ Troubleshooting

### Common Issues

#### "DEEPSEEK_API_KEY is required"
- **Solution**: Set your DeepSeek API key in the `.env` file
- **Get key**: [https://platform.deepseek.com/](https://platform.deepseek.com/)

#### Database Connection Errors
- **Neo4j**: Check URI format and credentials
- **MongoDB**: Verify connection string and network access
- **Redis**: Confirm host and port settings

#### Port Conflicts
- **Solution**: Change ports in `.env` file
- **Common conflicts**: 3000 (frontend), 3100 (API), 5672 (RabbitMQ)

#### Memory Issues
- **Solution**: Increase Docker memory allocation or use cloud services
- **Minimum**: 4GB RAM recommended

#### Frontend Build Errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Getting Help

1. **Check logs**: Look at coordinator and agent logs for error messages
2. **Verify environment**: Ensure all required variables are set
3. **Test connections**: Use health check endpoints
4. **GitHub Issues**: Report bugs at repository issues page

## 📈 Production Considerations

### Security
- Use strong passwords for all services
- Enable SSL/TLS for all connections
- Set up firewall rules
- Use secrets management (AWS Secrets Manager, etc.)

### Performance
- Use cloud databases for better performance
- Enable Redis caching
- Set up load balancing
- Monitor resource usage

### Monitoring
- Set up logging aggregation (ELK stack, Datadog)
- Monitor API response times
- Track database performance
- Set up alerts for failures

### Backup
- Regular database backups
- Code repository backups
- Configuration backups
- Disaster recovery plan

## 🎯 Next Steps

After deployment:
1. **Configure monitoring** and alerting
2. **Set up automated backups**
3. **Implement CI/CD pipeline**
4. **Scale based on usage**
5. **Add custom agents** for specific use cases

For support, please check the [GitHub repository](https://github.com/suleman-dawood/intelligent-knowledge-platform) or create an issue. 