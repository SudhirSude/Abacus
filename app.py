"""
Streamlit Frontend for RAG-Powered Claims Query Assistant
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag.vector_store import MultiIndexManager
from rag.advanced_rag import AdvancedRAGPipeline
from llm.groq_integration import GroqLLM, RAGResponseGenerator
import pandas as pd
import json

# Page configuration
st.set_page_config(
    page_title="Insurance Claims Query Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4788;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .query-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f4788;
        color: #1a1a1a;
    }
    .response-box {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4caf50;
        color: #000000;
    }
    .document-box {
        background-color: #fff9e6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .metadata-badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        background-color: #1f4788;
        color: white;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        margin: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.vector_store = None
    st.session_state.rag_pipeline = None
    st.session_state.response_generator = None
    st.session_state.chat_history = []
    st.session_state.data_loaded = False

def initialize_system():
    """Initialize the RAG system"""
    try:
        with st.spinner("🔄 Initializing system... This may take a moment."):
            # Check if vector stores exist
            csv_index_path = "data/vector_store/csv/faiss_index.bin"
            pdf_index_path = "data/vector_store/pdf/faiss_index.bin"
            
            if not os.path.exists(csv_index_path):
                st.error("❌ Vector store not found. Please run data generation and ETL first.")
                st.info("Run these commands in order:\n1. python data_generation/generate_mock_data.py\n2. python data_generation/generate_pdf_documents.py\n3. python etl/data_processor.py\n4. python etl/pdf_processor.py\n5. python rag/vector_store.py")
                return False
            
            # Load vector stores
            st.session_state.vector_store = MultiIndexManager()
            st.session_state.vector_store.load_indices()
            
            # Initialize RAG pipeline
            st.session_state.rag_pipeline = AdvancedRAGPipeline(
                st.session_state.vector_store
            )
            
            # Initialize LLM
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                st.warning("⚠️ GROQ_API_KEY not found in environment variables. Some features may be limited.")
                return False
            
            llm = GroqLLM(api_key=api_key)
            
            # Initialize response generator
            st.session_state.response_generator = RAGResponseGenerator(
                st.session_state.rag_pipeline,
                llm
            )
            
            st.session_state.initialized = True
            return True
    
    except Exception as e:
        st.error(f"❌ Error initializing system: {e}")
        return False

def load_data_summary():
    """Load summary statistics from processed data"""
    try:
        claims_path = "data/processed/enriched_claims.csv"
        if os.path.exists(claims_path):
            df = pd.read_csv(claims_path)
            return {
                'total_claims': len(df),
                'approved_claims': len(df[df['claim_status'] == 'Approved']),
                'denied_claims': len(df[df['claim_status'] == 'Denied']),
                'total_amount': df['claim_amount'].sum(),
                'approved_amount': df['approved_amount'].sum(),
                'date_range': f"{df['claim_date'].min()} to {df['claim_date'].max()}"
            }
        return None
    except Exception as e:
        st.error(f"Error loading data summary: {e}")
        return None

def display_sidebar():
    """Display sidebar with system info and controls"""
    with st.sidebar:
        st.markdown("## 🏥 Claims Query Assistant")
        st.markdown("---")
        
        # System status
        st.markdown("### System Status")
        if st.session_state.initialized:
            st.success("✅ System Ready")
        else:
            st.warning("⚠️ System Not Initialized")
            if st.button("Initialize System"):
                if initialize_system():
                    st.success("✅ System initialized successfully!")
                    st.rerun()
        
        st.markdown("---")
        
        # Data summary
        if st.session_state.initialized:
            st.markdown("### 📊 Data Summary")
            summary = load_data_summary()
            if summary:
                st.metric("Total Claims", f"{summary['total_claims']:,}")
                st.metric("Approved Claims", f"{summary['approved_claims']:,}")
                st.metric("Denied Claims", f"{summary['denied_claims']:,}")
                st.metric("Total Amount", f"${summary['total_amount']:,.2f}")
                st.metric("Date Range", summary['date_range'])
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        example_queries = [
            "Show me denied claims for diabetes patients last quarter",
            "What are the pre-authorization requirements?",
            "How many claims were processed in Q3 2024?",
            "What is covered for cancer treatment?",
            "List claims denied due to missing documentation",
            "What's the average claim amount for cardiology?"
        ]
        
        for query in example_queries:
            if st.button(f"📝 {query[:40]}...", key=f"example_{query}", use_container_width=True):
                st.session_state.current_query = query
                st.rerun()
        
        st.markdown("---")
        
        # Settings
        st.markdown("### ⚙️ Settings")
        st.session_state.show_documents = st.checkbox("Show Retrieved Documents", value=True)
        st.session_state.show_metadata = st.checkbox("Show Query Metadata", value=False)
        st.session_state.top_k = st.slider("Number of Documents", 5, 20, 10)
        
        # Clear history
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            if st.session_state.response_generator:
                st.session_state.response_generator.clear_conversation()
            st.success("Chat history cleared!")
            st.rerun()

def display_chat_history():
    """Display chat history"""
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation History")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):
            with st.expander(f"Query {len(st.session_state.chat_history) - i}: {chat['query'][:50]}..."):
                st.markdown(f"**Question:** {chat['query']}")
                st.markdown(f"**Answer:** {chat['response']}")
                
                if st.session_state.show_metadata and 'metadata' in chat:
                    st.markdown("**Metadata:**")
                    st.json(chat['metadata'])

def process_query(query: str):
    """Process user query"""
    if not st.session_state.initialized or not st.session_state.response_generator:
        st.error("System not initialized. Please initialize from sidebar.")
        return
    
    try:
        with st.spinner("🔍 Searching and generating response..."):
            # Generate response
            result = st.session_state.response_generator.generate_response(
                query=query,
                top_k=st.session_state.top_k,
                use_history=True
            )
            
            # Add to chat history
            chat_entry = {
                'query': query,
                'response': result['response'],
                'metadata': {
                    'routing': result['routing_info'],
                    'entities': result['entities_extracted'],
                    'num_documents': result['num_documents_used']
                }
            }
            
            if 'documents_preview' in result:
                chat_entry['documents'] = result['documents_preview']
            
            st.session_state.chat_history.append(chat_entry)
            
            # Display query box
            st.markdown(f"""
            <div class="query-box" style="background-color: #e8f4f8; color: #1a1a1a;">
                <strong style="color: #1a1a1a;">Your Question:</strong> <span style="color: #1a1a1a;">{query}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display response
            display_response(result)
    
    except Exception as e:
        st.error(f"Error processing query: {e}")

