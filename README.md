# 🙏 Biblical RAG Chatbot

A Retrieval Augmented Generation (RAG) chatbot that answers questions about the Bible using LangChain and Google Gemini.

## 📋 Project Overview

This project implements a sophisticated biblical Q&A system that:
- **Indexes biblical texts** into a vector database for semantic search
- **Retrieves relevant passages** based on user questions
- **Generates contextual answers** using retrieved scripture references
- **Provides a user-friendly interface** through Streamlit

## 🏗️ Project Structure

```
Chatbot/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration management
├── core/
│   ├── __init__.py
│   └── rag_engine.py        # Main RAG engine implementation
├── data/
│   ├── __init__.py
│   ├── bible_seeder.py      # Bible data loading and processing
│   └── bible_data.json      # Bible verses (auto-generated)
├── utils/
│   └── __init__.py
├── app.py                   # Streamlit web interface
├── main.py                  # Command-line testing interface
├── requirements.txt         # Python dependencies
├── env_template.txt         # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone or create the project directory
cd Chatbot

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env_template.txt .env
# Edit .env and add your Google API key
```

### 2. Configuration

Edit your `.env` file:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the Application

**Option A: Streamlit Web Interface**
```bash
streamlit run app.py
```

**Option B: Command Line Interface**
```bash
python main.py
```

## 🔧 Features

### Core RAG Functionality
- **Document Loading**: Processes biblical texts with proper metadata
- **Text Chunking**: Creates verse-level and passage-level chunks
- **Semantic Search**: Uses Google embeddings for relevance matching
- **Context Generation**: Formats retrieved passages with references
- **Answer Generation**: Provides biblically-grounded responses

### Web Interface (Streamlit)
- **Chat Interface**: Interactive conversation with the chatbot
- **System Status**: Real-time database and system information
- **Example Questions**: Pre-built questions to get started
- **Conversation Management**: Clear history and rebuild database options

### Command Line Interface
- **Testing Mode**: Predefined test questions
- **Interactive Mode**: Ask custom questions
- **Simple Setup**: No web dependencies required

## 📊 Data Processing

The system processes biblical data through multiple stages:

1. **Raw Data**: JSON format with book, chapter, verse, and text
2. **Document Creation**: LangChain Document objects with rich metadata
3. **Chunking**: Both individual verses and multi-verse passages
4. **Embedding**: Google embeddings for semantic similarity
5. **Vector Storage**: ChromaDB for efficient retrieval

### Metadata Structure
```python
{
    'book': 'Genesis',
    'chapter': 1,
    'verse': 1,
    'reference': 'Genesis 1:1',
    'translation': 'KJV',
    'testament': 'Old',
    'chunk_type': 'verse'
}
```

## 🧪 Testing

### Manual Testing
```bash
# Run main.py for interactive testing
python main.py

# Test specific modules
python -m data.bible_seeder
```

### Sample Questions
- "What does the Bible say about creation?"
- "Tell me about God's love for the world"
- "What does Psalm 23 say about God as shepherd?"
- "How does the Bible describe love?"

## 🔒 Configuration Options

### Model Settings
- **Model**: `gemini-2.0-flash` (configurable)
- **Temperature**: `0.7` (configurable)
- **Max Tokens**: `1000` (configurable)

### RAG Settings
- **Chunk Size**: `500` characters
- **Chunk Overlap**: `50` characters
- **Retrieval Count**: `5` documents

### Database Settings
- **Vector DB**: ChromaDB (file-based)
- **Embeddings**: Google embeddings
- **Persistence**: Local file storage

## 🛠️ Development

### Adding New Bible Data
1. Modify `data/bible_seeder.py`
2. Add verses to `create_sample_bible_data()`
3. Run the seeder to regenerate database

### Customizing Prompts
1. Edit `core/rag_engine.py`
2. Modify the `_setup_prompt()` method
3. Restart the application

### Extending Functionality
- Add new document processors in `utils/`
- Implement evaluation metrics
- Add support for multiple translations

## 📦 Dependencies

### Core Dependencies
- `langchain`: RAG framework
- `langchain-google-genai`: Google Gemini integration
- `langchain-chroma`: Vector database
- `streamlit`: Web interface
- `python-dotenv`: Environment management


---

**Built with LangChain, OpenAI, and Streamlit** 🚀 
