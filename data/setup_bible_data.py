#!/usr/bin/env python3
"""
Biblical RAG Data Setup Script

This script loads and processes the complete KJV Bible data for the RAG system.
Requires KJV.json in the data/ directory.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from data.bible_seeder import BibleDataSeeder
from utils.document_processor import DocumentProcessor
from core.rag_engine import BiblicalRAGEngine
from config.settings import config


def setup_bible_data():
    """Setup and process complete KJV Bible data for the RAG system"""
    
    print("🙏 Biblical RAG Data Setup")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Validate configuration
        print("✅ Validating configuration...")
        config.validate_config()
        
        # Initialize seeder
        print("\n📖 Initializing Bible data seeder...")
        seeder = BibleDataSeeder()
        
        # Check if KJV.json exists and show stats
        kjv_path = Path("data/KJV.json")
        if kjv_path.exists():
            print(f"\n📚 KJV.json found ({kjv_path.stat().st_size / 1024 / 1024:.1f} MB)")
            
            stats = seeder.get_bible_stats()
            if "error" not in stats:
                print(f"   Translation: {stats['translation']}")
                print(f"   Books: {stats['total_books']}")
                print(f"   Chapters: {stats['total_chapters']}")
                print(f"   Verses: {stats['total_verses']}")
        else:
            print(f"\n⚠️  KJV.json not found at {kjv_path}")
            print("   Will use minimal fallback data")
        
        # Load Bible data (always attempts full KJV, falls back if needed)
        print(f"\n📖 Loading Bible data...")
        bible_data = seeder.load_bible_data()
        
        if len(bible_data) > 1000:
            print(f"   ✅ Loaded complete Bible: {len(bible_data)} verses")
            print("   This will take several minutes to process...")
        else:
            print(f"   ⚠️  Using minimal fallback: {len(bible_data)} verses")
        
        # Convert to documents
        print(f"\n📄 Converting to LangChain documents...")
        documents = DocumentProcessor.create_documents_from_bible_data(bible_data)
        print(f"   ✅ Created {len(documents)} documents")
        
        # Initialize RAG engine
        print(f"\n🤖 Initializing RAG engine...")
        rag_engine = BiblicalRAGEngine()
        print("   ✅ RAG engine initialized")
        
        # Create vector database
        print(f"\n🔍 Creating vector database...")
        
        # Remove existing vector store if it exists
        import shutil
        chroma_path = Path(config.CHROMA_DB_PATH)
        if chroma_path.exists():
            print(f"   Removing existing vector store...")
            shutil.rmtree(chroma_path)
        
        vectorstore = rag_engine.create_vectorstore(documents)
        print(f"   ✅ Vector database created successfully")
        

        elapsed_time = time.time() - start_time
        print(f"\n🎉 Setup completed successfully!")
        print(f"   Processing time: {elapsed_time:.1f} seconds")
        print(f"   Verses processed: {len(bible_data)}")
        print(f"\n📖 Your Biblical RAG system is ready!")
        print(f"   Run: streamlit run app.py")
        
        if not kjv_path.exists():
            print(f"\n💡 To use complete Bible:")
            print(f"   1. Add KJV.json to data/ directory")
            print(f"   2. Run this setup script again")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    setup_bible_data()