def display_response(result):
    """Display query response"""
    st.markdown("### 🤖 Assistant Response")
    
    # Response box
    st.markdown(f"""
    <div class="response-box" style="color: #1a1a1a; background-color: #f9f9f9;">
        <p style="color: #1a1a1a; margin: 0;">{result['response']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata
    if st.session_state.show_metadata:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Query Type**")
            st.markdown(f"`{result['routing_info']['query_type']}`")
        
        with col2:
            st.markdown("**Data Sources**")
            sources = []
            if result['routing_info']['use_csv']:
                sources.append("CSV")
            if result['routing_info']['use_pdf']:
                sources.append("PDF")
            st.markdown(f"`{', '.join(sources)}`")
        
        with col3:
            st.markdown("**Documents Used**")
            st.markdown(f"`{result['num_documents_used']}`")
        
        if result['entities_extracted']:
            st.markdown("**Extracted Entities**")
            st.json(result['entities_extracted'])
    
    # Retrieved documents
    if st.session_state.show_documents and 'documents_preview' in result:
        st.markdown("### 📄 Retrieved Documents")
        
        for i, doc in enumerate(result['documents_preview'], 1):
            with st.expander(f"Document {i}"):
                st.markdown(doc['text'])
                
                if doc.get('metadata'):
                    st.markdown("**Metadata:**")
                    metadata_html = ""
                    for key, value in doc['metadata'].items():
                        metadata_html += f'<span class="metadata-badge">{key}: {value}</span> '
                    st.markdown(metadata_html, unsafe_allow_html=True)

def main():
    """Main application"""
    # Header
    st.markdown('<div class="main-header">🏥 Insurance Claims Query Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask natural language questions about insurance claims and policies</div>', unsafe_allow_html=True)
    
    # Sidebar
    display_sidebar()
    
    # Main content
    if not st.session_state.initialized:
        st.info("👈 Please initialize the system from the sidebar to begin.")
        
        # Show setup instructions
        with st.expander("📋 Setup Instructions"):
            st.markdown("""
            ### Getting Started
            
            1. **Generate Mock Data**
               ```bash
               python data_generation/generate_mock_data.py
               python data_generation/generate_pdf_documents.py
               ```
            
            2. **Run ETL Pipeline**
               ```bash
               python etl/data_processor.py
               python etl/pdf_processor.py
               ```
            
            3. **Build Vector Stores**
               ```bash
               python rag/vector_store.py
               ```
            
            4. **Set Environment Variables**
               ```bash
               set GROQ_API_KEY=your_api_key_here
               ```
            
            5. **Launch Application**
               ```bash
               streamlit run app.py
               ```
            """)
        
        return
    
    # Query input
    st.markdown("### 💭 Ask a Question")
    
    # Check if there's a current query from example - auto-process it
    if 'current_query' in st.session_state and st.session_state.current_query:
        query_to_process = st.session_state.current_query
        st.session_state.current_query = None
        process_query(query_to_process)
    
    query = st.text_input(
        "Enter your question:",
        placeholder="e.g., Show me denied claims for diabetes patients last quarter",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        if st.button("🔍 Submit Query", type="primary", use_container_width=True) and query:
            process_query(query)
    
    with col2:
        if st.button("🔄 New Query", use_container_width=True):
            st.rerun()
    
    # Chat history
    st.markdown("---")
    display_chat_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        RAG-Powered Claims Query Assistant | Built with Streamlit, FAISS, Sentence Transformers, and Groq
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
