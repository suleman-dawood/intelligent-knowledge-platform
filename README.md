# Knowledge Integration System

A comprehensive knowledge management and integration platform built with Python (FastAPI) and Next.js. This system allows users to upload, process, and analyze various types of content while providing intelligent search and visualization capabilities.

## 🚀 Features

### ✅ **Fully Implemented Core Features**

#### **Authentication System**
- Real JWT-based authentication with refresh tokens
- User registration and login
- Password hashing with bcrypt
- Session management
- Demo credentials: `admin@example.com` / `password`

#### **Content Processing**
- **Text Processing**: Real NLP analysis including sentiment analysis and entity extraction
- **Web Scraping**: Live web content extraction with HTML parsing
- **File Upload**: Secure file upload with validation and progress tracking
- **Real-time Processing**: Asynchronous task processing with status tracking

#### **Knowledge Management**
- **Search Engine**: Real search functionality with relevance scoring
- **Knowledge Graph**: Interactive graph visualization of entities and relationships
- **Content Analytics**: Statistics and insights about processed content

#### **User Interface**
- **Modern Dashboard**: Real-time analytics and system status
- **Content Upload Modal**: Drag-and-drop file upload with progress bars
- **Search Interface**: Advanced search with filters and result ranking
- **Responsive Design**: Mobile-friendly interface with Tailwind CSS

#### **System Architecture**
- **Multi-Agent Backend**: Distributed processing with specialized agents
- **Real-time Communication**: WebSocket support for live updates
- **Task Queue System**: Asynchronous job processing with status tracking
- **Comprehensive API**: RESTful API with OpenAPI documentation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Agents        │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Specialized) │
│                 │    │                 │    │                 │
│ • Authentication│    │ • API Gateway   │    │ • Text Processor│
│ • Dashboard     │    │ • Task Manager  │    │ • Web Scraper   │
│ • File Upload   │    │ • WebSocket Hub │    │ • Knowledge     │
│ • Search UI     │    │ • Agent Coord.  │    │ • UI Handler    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Quick Start (Recommended)

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd Homework
   pip3 install -r requirements.txt
   ```

2. **Start the complete system**
   ```bash
   python3 start_system.py
   ```
   
   This automatically:
   - Installs frontend dependencies if needed
   - Starts backend (port 3100) and frontend (port 3000)
   - Monitors both services

### Manual Setup (Optional)

If you prefer to start services individually:

1. **Backend**
   ```bash
   python3 -m coordinator.main --host 0.0.0.0 --port 3100
   ```

2. **Frontend** (new terminal)
   ```bash
   cd frontend && npm install && npm run dev
   ```

## 🎯 Usage

### Accessing the System
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:3100
- **API Documentation**: http://localhost:3100/docs
- **Health Check**: http://localhost:3100/health

### Demo Credentials
- **Email**: `admin@example.com`
- **Password**: `password`

### Key Workflows

#### 1. **Content Upload & Processing**
1. Login to the dashboard
2. Click "Add Content" button
3. Choose content type (Text, URL, or File)
4. Upload/paste your content
5. Monitor processing status in real-time
6. View extracted entities and analysis results

#### 2. **Search & Discovery**
1. Use the search bar in the dashboard
2. Enter your query (e.g., "artificial intelligence")
3. View ranked results with relevance scores
4. Click on results to view detailed information

#### 3. **Knowledge Graph Exploration**
1. Navigate to the analytics section
2. View the interactive knowledge graph
3. Explore relationships between entities
4. Click nodes to see detailed information

## 🧪 Testing

### Automated System Tests
Run comprehensive system tests to verify all functionality:

```bash
python3 test_system.py
```

This will test:
- Backend health and status
- Content processing (text analysis)
- Web scraping functionality
- Search capabilities
- Knowledge graph generation
- Authentication endpoints

### Manual Testing
1. **Authentication**: Try logging in with demo credentials
2. **Text Processing**: Upload a text document and check analysis results
3. **Web Scraping**: Submit a URL and verify content extraction
4. **Search**: Search for topics and verify relevant results
5. **File Upload**: Upload a PDF and check processing status

## 📁 Project Structure

```
Homework/
├── coordinator/              # Backend service
│   ├── main.py              # Main application entry point
│   ├── api.py               # REST API endpoints
│   ├── agent_manager.py     # Agent coordination and task processing
│   └── agents/              # Specialized processing agents
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   ├── components/      # React components
│   │   └── lib/             # Utility libraries
│   ├── package.json         # Frontend dependencies
│   └── .env.local           # Frontend environment config
├── start_system.py          # 🚀 Main launcher (start here!)
├── test_system.py           # 🧪 System validation
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md               # Documentation
```

## 🔧 Configuration

### Environment Variables

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:3100
JWT_SECRET=your-secret-key-change-in-production
REFRESH_SECRET=your-refresh-secret-change-in-production
```

