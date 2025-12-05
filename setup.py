"""
Complete setup script for RAG-Powered Claims Query Assistant
Runs all data generation and indexing steps
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_script(script_path, description):
    """Run a Python script and handle errors"""
    print(f"Running: {description}")
    print(f"Script: {script_path}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} completed successfully!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'pandas', 'numpy', 'sentence_transformers', 'faiss',
        'streamlit', 'PyPDF2', 'reportlab', 'groq'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!")
    return True

def check_environment():
    """Check environment variables"""
    print_header("Checking Environment Variables")
    
    api_key = os.getenv('GROQ_API_KEY')
    if api_key:
        print(f"✅ GROQ_API_KEY is set (ends with: ...{api_key[-4:]})")
        return True
    else:
        print("⚠️  GROQ_API_KEY not set")
        print("Please set it in .env file or as environment variable")
        print("The system will work for data generation but not for LLM responses")
        return False

def main():
    """Main setup function"""
    print_header("RAG-Powered Claims Query Assistant - Complete Setup")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install dependencies first: pip install -r requirements.txt")
        return False
    
    # Check environment
    env_ok = check_environment()
    
    # Create necessary directories
    print_header("Creating Directory Structure")
    directories = [
        'data',
        'data/processed',
        'data/pdf_documents',
        'data/vector_store',
        'data/vector_store/csv',
        'data/vector_store/pdf'
    ]
    
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ {dir_path}")
    
    print("\n✅ Directory structure created!")
    
    # Step 1: Generate mock claims data
    print_header("STEP 1: Generate Mock Claims Data")
    if not run_script(
        'data_generation/generate_mock_data.py',
        'Mock claims data generation'
    ):
        print("❌ Setup failed at Step 1")
        return False
    
    # Step 2: Generate PDF documents
    print_header("STEP 2: Generate PDF Documents")
    if not run_script(
        'data_generation/generate_pdf_documents.py',
        'PDF document generation'
    ):
        print("❌ Setup failed at Step 2")
        return False
    
    # Step 3: Run ETL pipeline
    print_header("STEP 3: Run ETL Pipeline")
    if not run_script(
        'etl/data_processor.py',
        'ETL data processing'
    ):
        print("❌ Setup failed at Step 3")
        return False
    
    # Step 4: Process PDF documents
    print_header("STEP 4: Process PDF Documents")
    if not run_script(
        'etl/pdf_processor.py',
        'PDF document processing'
    ):
        print("❌ Setup failed at Step 4")
        return False
    
    # Step 5: Build vector stores
    print_header("STEP 5: Build Vector Stores")
    print("⚠️  This step may take 2-3 minutes and will download embedding models...")
    if not run_script(
        'rag/vector_store.py',
        'Vector store building'
    ):
        print("❌ Setup failed at Step 5")
        return False
    
    # Final summary
    print_header("🎉 SETUP COMPLETE!")
    
    print("✅ All components successfully set up!")
    print("\nGenerated:")
    print("  • 3,000 insurance claims with patients and doctors")
    print("  • 5 PDF policy and reference documents")
    print("  • Processed and enriched datasets")
    print("  • FAISS vector indices for retrieval")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    
    if env_ok:
        print("\n1. Launch the application:")
        print("   streamlit run app.py")
        print("\n2. Open your browser to: http://localhost:8501")
        print("\n3. Click 'Initialize System' in the sidebar")
        print("\n4. Start asking questions!")
    else:
        print("\n1. Set your GROQ_API_KEY:")
        print("   • Copy .env.example to .env")
        print("   • Add your API key to .env file")
        print("\n2. Launch the application:")
        print("   streamlit run app.py")
        print("\n3. Open your browser to: http://localhost:8501")
    
    print("\n" + "="*70)
    print("Example queries to try:")
    print("="*70)
    print("  • Show me denied claims for diabetes patients last quarter")
    print("  • What are the pre-authorization requirements?")
    print("  • How many claims were processed in Q3 2024?")
    print("  • List claims denied due to missing documentation")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
