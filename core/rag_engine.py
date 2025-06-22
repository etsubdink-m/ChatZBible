"""
Core RAG Engine for Biblical Chatbot
Handles document loading, embedding, retrieval, and answer generation
"""
import os
from typing import List, Dict, Optional
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable, Client


from config.settings import config


class BiblicalRAGEngine:
    """
    Core RAG engine for biblical question answering
    """
    
    def __init__(self):
        """Initialize the RAG engine with default components"""
        config.validate_config()
        
        # Initialize components
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " "],
            add_start_index=True,  # track index in original document
        )
        
        # Setup components
        self._setup_llm()
        self._setup_embeddings()
        self._setup_prompt()
        
    def _setup_llm(self):
        """Initialize the language model"""
        import os
        if not os.environ.get("GOOGLE_API_KEY") and config.GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
        
        self.llm = init_chat_model(
            "gemini-2.0-flash", 
            model_provider="google_genai",
            # temperature=config.TEMPERATURE,
        )
    
    def _setup_embeddings(self):
        """Initialize embeddings model"""
        import os
        if not os.environ.get("GOOGLE_API_KEY") and config.GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )

    def _setup_langsmith(self):
        """Setup LangSmith tracing if configured"""
        if config.LANGSMITH_API_KEY:
            os.environ["LANGSMITH_API_KEY"] = config.LANGSMITH_API_KEY
        
        if config.LANGSMITH_TRACING:
            os.environ["LANGSMITH_TRACING"] = "true"
            
        if config.LANGSMITH_PROJECT:
            os.environ["LANGSMITH_PROJECT"] = config.LANGSMITH_PROJECT
        
    
    def _setup_prompt(self):
        """Setup the biblical RAG prompt template from LangSmith Hub"""
        try:
            
            # Initialize LangSmith client
            client = Client()
            
            # Pull prompt from LangSmith Hub
            self.prompt = client.pull_prompt("biblical-rag-assistant")
            
        except Exception as e:
            print(f"Warning: Could not load prompt from LangSmith Hub: {e}")
            print("Falling back to default prompt template...")
            
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        Create and populate vector store with documents
        
        Args:
            documents: List of Document objects to index
            
        Returns:
            Populated Chroma vector store
        """
        if not documents:
            raise ValueError("No documents provided for indexing")
        
        # Split documents into chunks
        all_splits = self.text_splitter.split_documents(documents)
        
        print(f"Created {len(all_splits)} text chunks from {len(documents)} documents")
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=all_splits,
            embedding=self.embeddings,
            persist_directory=config.CHROMA_DB_PATH
        )
        
        # Setup retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": config.RETRIEVAL_K}
        )
        
        # Create RAG chain
        self._create_rag_chain()
        
        return self.vectorstore
    
    def load_existing_vectorstore(self) -> Optional[Chroma]:
        """
        Load existing vector store from disk
        
        Returns:
            Loaded Chroma vector store or None if not found
        """
        chroma_path = Path(config.CHROMA_DB_PATH)
        
        if not chroma_path.exists():
            print(f"No existing vector store found at {chroma_path}")
            return None
        
        try:
            self.vectorstore = Chroma(
                persist_directory=config.CHROMA_DB_PATH,
                embedding_function=self.embeddings
            )
            
            # Check if vectorstore has documents
            if self.vectorstore._collection.count() == 0:
                print("Vector store exists but is empty")
                return None
            
            # Setup retriever
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": config.RETRIEVAL_K}
            )
            
            # Create RAG chain
            self._create_rag_chain()
            
            print(f"Loaded existing vector store with {self.vectorstore._collection.count()} documents")
            return self.vectorstore
            
        except Exception as e:
            print(f"Error loading vector store: {e}")
            return None
    
    def _create_rag_chain(self):
        """Create the RAG chain for question answering"""
        if not self.retriever:
            raise ValueError("Retriever not initialized. Create or load vector store first.")
        
        def format_docs(docs):
            """Format retrieved documents for context"""
            formatted = []
            for doc in docs:
                # Extract metadata for reference
                metadata = doc.metadata
                reference = metadata.get('reference', 'Unknown Reference')
                content = doc.page_content
                
                formatted.append(f"[{reference}] {content}")
            
            return "\n\n".join(formatted)
        
        # Create the RAG chain
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    @traceable
    def ask_question(self, question: str) -> str:
        """
        Ask a question and get an answer from the RAG system
        
        Args:
            question: The question to ask
            
        Returns:
            Generated answer based on retrieved context
        """
        if not self.rag_chain:
            raise ValueError("RAG chain not initialized. Create or load vector store first.")
        
        try:
            response = self.rag_chain.invoke(question)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    @traceable
    def ask_question_stream(self, question: str):
        """
        Ask a question and get a streaming answer from the RAG system
        
        Args:
            question: The question to ask
            
        Yields:
            Streaming chunks of the generated answer
        """
        if not self.rag_chain:
            raise ValueError("RAG chain not initialized. Create or load vector store first.")
        
        try:
            for chunk in self.rag_chain.stream(question):
                yield chunk
        except Exception as e:
            yield f"Error generating response: {str(e)}"
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with vector store statistics
        """
        if not self.vectorstore:
            return {"status": "No vector store loaded"}
        
        try:
            count = self.vectorstore._collection.count()
            return {
                "status": "Ready",
                "document_count": count,
                "database_path": config.CHROMA_DB_PATH
            }
        except Exception as e:
            return {"status": f"Error: {str(e)}"}

    def is_ready(self) -> bool:
        """Check if the RAG engine is ready to answer questions"""
        return self.rag_chain is not None 