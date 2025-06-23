"""
Streamlit App for Biblical Question & Answer Assistant
Simple, user-friendly interface for exploring the Bible
"""
import pysqlite3
import sys
sys.modules["sqlite3"] = sys.modules["pysqlite3"]

import streamlit as st
import sys
import subprocess
import time
import json
from pathlib import Path
import shutil
import gc

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from core.rag_engine import BiblicalRAGEngine
from config.settings import config


def check_if_setup_needed():
    """Check if the RAG system is already set up"""
    
    # Check if vector database exists
    chroma_path = Path(config.CHROMA_DB_PATH)
        
    if chroma_path.exists():
        return False, None
    
    return True, None


def run_bible_setup():
    """Run the Bible data setup process"""
    
    setup_script = Path("data/download_and_setup.py")
    
    if not setup_script.exists():
        st.error("Setup script not found!")
        return False
    
    # Create progress containers
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    with status_container:
        log_container = st.empty()
    
    try:
        # Start the setup process with proper encoding
        process = subprocess.Popen(
            [sys.executable, str(setup_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',  # Force UTF-8 encoding
            errors='replace'   # Replace problematic characters
        )
        
        log_messages = []
        progress_value = 10
        
        # Read output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            
            if output:
                line = output.strip()
                log_messages.append(line)
                
                # Update progress based on keywords
                if "Downloading" in line:
                    progress_value = min(progress_value + 5, 30)
                elif "Loading Bible data" in line:
                    progress_value = 40
                elif "Converting to LangChain" in line:
                    progress_value = 50
                elif "Initializing RAG engine" in line:
                    progress_value = 60
                elif "Creating vector database" in line:
                    progress_value = 70
                elif "Vector database created" in line:
                    progress_value = 95
                elif "Setup completed" in line:
                    progress_value = 100
                
                progress_bar.progress(progress_value)
                status_text.text(line)
                
                # Show recent log messages
                recent_logs = log_messages[-10:]  # Show last 10 messages
                log_text = "\n".join(recent_logs)
                log_container.text(log_text)
        
        # Wait for process to complete
        return_code = process.wait()
        
        if return_code == 0:
            progress_bar.progress(100)
            status_text.text("Setup completed successfully!")
            st.success("Biblical assistant is ready!")
            time.sleep(2)
            st.rerun()
            return True
        else:
            stderr = process.stderr.read()
            st.error(f"Setup failed with return code {return_code}")
            if stderr:
                st.error(f"Error: {stderr}")
            return False
            
    except Exception as e:
        st.error(f"Failed to run setup: {str(e)}")
        return False


def initialize_rag_engine():
    """Initialize the RAG engine with pre-loaded data"""
    try:
        # Initialize RAG engine
        rag_engine = BiblicalRAGEngine()
        
        # Try to load existing vector store
        vectorstore = rag_engine.load_existing_vectorstore()
        
        if vectorstore is None:
            return None
            
        return rag_engine
        
    except Exception as e:
        st.error(f"❌ Error loading system: {str(e)}")
        return None


def safe_cleanup_system():
    """Safely cleanup the RAG system and delete files"""
    try:
        # Step 1: Clear the RAG engine from session state
        if "rag_engine" in st.session_state:
            # Try to close any connections if the engine has such methods
            rag_engine = st.session_state.rag_engine
            if hasattr(rag_engine, 'vectorstore') and rag_engine.vectorstore:
                # Clear the vectorstore reference
                rag_engine.vectorstore = None
            if hasattr(rag_engine, 'rag_chain') and rag_engine.rag_chain:
                # Clear the RAG chain reference
                rag_engine.rag_chain = None
            
            # Remove from session state
            del st.session_state.rag_engine
        
        # Step 2: Force garbage collection
        gc.collect()
        
        # Step 3: Small delay to let Windows release file handles
        time.sleep(1)
        
        # Step 4: Try to delete the directory
        chroma_path = Path(config.CHROMA_DB_PATH)
        if chroma_path.exists():
            # Try multiple times with increasing delays (Windows file locking workaround)
            for attempt in range(3):
                try:
                    shutil.rmtree(chroma_path)
                    return True
                except PermissionError as e:
                    if attempt < 2:  # Not the last attempt
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                        continue
                    else:
                        # Last attempt failed, try alternative cleanup
                        return force_delete_directory(chroma_path)
        
        return True
        
    except Exception as e:
        st.error(f"Error during cleanup: {str(e)}")
        return False


def force_delete_directory(path):
    """Force delete directory on Windows using alternative methods"""
    try:
        import subprocess
        import platform
        
        if platform.system() == "Windows":
            # Use Windows rmdir command with force flag
            result = subprocess.run(
                ['rmdir', '/s', '/q', str(path)], 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                return True
            else:
                # Try robocopy method (Windows advanced file operations)
                empty_dir = path.parent / "empty_temp_dir"
                empty_dir.mkdir(exist_ok=True)
                
                subprocess.run([
                    'robocopy', 
                    str(empty_dir), 
                    str(path), 
                    '/mir', 
                    '/r:0', 
                    '/w:0'
                ], shell=True, capture_output=True)
                
                # Clean up
                shutil.rmtree(empty_dir, ignore_errors=True)
                shutil.rmtree(path, ignore_errors=True)
                
                return not path.exists()
        else:
            # For non-Windows systems, use regular shutil
            shutil.rmtree(path)
            return True
            
    except Exception as e:
        st.error(f"Force delete failed: {str(e)}")
        # Last resort: rename the directory so a new one can be created
        try:
            backup_path = path.parent / f"{path.name}_backup_{int(time.time())}"
            path.rename(backup_path)
            st.warning(f"Could not delete files. Renamed old database to: {backup_path.name}")
            return True
        except:
            return False


def show_setup_page():
    """Show the setup page when system is not ready"""
    
    st.title(f"✝️ {config.APP_TITLE} Setup")
    st.markdown(f"Welcome! Let's set up your ✝️ {config.APP_TITLE} system.")
    
    # Check current status
    setup_needed, summary = check_if_setup_needed()
    
    if not setup_needed:
        st.success("✅ System is ready!")
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Start Chatting", type="primary"):
                st.rerun()
        with col2:
            if st.button("🔄 Re-setup System"):
                with st.spinner("Cleaning up old system..."):
                    success = safe_cleanup_system()
                    if success:
                        st.success("✅ Cleanup successful! Redirecting to setup...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Cleanup failed. You may need to manually delete the data/chroma_db folder.")
        return
    
    # Show setup information
    st.info("""
    This will:
    1. 📥 Download complete KJV Bible data (~8MB)
    2. 🔍 Create search capabilities for all verses
    3. 💾 Set up the question-answering system
    
    ⏱️ **Estimated time:** 5-10 minutes
    """)
    
    # Setup button
    if st.button(f"🚀 Setup ✝️ {config.APP_TITLE}", type="primary"):
        st.warning("⏳ **Please wait!** This takes several minutes. Do not close this tab.")
        
        with st.spinner(f"Setting up ✝️ {config.APP_TITLE}..."):
            success = run_bible_setup()
            
            if success:
                st.balloons()
                time.sleep(2)
                st.rerun()


def show_starter_questions():
    """Show example questions as clickable cards when no conversation exists"""
    
    st.markdown("### 💡 Try asking about:")
    
    example_questions = [
        "What does the Bible say about creation?",
        "Tell me about God's love for the world",
        "What is the Lord's Prayer?",
        "How does the Bible describe love?",
        "What does Psalm 23 say about God as shepherd?"
    ]
    
    # Create columns for better layout
    cols = st.columns(2)
    
    for i, question in enumerate(example_questions):
        col = cols[i % 2]
        with col:
            if st.button(
                f"💬 {question}",
                key=f"example_{i}",
                use_container_width=True,
                help="Click to ask this question"
            ):
                # Add the question to chat history
                st.session_state.messages.append({"role": "user", "content": question})
                # Set a flag to trigger response generation
                st.session_state.generate_response = question
                st.rerun()


def show_chat_page():
    """Show the main chat interface"""
    
    # Main title
    st.title(f"✝️ {config.APP_TITLE}")
    st.markdown("Ask questions about the Bible and get scripture-based answers!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "rag_engine" not in st.session_state:
        with st.spinner("Loading biblical assistant..."):
            st.session_state.rag_engine = initialize_rag_engine()
    
    # Simplified sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        if st.session_state.rag_engine:
            st.success("✅ Ready to answer questions")
            
            # Clear conversation
            if st.button("🗑️ Clear Conversation"):
                st.session_state.messages = []
                # Clear any pending response generation
                if "generate_response" in st.session_state:
                    del st.session_state.generate_response
                st.rerun()

        else:
            st.error("❌ System not ready")
            if st.button("🔄 Return to Setup"):
                st.rerun()
    
    # Main chat interface
    if st.session_state.rag_engine and st.session_state.rag_engine.is_ready():
        
        # Show starter questions if no conversation exists
        if not st.session_state.messages:
            show_starter_questions()
            st.markdown("---")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Check if we need to generate a response from starter question
        if "generate_response" in st.session_state:
            question = st.session_state.generate_response
            del st.session_state.generate_response  # Clear the flag
            
            # Generate streaming response for the starter question
            with st.chat_message("assistant"):
                def response_generator():
                    """Generator function for streaming biblical responses"""
                    try:
                        for chunk in st.session_state.rag_engine.ask_question_stream(question):
                            yield chunk
                    except Exception as e:
                        yield f"Error: {str(e)}"
                
                with st.spinner("Thinking..."):
                    # Use Streamlit's write_stream for typewriter effect
                    response = st.write_stream(response_generator())
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()  # Rerun to show the complete conversation
        
        # Chat input with streaming
        if prompt := st.chat_input("Ask a biblical question..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate streaming response
            with st.chat_message("assistant"):
                def response_generator():
                    """Generator function for streaming biblical responses"""
                    try:
                        for chunk in st.session_state.rag_engine.ask_question_stream(prompt):
                            yield chunk
                    except Exception as e:
                        yield f"Error: {str(e)}"
                
                with st.spinner("Searching scriptures..."):
                    # Use Streamlit's write_stream for typewriter effect
                    response = st.write_stream(response_generator())
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    else:
        st.error("❌ System not available")
        if st.button("🔄 Return to Setup"):
            st.rerun()


def main():
    """Main application"""
    
    # Page configuration
    st.set_page_config(
        page_title=f"{config.APP_TITLE}",
        page_icon=config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if setup is needed
    setup_needed, _ = check_if_setup_needed()
    
    if setup_needed:
        show_setup_page()
    else:
        show_chat_page()


if __name__ == "__main__":
    main() 