# CodeMatrix - Your Code's Digital Ghost

> **AI-Powered Code Analysis with Cursor-like Intelligence**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 What is CodeMatrix?

CodeMatrix is an advanced AI-powered code analysis platform that provides **Cursor-like intelligence** for understanding, analyzing, and improving your codebase. It combines the power of RAG (Retrieval-Augmented Generation) with multiple AI models to deliver intelligent code suggestions, refactoring recommendations, and comprehensive code explanations.

### ✨ Key Features

- **🤖 Cursor-like AI Assistant** - Context-aware code analysis and suggestions
- **🔍 Multi-Mode Chat** - Normal, Cursor, Suggest, Refactor, and Explain modes
- **📊 Repository Intelligence** - Deep understanding of codebase structure and relationships
- **🛡️ Security Scanning** - Identify potential security vulnerabilities
- **📈 Code Visualization** - Visual representation of code architecture
- **⚡ Real-time Analysis** - Instant responses with Groq and Gemini AI
- **🎨 Matrix-style UI** - Beautiful, modern interface with cyberpunk aesthetics

## 🚀 Cursor-like Features

### 1. **Context-Aware Chat**
- Understands current file context and cursor position
- Provides intelligent suggestions based on codebase analysis
- Multi-file relationship understanding

### 2. **Code Improvement Suggestions**
- Identifies optimization opportunities
- Suggests best practices and modern patterns
- Performance and security recommendations

### 3. **Refactoring Assistance**
- Suggests code structure improvements
- Identifies refactoring opportunities
- Provides before/after examples

### 4. **Complexity Explanations**
- Explains code complexity and logic
- Educational insights for learning
- Simplification strategies

### 5. **Dynamic Repository Analysis**
- Real-time analysis of any repository
- No hardcoded responses - always context-aware
- Intelligent metadata extraction

## 🏗️ Architecture

```
CodeMatrix/
├── codematrix_backend/          # FastAPI Backend
│   ├── core/                   # Core Services
│   │   ├── ai_service.py       # AI Model Integration
│   │   ├── rag_service.py      # RAG & Vector Search
│   │   ├── cloning_service.py  # Repository Processing
│   │   └── state_manager.py    # State Management
│   ├── models/                 # Data Models
│   ├── vector_db/              # Vector Database
│   └── main.py                 # FastAPI Application
├── codematrix_frontend/        # React Frontend
│   ├── src/
│   │   ├── components/         # UI Components
│   │   ├── services/           # API Services
│   │   └── pages/              # Application Pages
│   └── package.json
└── README.md
```

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Git**

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/RAG3.0.git
   cd RAG3.0
   ```

2. **Set up Python environment**
   ```bash
   cd codematrix_backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Add your API keys
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY_1=your_gemini_api_key
   GEMINI_API_KEY_2=your_backup_gemini_key
   ```

5. **Start the backend**
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../codematrix_frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://127.0.0.1:8000
   - API Docs: http://127.0.0.1:8000/docs

## 🎮 Usage

### 1. **Clone a Repository**
- Enter a GitHub repository URL in the frontend
- Supported repositories: < 50MB for optimal performance
- The system will automatically process and index the codebase

### 2. **Choose Chat Mode**
- **Normal Chat**: General code questions
- **Cursor Mode**: Context-aware with current file focus
- **Suggest Mode**: Code improvement recommendations
- **Refactor Mode**: Code restructuring suggestions
- **Explain Mode**: Complexity and educational explanations

### 3. **Ask Questions**
Examples of questions you can ask:

```
# Simple Questions
"repo name"
"what is this project about?"
"how many files are there?"

# Code Analysis
"explain the main function"
"how can I improve this code?"
"suggest refactoring for this function"

# Architecture Questions
"what is the overall architecture?"
"how do these files work together?"
"identify potential issues"
```

### 4. **Advanced Features**
- **Security Scanning**: Analyze code for vulnerabilities
- **Code Visualization**: Visual representation of code structure
- **Live Preview**: Real-time code execution preview

## 🔧 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/clone` | POST | Clone and process repository |
| `/status` | GET | Get processing status |
| `/chat` | POST | General chat with AI |
| `/chat/cursor` | POST | Context-aware chat |
| `/code/suggest` | POST | Code improvement suggestions |
| `/code/refactor` | POST | Refactoring recommendations |
| `/code/explain` | POST | Code complexity explanations |

### Example API Usage

```bash
# Clone repository
curl -X POST "http://127.0.0.1:8000/clone" \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/pallets/flask"}'

# Chat with AI
curl -X POST "http://127.0.0.1:8000/chat/cursor" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "explain the main function",
    "top_k": 5,
    "current_file": "app.py",
    "cursor_position": 100
  }'
```

## 🤖 AI Models Used

- **Groq**: Fast, real-time responses for chat interactions
- **Gemini**: Detailed code analysis and explanations
- **Gemini Embeddings**: Vector search and similarity matching

## 🔒 Security Features

- Repository size limits (50MB max)
- Secure API key management
- Input validation and sanitization
- CORS protection
- Rate limiting

## 🎨 UI Features

- **Matrix-style Interface**: Cyberpunk aesthetics with neon colors
- **Real-time Chat**: Typewriter effect for AI responses
- **Code Highlighting**: Syntax highlighting for code snippets
- **Responsive Design**: Works on desktop and mobile
- **Dark Theme**: Easy on the eyes for long coding sessions

## 🚀 Performance Optimizations

- **In-memory Vector Storage**: Fast retrieval and processing
- **Async Processing**: Non-blocking repository cloning
- **Smart Caching**: Efficient memory usage
- **Timeout Protection**: Prevents hanging on large repositories
- **Partial Matching**: Intelligent repository name resolution

## 🐛 Troubleshooting

### Common Issues

1. **Repository too large**
   ```
   Error: Repository is too large (XX.XMB). Please use a smaller repository (< 50MB)
   ```
   **Solution**: Use a smaller repository or fork and remove unnecessary files

2. **API key issues**
   ```
   Error: AI services not initialized
   ```
   **Solution**: Check your API keys in the .env file

3. **Cloning timeout**
   ```
   Error: Clone timed out after 60 seconds
   ```
   **Solution**: Check internet connection or try a different repository

4. **Vector store mismatch**
   ```
   Error: Repository was previously loaded but index cleared
   ```
   **Solution**: Re-clone the repository (server restart clears memory)

### Debug Commands

```bash
# Check backend health
curl http://127.0.0.1:8000/health

# Check repository status
curl http://127.0.0.1:8000/status

# View vector stores
curl http://127.0.0.1:8000/debug/vector-stores
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .

# Lint code
flake8
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Open-Meteo**: For the inspiration from their comprehensive API documentation
- **Cursor**: For the AI assistant concept and user experience
- **FastAPI**: For the excellent web framework
- **React**: For the powerful frontend framework
- **LangChain**: For the RAG implementation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/RAG3.0/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/RAG3.0/discussions)
- **Email**: your-email@example.com

## 🚀 Roadmap

- [ ] **Real-time File Editing**: Edit files directly in the interface
- [ ] **Multi-language Support**: Support for more programming languages
- [ ] **Team Collaboration**: Shared workspaces and team features
- [ ] **Advanced Analytics**: Code quality metrics and trends
- [ ] **Integration APIs**: Connect with other development tools
- [ ] **Mobile App**: Native mobile application
- [ ] **Offline Mode**: Work without internet connection

---

**Made with ❤️ by the CodeMatrix Team**

*Your Code's Digital Ghost - Bringing AI Intelligence to Every Codebase* 