### Backend Configuration
- Default port: 3100
- Log level: INFO
- CORS enabled for frontend integration
- WebSocket support enabled

### Frontend Configuration
- Default port: 3000
- API proxy to backend
- Tailwind CSS for styling
- TypeScript enabled

## 🚀 Production Deployment

### Backend Deployment
1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn with Uvicorn workers)
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Configure database (PostgreSQL recommended)

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy to Vercel, Netlify, or similar platform
3. Configure environment variables
4. Set up custom domain

## 🔍 API Documentation

### Key Endpoints

#### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/signup` - User registration
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

#### Content Processing
- `POST /api/process-content` - Submit content for processing
- `GET /tasks/{task_id}` - Check task status
- `POST /files/upload` - Upload files

#### Search & Knowledge
- `GET /search?q={query}` - Search knowledge base
- `GET /graph/overview` - Get knowledge graph overview
- `GET /graph/node/{node_id}` - Get node-specific graph

#### System
- `GET /health` - Health check
- `GET /status` - System status
- `GET /agents` - Agent status

## 🛡️ Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **File Validation**: Type and size validation for uploads
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Sanitization**: Protection against injection attacks
- **Rate Limiting**: API rate limiting (configurable)

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Live status updates and notifications
- **Progress Tracking**: Visual progress bars for uploads and processing
- **Interactive Elements**: Hover effects, animations, and transitions
- **Accessibility**: ARIA labels and keyboard navigation support

## 📊 Performance Features

- **Asynchronous Processing**: Non-blocking task execution
- **Caching**: Response caching for improved performance
- **Lazy Loading**: Efficient resource loading
- **Connection Pooling**: Optimized database connections
- **Background Tasks**: Long-running tasks don't block UI

## 🔄 Recent Improvements

### High Priority Tasks Completed ✅
1. **Real Authentication System** - JWT-based auth with refresh tokens
2. **File Upload Integration** - Real file storage with progress tracking
3. **Content Processing** - Actual NLP analysis and web scraping
4. **Database Integration** - Real data persistence and retrieval
5. **Search Functionality** - Working search with relevance scoring
6. **Visualization System** - Interactive charts and knowledge graphs

### Medium Priority Tasks Completed ✅
1. **Error Handling** - Comprehensive error management
2. **Loading States** - Proper loading indicators throughout UI
3. **Responsive Design** - Mobile-friendly interface
4. **API Documentation** - Complete OpenAPI/Swagger docs
5. **System Monitoring** - Health checks and status endpoints

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill processes on ports 3000 and 3100
   sudo lsof -ti:3000 | xargs kill -9
   sudo lsof -ti:3100 | xargs kill -9
   ```

2. **Frontend Dependencies**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Python Dependencies**
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

4. **Permission Issues**
   ```bash
   chmod +x start_system.py
   chmod +x test_system.py
   ```

### Logs and Debugging
- Backend logs: Check console output when running coordinator
- Frontend logs: Check browser console and terminal output
- System tests: Run `python test_system.py` for diagnostic information

## 📈 Future Enhancements

### Planned Features
- Advanced NLP with transformer models
- Real-time collaboration features
- Advanced visualization options
- Integration with external knowledge bases
- Machine learning-based recommendations
- Advanced analytics and reporting
- Multi-language support
- Advanced user management and permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Run the system tests
3. Review the API documentation
4. Create an issue with detailed information

---

**Status**: ✅ **PRODUCTION READY** - All core features implemented and tested 