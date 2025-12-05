"""
System Verification Script
Tests all components before running the main application
"""

import sys
import os
from pathlib import Path

def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def check_python_version():
    """Check Python version"""
    print_section("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python 3.8 or higher required")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print_section("Dependency Check")
    
    dependencies = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing',
        'sentence_transformers': 'Text embeddings',
        'faiss': 'Vector search',
        'streamlit': 'Web interface',
        'PyPDF2': 'PDF processing',
        'reportlab': 'PDF generation',
        'groq': 'LLM integration'
    }
    
    all_installed = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print(f"✅ {package:25} - {description}")
        except ImportError:
            print(f"❌ {package:25} - MISSING ({description})")
            all_installed = False
    
    if all_installed:
        print("\n✅ All dependencies installed")
    else:
        print("\n❌ Missing dependencies. Run: pip install -r requirements.txt")
    
    return all_installed

def check_environment_variables():
    """Check environment variables"""
    print_section("Environment Variables Check")
    
    groq_key = os.getenv('GROQ_API_KEY')
    
    if groq_key:
        print(f"✅ GROQ_API_KEY is set (length: {len(groq_key)} chars)")
        return True
    else:
        print("⚠️  GROQ_API_KEY not set")
        print("   The system will work for data generation but not for LLM responses")
        print("   Set it in .env file or as environment variable")
        return False

def check_data_files():
    """Check if data files exist"""
    print_section("Data Files Check")
    
    files_to_check = {
        'data/claims.csv': 'Claims data',
        'data/patients.csv': 'Patient data',
        'data/doctors.csv': 'Doctor data',
        'data/processed/documents.json': 'Processed CSV documents',
        'data/processed/pdf_documents.json': 'Processed PDF documents'
    }
    
    all_exist = True
    
    for filepath, description in files_to_check.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"✅ {filepath:40} ({size:.1f} KB)")
        else:
            print(f"❌ {filepath:40} MISSING")
            all_exist = False
    
    if all_exist:
        print("\n✅ All data files present")
    else:
        print("\n⚠️  Some data files missing. Run: python setup.py")
    
    return all_exist

def check_vector_stores():
    """Check if vector stores exist"""
    print_section("Vector Store Check")
    
    stores_to_check = {
        'data/vector_store/csv/faiss_index.bin': 'CSV FAISS index',
        'data/vector_store/csv/documents_metadata.pkl': 'CSV metadata',
        'data/vector_store/pdf/faiss_index.bin': 'PDF FAISS index',
        'data/vector_store/pdf/documents_metadata.pkl': 'PDF metadata'
    }
    
    all_exist = True
    
    for filepath, description in stores_to_check.items():
        if os.path.exists(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"✅ {description:30} ({size:.1f} KB)")
        else:
            print(f"❌ {description:30} MISSING")
            all_exist = False
    
    if all_exist:
        print("\n✅ All vector stores built")
    else:
        print("\n⚠️  Vector stores missing. Run: python rag/vector_store.py")
    
    return all_exist

def test_vector_store_loading():
    """Test loading vector stores"""
    print_section("Vector Store Loading Test")
    
    try:
        from rag.vector_store import MultiIndexManager
        
        manager = MultiIndexManager()
        manager.load_indices()
        
        print("✅ Vector stores loaded successfully")
        print(f"   CSV index: {manager.csv_store.index.ntotal} vectors")
        print(f"   PDF index: {manager.pdf_store.index.ntotal} vectors")
        return True
    
    except Exception as e:
        print(f"❌ Error loading vector stores: {e}")
        return False

def test_llm_connection():
    """Test LLM connection"""
    print_section("LLM Connection Test")
    
    try:
        from llm.groq_integration import GroqLLM
        
        llm = GroqLLM()
        print(f"✅ LLM initialized successfully")
        print(f"   Model: {llm.model}")
        
        # Try a simple test
        test_docs = ["Test document about insurance claims."]
        response = llm.generate_response(
            query="What is this about?",
            context_documents=test_docs,
            max_tokens=50
        )
        
        if response and "error" not in response.lower():
            print(f"✅ LLM responding correctly")
            print(f"   Sample response: {response[:100]}...")
            return True
        else:
            print(f"⚠️  LLM response may have issues")
            return False
    
    except Exception as e:
        print(f"❌ Error testing LLM: {e}")
        return False

def test_advanced_rag():
    """Test advanced RAG components"""
    print_section("Advanced RAG Components Test")
    
    try:
        from rag.advanced_rag import QueryRouter, QueryTranslator, QueryConstructor
        
        # Test router
        router = QueryRouter()
        routing = router.route_query("Show me denied claims for diabetes")
        print(f"✅ Query Router working")
        print(f"   Query type: {routing['query_type']}")
        
        # Test translator
        translator = QueryTranslator()
        translation = translator.translate("Show me denied claims for diabetes last quarter")
        print(f"✅ Query Translator working")
        print(f"   Entities: {translation['entities']}")
        
        # Test constructor
        constructor = QueryConstructor()
        variations = constructor.construct_queries("Show me claims", translation)
        print(f"✅ Query Constructor working")
        print(f"   Generated {len(variations)} query variations")
        
        return True
    
    except Exception as e:
        print(f"❌ Error testing RAG components: {e}")
        return False

def generate_report(results):
    """Generate final report"""
    print_section("VERIFICATION SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nTests Passed: {passed}/{total}")
    print("\nDetailed Results:")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED - System is ready!")
        print("\nYou can now run: streamlit run app.py")
    elif passed >= total - 2:
        print("⚠️  MOSTLY READY - Some optional components missing")
        print("\nYou can proceed, but some features may not work")
    else:
        print("❌ SYSTEM NOT READY - Please fix the issues above")
        print("\nRun: python setup.py")
    
    print("="*70)
    
    return passed == total

def main():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("  RAG-POWERED CLAIMS QUERY ASSISTANT")
    print("  System Verification")
    print("="*70)
    
    results = {}
    
    # Run checks
    results['Python Version'] = check_python_version()
    results['Dependencies'] = check_dependencies()
    results['Environment Variables'] = check_environment_variables()
    results['Data Files'] = check_data_files()
    results['Vector Stores'] = check_vector_stores()
    
    # Only run advanced tests if basic checks pass
    if results['Vector Stores']:
        results['Vector Store Loading'] = test_vector_store_loading()
    
    if results['Environment Variables'] and results['Dependencies']:
        results['LLM Connection'] = test_llm_connection()
    
    if results['Dependencies']:
        results['Advanced RAG'] = test_advanced_rag()
    
    # Generate report
    all_passed = generate_report(results)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
