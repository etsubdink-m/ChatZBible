"""
Streamlit App for Biblical RAG Chatbot
Main UI interface for the chatbot
"""
import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from core.rag_engine import BiblicalRAGEngine
from data.bible_seeder import BibleDataSeeder
from utils.document_processor import DocumentProcessor
from config.settings import config


def initialize_rag_engine():
    """Initialize the RAG engine with error handling"""
    try:
        # Initialize RAG engine
        rag_engine = BiblicalRAGEngine()
        
        # Try to load existing vector store
        vectorstore = rag_engine.load_existing_vectorstore()
        
        if vectorstore is None:
            st.info("No existing database found. Creating new one with sample data...")
            
            # Create sample data
            seeder = BibleDataSeeder()
            bible_data = seeder.load_bible_data()
            
            # Convert to documents
            documents = DocumentProcessor.create_documents_from_bible_data(bible_data)
            
            # Create vector store
            rag_engine.create_vectorstore(documents)
            
            st.success(f"✅ Created new database with {len(documents)} documents!")
        
        return rag_engine
        
    except Exception as e:
        st.error(f"❌ Error initializing RAG engine: {str(e)}")
        st.info("Please check your API key in the .env file")
        return None


def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon=config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title(config.APP_TITLE)
    st.markdown("Ask questions about the Bible and get scripture-based answers!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "rag_engine" not in st.session_state:
        with st.spinner("Initializing Biblical RAG system..."):
            st.session_state.rag_engine = initialize_rag_engine()
    
    # Sidebar
    with st.sidebar:
        st.header("📖 System Information")
        
        if st.session_state.rag_engine:
            stats = st.session_state.rag_engine.get_stats()
            st.success(f"Status: {stats['status']}")
            st.info(f"Documents: {stats.get('document_count', 'N/A')}")
            
            # System settings
            st.header("⚙️ Settings")
            
            # Clear conversation
            if st.button("🗑️ Clear Conversation"):
                st.session_state.messages = []
                st.rerun()
            
            # Rebuild database
            if st.button("🔄 Rebuild Database"):
                st.session_state.rag_engine = None
                st.rerun()
            
            # Example questions
            st.header("💡 Example Questions")
            example_questions = [
                "What does the Bible say about creation?",
                "Tell me about God's love for the world",
                "What is the Lord's Prayer?",
                "How does the Bible describe love?",
                "What does Psalm 23 say about God as shepherd?"
            ]
            
            for question in example_questions:
                if st.button(f"💬 {question[:30]}..."):
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()
        
        else:
            st.error("❌ System not ready")
    
    # Main chat interface
    if st.session_state.rag_engine and st.session_state.rag_engine.is_ready():
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a biblical question..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Searching scriptures..."):
                    response = st.session_state.rag_engine.ask_question(prompt)
                    st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        st.warning("⚠️ Please configure your API key and restart the application")
        st.markdown("""
        ### Setup Instructions:
        1. Copy `env_template.txt` to `.env`
        2. Add your Google API key to the `.env` file
        3. Restart the application
        """)


if __name__ == "__main__":
    main() 