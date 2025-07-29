# RAG3.0 - Advanced Code Analysis and Repository Intelligence

A comprehensive RAG (Retrieval-Augmented Generation) system for intelligent code analysis, repository understanding, and AI-powered development assistance.

## 🚀 Features

- **Intelligent Code Analysis**: Deep understanding of codebases using advanced RAG techniques
- **Repository Cloning & Processing**: Automated repository analysis and vectorization
- **AI-Powered Chat Interface**: Interactive code exploration and explanation
- **Security Scanning**: Automated security vulnerability detection
- **Live Code Preview**: Real-time code execution and visualization
- **Multi-Repository Support**: Handle multiple repositories simultaneously

## 🏗️ Architecture

The project consists of two main components:

### Backend (`codematrix_backend/`)
- **FastAPI** server for API endpoints
- **RAG Service**: Advanced retrieval and generation capabilities
- **AI Service**: Integration with AI models for code analysis
- **Cloning Service**: Repository management and processing
- **Vector Database**: ChromaDB for efficient similarity search

### Frontend (`codematrix_frontend/`)
- **React + TypeScript** application
- **Modern UI** with shadcn/ui components
- **Real-time Chat Interface** for code exploration
- **Code Visualization** and live preview capabilities

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Git

## 🛠️ Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd codematrix_backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the backend server:
```bash
python main.py
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd codematrix_frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## 🚀 Usage

1. **Start both backend and frontend servers**
2. **Open the frontend application** in your browser
3. **Enter a repository URL** to analyze
4. **Use the chat interface** to ask questions about the code
5. **Explore code insights** and security findings

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# AI Model Configuration
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Database Configuration
CHROMA_DB_PATH=./vector_db

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

## 📁 Project Structure

```
RAG3.0/
├── codematrix_backend/
│   ├── api/                 # API endpoints
│   ├── core/               # Core services
│   │   ├── ai_service.py   # AI model integration
│   │   ├── rag_service.py  # RAG implementation
│   │   ├── cloning_service.py # Repository management
│   │   └── config.py       # Configuration management
│   ├── models/             # Data models and schemas
│   ├── repositories/       # Repository data
│   ├── vector_db/          # Vector database storage
│   └── main.py            # FastAPI application
├── codematrix_frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/yourusername/RAG3.0/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🔮 Roadmap

- [ ] Enhanced security scanning capabilities
- [ ] Support for more programming languages
- [ ] Integration with CI/CD pipelines
- [ ] Advanced code visualization features
- [ ] Multi-user collaboration features 