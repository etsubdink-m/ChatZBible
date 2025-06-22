"""
Main script for testing Biblical RAG Chatbot
Simple command-line interface for testing
"""
from pathlib import Path

from core.rag_engine import BiblicalRAGEngine
from data.bible_seeder import BibleDataSeeder
from config.settings import config


def test_rag_system():
    """Test the RAG system with sample questions"""
    print("🙏 Initializing Biblical RAG Chatbot...")
    
    try:
        # Initialize RAG engine
        rag_engine = BiblicalRAGEngine()
        
        # Try to load existing vector store
        vectorstore = rag_engine.load_existing_vectorstore()
        
        if vectorstore is None:
            print("📚 No existing database found. Creating new one...")
            
            # Create sample data
            seeder = BibleDataSeeder()
            bible_data = seeder.load_bible_data()
            
            # Convert to documents (we'll do this in the engine for now)
            from langchain_core.documents import Document
            
            documents = []
            for verse in bible_data:
                doc = Document(
                    page_content=verse['text'],
                    metadata={
                        'book': verse['book'],
                        'chapter': verse['chapter'],
                        'verse': verse['verse'],
                        'reference': f"{verse['book']} {verse['chapter']}:{verse['verse']}",
                        'translation': verse.get('translation', 'KJV')
                    }
                )
                documents.append(doc)
            
            # Create vector store
            rag_engine.create_vectorstore(documents)
            print(f"✅ Created database with {len(documents)} documents!")
        
        # Test questions
        test_questions = [
            "What does the Bible say about creation?",
            "Tell me about God's love for the world",
            "What does Psalm 23 say about God as shepherd?"
        ]
        
        print("\n" + "="*50)
        print("🔍 Testing RAG System")
        print("="*50)
        
        for question in test_questions:
            print(f"\n❓ Question: {question}")
            print("-" * 30)
            
            response = rag_engine.ask_question(question)
            print(f"📖 Answer: {response}")
            print()
        
        # Interactive mode
        print("\n" + "="*50)
        print("💬 Interactive Mode (type 'quit' to exit)")
        print("="*50)
        
        while True:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                break
            
            if question:
                response = rag_engine.ask_question(question)
                print(f"📖 Answer: {response}")
        
        print("\n👋 Thank you for using the Biblical RAG Chatbot!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Please check your .env file and ensure OPENAI_API_KEY is set")


if __name__ == "__main__":
    test_rag_system() 