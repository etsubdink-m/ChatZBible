#!/usr/bin/env python3
"""
Download KJV Bible data and setup RAG system for Streamlit deployment
"""

import sys
import time
import requests
import json
from pathlib import Path
import shutil

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from data.bible_seeder import BibleDataSeeder
from utils.document_processor import DocumentProcessor
from core.rag_engine import BiblicalRAGEngine
from config.settings import config


def download_kjv_bible(progress_callback=None):
    """Download KJV.json from GitHub repository"""
    
    kjv_url = "https://github.com/scrollmapper/bible_databases/raw/refs/heads/master/formats/json/KJV.json"
    kjv_path = Path("data/KJV.json")
    
    if progress_callback:
        progress_callback("📥 Downloading KJV Bible data from GitHub...")
    
    try:
        print("📥 Downloading KJV Bible data...")
        print(f"   Source: {kjv_url}")
        print(f"   Target: {kjv_path}")
        
        # Create data directory if it doesn't exist
        kjv_path.parent.mkdir(exist_ok=True)
        
        # Download with progress
        response = requests.get(kjv_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(kjv_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0 and progress_callback:
                        percent = (downloaded / total_size) * 100
                        progress_callback(f"📥 Downloading... {percent:.1f}% ({downloaded / 1024 / 1024:.1f} MB)")
        
        print(f"   ✅ Downloaded {kjv_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        # Validate JSON
        try:
            with open(kjv_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            verse_count = sum(
                len(verse['verses']) 
                for book in data['books'] 
                for verse in book['chapters']
            )
            
            print(f"   ✅ Validation successful: {verse_count} verses found")
            
            if progress_callback:
                progress_callback(f"✅ Downloaded complete! {verse_count} verses ready")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON downloaded: {e}")
            if kjv_path.exists():
                kjv_path.unlink()
            return False
            
    except requests.RequestException as e:
        print(f"   ❌ Download failed: {e}")
        if progress_callback:
            progress_callback(f"❌ Download failed: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        if progress_callback:
            progress_callback(f"❌ Error: {str(e)}")
        return False


def setup_bible_data_with_download(progress_callback=None):
    """Download KJV data and setup RAG system"""
    
    if progress_callback:
        progress_callback("🙏 Starting Biblical RAG Setup...")
    
    print("🙏 Biblical RAG Data Setup with Download")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Validate configuration
        if progress_callback:
            progress_callback("✅ Validating configuration...")
        
        config.validate_config()
        
        # Check if KJV.json exists, download if not
        kjv_path = Path("data/KJV.json")
        
        if not kjv_path.exists():
            if progress_callback:
                progress_callback("📥 KJV.json not found, downloading...")
            
            success = download_kjv_bible(progress_callback)
            if not success:
                raise Exception("Failed to download KJV Bible data")
        else:
            file_size = kjv_path.stat().st_size / 1024 / 1024
            if progress_callback:
                progress_callback(f"✅ KJV.json found ({file_size:.1f} MB)")
        
        # Initialize seeder
        if progress_callback:
            progress_callback("📖 Initializing Bible data seeder...")
        
        seeder = BibleDataSeeder()
        
        # Show Bible statistics
        stats = seeder.get_bible_stats()
        if "error" not in stats:
            stats_msg = f"📊 {stats['total_books']} books, {stats['total_chapters']} chapters, {stats['total_verses']} verses"
            print(f"   {stats_msg}")
            if progress_callback:
                progress_callback(stats_msg)
        
        # Load Bible data
        if progress_callback:
            progress_callback("📖 Loading Bible data...")
        
        bible_data = seeder.load_bible_data()
        
        if len(bible_data) > 1000:
            data_msg = f"✅ Loaded complete Bible: {len(bible_data)} verses"
            print(f"   {data_msg}")
            if progress_callback:
                progress_callback(data_msg)
                progress_callback("⏳ Processing embeddings (this may take 5-10 minutes)...")
        
        # Convert to documents
        if progress_callback:
            progress_callback("📄 Converting to LangChain documents...")
        
        documents = DocumentProcessor.create_documents_from_bible_data(bible_data)
        doc_msg = f"✅ Created {len(documents)} documents"
        print(f"   {doc_msg}")
        
        # Initialize RAG engine
        if progress_callback:
            progress_callback("🤖 Initializing RAG engine...")
        
        rag_engine = BiblicalRAGEngine()
        
        # Create vector database
        if progress_callback:
            progress_callback("🔍 Creating vector database (this is the slow part)...")
        
        # Remove existing vector store if it exists
        chroma_path = Path(config.CHROMA_DB_PATH)
        if chroma_path.exists():
            if progress_callback:
                progress_callback("🗑️ Removing existing vector store...")
            shutil.rmtree(chroma_path)
        
        vectorstore = rag_engine.create_vectorstore(documents)
        
        if progress_callback:
            progress_callback("✅ Vector database created successfully!")
        
        # Test the system
        if progress_callback:
            progress_callback("🧪 Testing the RAG system...")
        
        test_questions = ["What does the Bible say about creation?"]
        
        for question in test_questions:
            try:
                response = rag_engine.ask_question(question)
                test_msg = f"✅ Test successful ({len(response)} characters)"
                print(f"   {test_msg}")
                if progress_callback:
                    progress_callback(test_msg)
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
        
        # Save processing summary
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "verses_loaded": len(bible_data),
            "documents_created": len(documents),
            "vector_db_path": config.CHROMA_DB_PATH,
            "processing_time_seconds": time.time() - start_time,
            "auto_downloaded": True
        }
        
        elapsed_time = time.time() - start_time
        success_msg = f"🎉 Setup completed! ({elapsed_time:.1f} seconds, {len(bible_data)} verses)"
        print(success_msg)
        
        if progress_callback:
            progress_callback(success_msg)
            progress_callback("📖 Biblical RAG system is ready!")
        
        return True
        
    except Exception as e:
        error_msg = f"❌ Setup failed: {str(e)}"
        print(error_msg)
        if progress_callback:
            progress_callback(error_msg)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    def print_progress(message):
        print(f"[PROGRESS] {message}")
    
    success = setup_bible_data_with_download(print_progress)
    sys.exit(0 if success else 1) 