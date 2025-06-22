#!/usr/bin/env python3
"""
Simple setup trigger for Biblical RAG system
Can be run locally or triggered from Streamlit
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Run the download and setup process"""
    
    print("🙏 Biblical RAG Quick Setup")
    print("========================")
    
    setup_script = Path("data/download_and_setup.py")
    
    if not setup_script.exists():
        print("❌ Setup script not found!")
        sys.exit(1)
    
    print("🚀 Starting automatic setup...")
    print("This will download KJV Bible data and create embeddings")
    
    try:
        result = subprocess.run([sys.executable, str(setup_script)], check=True)
        print("\n🎉 Setup complete!")
        print("Run the app with: streamlit run app.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed with return code {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 