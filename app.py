"""
Enhanced Streamlit Frontend for RAG-Powered Claims Query Assistant
Integrates advanced RAG with analytics dashboard and claim search features
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import re
from datetime import datetime

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag.vector_store import MultiIndexManager
from rag.advanced_rag import AdvancedRAGPipeline
from llm.groq_integration import GroqLLM, RAGResponseGenerator

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
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
        text-align: center;
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
    .claim-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f4788;
    }
    .stAlert {
        margin-top: 1rem;
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
    st.session_state.show_documents = True
    st.session_state.show_metadata = False
    st.session_state.top_k = 10

def initialize_system():
    """Initialize the RAG system"""
    try:
        with st.spinner("🔄 Initializing system... This may take a moment."):
            # Check if vector stores exist
            csv_index_path = "data/vector_store/csv/faiss_index.bin"
            pdf_index_path = "data/vector_store/pdf/faiss_index.bin"
            
            if not os.path.exists(csv_index_path):
                st.error("❌ Vector store not found. Please run setup first.")
                st.info("Run: `python setup.py`")
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
                st.warning("⚠️ GROQ_API_KEY not found. Some features may be limited.")
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

@st.cache_data
def load_claims_data():
    """Load claims data for analytics"""
    try:
        claims_df = pd.read_csv("data/processed/enriched_claims.csv")
        return claims_df
    except Exception as e:
        st.error(f"Error loading claims data: {e}")
        return None

def display_claim_card(row):
    """Display a single claim as a card"""
    status_emoji = {
        "Approved": "✅",
        "Denied": "❌",
        "Pending": "⏳",
        "Partially Approved": "⚠️"
    }
    
    emoji = status_emoji.get(row['claim_status'], "📄")
    
    st.markdown(f"""
    <div class="claim-card" style="background-color: #f8f9fa; color: #1a1a1a;">
        <h4 style="color: #1f4788;">{emoji} Claim {row['claim_id']}</h4>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem; color: #1a1a1a;">
            <div style="color: #1a1a1a;">
                <strong style="color: #1f4788;">👤 Patient Information</strong><br>
                <span style="color: #1a1a1a;">Name: {row['patient_name']}<br>
                Age: {row['patient_age']} | Gender: {row['patient_gender']}<br>
                State: {row['patient_state']}<br>
                Plan: {row['insurance_plan']}</span>
            </div>
            <div style="color: #1a1a1a;">
                <strong style="color: #1f4788;">🏥 Medical Details</strong><br>
                <span style="color: #1a1a1a;">Disease: {row['disease']}<br>
                Procedure: {row['procedure']}<br>
                Hospital: {row['hospital']}<br>
                Network: {row['network_status']}</span>
            </div>
            <div style="color: #1a1a1a;">
                <strong style="color: #1f4788;">💰 Financial & Status</strong><br>
                <span style="color: #1a1a1a;">Status: <strong>{row['claim_status']}</strong><br>
                {"Denial Reason: " + row['denial_reason'] + "<br>" if row['claim_status'] == 'Denied' else ""}
                Claimed: ${row['claim_amount']:,.2f}<br>
                Approved: ${row['approved_amount']:,.2f}<br>
                Service Date: {row['service_date']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_analytics_dashboard():
    """Display comprehensive analytics dashboard"""
    st.markdown("## 📊 Claims Analytics Dashboard")
    
    df = load_claims_data()
    if df is None:
        st.error("Unable to load claims data for analytics")
        return
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_claims = len(df)
    approved_claims = len(df[df['claim_status'] == 'Approved'])
    denied_claims = len(df[df['claim_status'] == 'Denied'])
    pending_claims = len(df[df['claim_status'] == 'Pending'])
    
    approval_rate = (approved_claims / total_claims * 100) if total_claims > 0 else 0
    denial_rate = (denied_claims / total_claims * 100) if total_claims > 0 else 0
    
    with col1:
        st.metric("Total Claims", f"{total_claims:,}")
    
    with col2:
        st.metric("Approved", f"{approved_claims:,}", f"{approval_rate:.1f}%")
    
    with col3:
        st.metric("Denied", f"{denied_claims:,}", f"{denial_rate:.1f}%", delta_color="inverse")
    
    with col4:
        total_claimed = df['claim_amount'].sum()
        st.metric("Total Claimed", f"${total_claimed/1e6:.2f}M")
    
    with col5:
        total_approved = df['approved_amount'].sum()
        approval_amount_rate = (total_approved / total_claimed * 100) if total_claimed > 0 else 0
        st.metric("Total Approved", f"${total_approved/1e6:.2f}M", f"{approval_amount_rate:.1f}%")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Status Distribution Pie Chart
        status_counts = df['claim_status'].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Claims Distribution by Status",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 Diseases
        top_diseases = df['disease'].value_counts().head(10)
        fig = px.bar(
            x=top_diseases.values,
            y=top_diseases.index,
            orientation='h',
            title="Top 10 Diseases by Claim Volume",
            labels={'x': 'Number of Claims', 'y': 'Disease'},
            color=top_diseases.values,
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Network Status Distribution
        network_counts = df['network_status'].value_counts()
        fig = px.bar(
            x=network_counts.index,
            y=network_counts.values,
            title="Network Status Distribution",
            labels={'x': 'Network Status', 'y': 'Number of Claims'},
            color=network_counts.values,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average Claim Amount by Status
        avg_by_status = df.groupby('claim_status')['claim_amount'].mean().sort_values(ascending=False)
        fig = px.bar(
            x=avg_by_status.index,
            y=avg_by_status.values,
            title="Average Claim Amount by Status",
            labels={'x': 'Claim Status', 'y': 'Average Amount ($)'},
            color=avg_by_status.values,
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Denial Reasons Analysis
    st.markdown("### ❌ Denial Reasons Analysis")
    denied_df = df[df['claim_status'] == 'Denied']
    if len(denied_df) > 0:
        denial_reasons = denied_df['denial_reason'].value_counts()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                x=denial_reasons.values,
                y=denial_reasons.index,
                orientation='h',
                title="Distribution of Denial Reasons",
                labels={'x': 'Count', 'y': 'Denial Reason'},
                color=denial_reasons.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**Denial Statistics**")
            for reason, count in denial_reasons.items():
                percentage = (count / len(denied_df) * 100)
                st.markdown(f"• **{reason}**: {count} ({percentage:.1f}%)")
    else:
        st.info("No denied claims found.")
    
    # Quarterly Trends
    st.markdown("### 📈 Claims Trends Over Time")
    if 'service_date' in df.columns:
        df_copy = df.copy()
        df_copy['service_date'] = pd.to_datetime(df_copy['service_date'])
        df_copy = df_copy.sort_values('service_date')
        df_copy['year_month'] = df_copy['service_date'].dt.to_period('M').astype(str)
        
        monthly_data = df_copy.groupby(['year_month', 'claim_status']).size().reset_index(name='count')
        
        fig = px.line(
            monthly_data,
            x='year_month',
            y='count',
            color='claim_status',
            title="Claims Volume Over Time by Status",
            labels={'year_month': 'Month', 'count': 'Number of Claims', 'claim_status': 'Status'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Procedures and Doctors
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔬 Top 10 Procedures")
        top_procedures = df['procedure'].value_counts().head(10)
        for i, (procedure, count) in enumerate(top_procedures.items(), 1):
            st.markdown(f"{i}. **{procedure}**: {count} claims")
    
    with col2:
        st.markdown("### 👨‍⚕️ Top 10 Doctors by Claim Volume")
        top_doctors = df['doctor_name'].value_counts().head(10)
        for i, (doctor, count) in enumerate(top_doctors.items(), 1):
            st.markdown(f"{i}. **{doctor}**: {count} claims")

def show_claim_search():
    """Advanced claim search interface"""
    st.markdown("## 🔍 Advanced Claim Search")
    
    df = load_claims_data()
    if df is None:
        st.error("Unable to load claims data")
        return
    
    # Search by Claim ID
    st.markdown("### Search by Claim ID")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        claim_id = st.text_input("Enter Claim ID", placeholder="e.g., CLM0000001")
    
    with col2:
        search_btn = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_btn and claim_id:
        matches = df[df['claim_id'].str.upper() == claim_id.upper()]
        if not matches.empty:
            row = matches.iloc[0]
            st.success(f"✅ Found claim {claim_id}")
            display_claim_card(row)
        else:
            st.error(f"❌ Claim ID '{claim_id}' not found")
    
    st.markdown("---")
    
    # Advanced Filters
    st.markdown("### Filter Claims")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=sorted(df['claim_status'].unique()),
            default=None
        )
    
    with col2:
        year_filter = st.multiselect(
            "Year",
            options=sorted(df['year'].unique(), reverse=True),
            default=None
        )
    
    with col3:
        disease_filter = st.multiselect(
            "Disease",
            options=sorted(df['disease'].unique()),
            default=None
        )
    
    with col4:
        network_filter = st.multiselect(
            "Network Status",
            options=sorted(df['network_status'].unique()),
            default=None
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter:
        filtered_df = filtered_df[filtered_df['claim_status'].isin(status_filter)]
    if year_filter:
        filtered_df = filtered_df[filtered_df['year'].isin(year_filter)]
    if disease_filter:
        filtered_df = filtered_df[filtered_df['disease'].isin(disease_filter)]
    if network_filter:
        filtered_df = filtered_df[filtered_df['network_status'].isin(network_filter)]
    
    st.markdown(f"**Showing {len(filtered_df):,} of {len(df):,} claims**")
    
    # Display options
    view_mode = st.radio("View Mode:", ["Table", "Cards"], horizontal=True)
    
    if view_mode == "Table":
        # Display as table
        display_cols = [
            'claim_id', 'patient_name', 'disease', 'procedure',
            'claim_status', 'claim_amount', 'approved_amount',
            'service_date', 'network_status', 'quarter', 'year'
        ]
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            height=600
        )
    else:
        # Display as cards
        num_to_show = st.slider("Number of claims to display:", 1, 50, 10)
        for idx, row in filtered_df.head(num_to_show).iterrows():
            display_claim_card(row)
    
    # Export option
    st.markdown("---")
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"filtered_claims_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def display_sidebar():
    """Enhanced sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown("## 🏥 Claims Assistant")
        
        # Navigation
        st.markdown("### 🧭 Navigation")
        mode = st.radio(
            "Select Mode:",
            ["💬 Ask Questions", "📊 Analytics Dashboard", "🔍 Search Claims"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # System Status
        st.markdown("### 📡 System Status")
        if st.session_state.initialized:
            st.success("✅ System Ready")
        else:
            if st.button("🔄 Initialize System", use_container_width=True):
                if initialize_system():
                    st.success("✅ System initialized successfully!")
                    st.rerun()
        
        st.markdown("---")
        
        # Example Queries (only in Ask Questions mode)
        if mode == "💬 Ask Questions":
            st.markdown("### 💡 Example Queries")
            examples = [
                "Tell me all details for CLM0001190",
                "Show me all information for Charles Johnson",
                "Give me details for patient Elizabeth Nguyen",
                "Show me denied claims for diabetes",
                "List high-cost claims over $100,000",
                "What are pre-authorization requirements?",
                "Find claims denied for missing documentation",
                "Show pending claims this quarter",
                "List out-of-network claims",
                "Tell me about claim CLM0000005",
                "Find claims for Robert Torres"
            ]
            
            for example in examples:
                if st.button(f"📝 {example[:35]}...", key=f"ex_{example}", use_container_width=True):
                    st.session_state.current_query = example
                    st.rerun()
            
            st.markdown("---")
            
            # Settings
            st.markdown("### ⚙️ Query Settings")
            st.session_state.show_documents = st.checkbox("Show Retrieved Documents", value=True)
            st.session_state.show_metadata = st.checkbox("Show Query Metadata", value=False)
            st.session_state.top_k = st.slider("Documents to Retrieve", 5, 20, 10)
            
            st.markdown("---")
            
            # Clear History
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                if st.session_state.response_generator:
                    st.session_state.response_generator.clear_conversation()
                st.success("Chat history cleared!")
                st.rerun()
        
        return mode

def process_query(query: str):
    """Process user query"""
    if not st.session_state.initialized or not st.session_state.response_generator:
        st.error("System not initialized. Please initialize from sidebar.")
        return
    
    try:
        # Check for exact claim ID in query
        claim_id_match = re.search(r'\b(CLM\d+)\b', query, re.IGNORECASE)
        
        if claim_id_match:
            # Extract claim ID
            claim_id = claim_id_match.group(1).upper()
            
            # Try to find exact claim from CSV
            try:
                claims_file = 'data/processed/enriched_claims.csv'
                if os.path.exists(claims_file):
                    df = pd.read_csv(claims_file)
                    claim_match = df[df['claim_id'].str.upper() == claim_id]
                    
                    if not claim_match.empty:
                        # Found exact match - create detailed response
                        claim = claim_match.iloc[0]
                        
                        response_text = f"""**Claim ID: {claim['claim_id']}**

**Patient Information:**
- Name: {claim['patient_name']}
- Age: {claim['patient_age']} years
- Gender: {claim['patient_gender']}
- State: {claim['patient_state']}
- Insurance Plan: {claim['insurance_plan']}

**Medical Details:**
- Disease/Condition: {claim['disease']}
- Procedure: {claim['procedure']}
- Doctor: {claim['doctor_name']} ({claim['doctor_specialty']})
- Hospital: {claim['hospital']}
- Network Status: {claim['network_status']}

**Claim Details:**
- Service Date: {claim['service_date']}
- Claim Date: {claim['claim_date']}
- Processed Date: {claim['processed_date']}
- Processing Time: {claim['processing_days']} days

**Financial Information:**
- Claim Amount: ${claim['claim_amount']:,.2f}
- Approved Amount: ${claim['approved_amount']:,.2f}
- Status: **{claim['claim_status']}**
- Denial Reason: {claim['denial_reason'] if claim['denial_reason'] != 'N/A' else 'Not applicable'}

**Period:** {claim['quarter']} {claim['year']}"""
                        
                        # Create result structure
                        result = {
                            'response': response_text,
                            'routing_info': {
                                'query_type': 'specific',
                                'use_csv': True,
                                'use_pdf': False
                            },
                            'entities_extracted': {'claim_id': claim_id},
                            'num_documents_used': 1,
                            'documents_preview': [{
                                'text': f"Exact match for {claim_id}",
                                'metadata': claim.to_dict()
                            }]
                        }
                        
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
                        return
            except Exception as e:
                print(f"Error looking up claim ID: {e}")
                # Fall through to normal processing
        
        with st.spinner("🔍 Searching and generating response..."):
            # Generate response using RAG
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
    """Display query response with metadata"""
    st.markdown("### 🤖 Assistant Response")
    
    # Response box
    st.markdown(f"""
    <div class="response-box" style="color: #1a1a1a; background-color: #f9f9f9;">
        <p style="color: #1a1a1a; margin: 0;">{result['response']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metadata
    if st.session_state.show_metadata:
        with st.expander("📊 Query Metadata"):
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
    
    # Retrieved Documents
    if st.session_state.show_documents and 'documents_preview' in result:
        with st.expander(f"📄 Retrieved Documents ({len(result['documents_preview'])} shown)"):
            for i, doc in enumerate(result['documents_preview'], 1):
                st.markdown(f"**Document {i}**")
                st.markdown(f"```\n{doc['text']}\n```")
                if doc.get('metadata'):
                    st.json(doc['metadata'])
                st.markdown("---")

def show_ask_questions_mode():
    """Ask Questions mode interface"""
    st.markdown("## 💬 Ask Questions About Insurance Claims")
    
    # Auto-process current query if set
    if 'current_query' in st.session_state and st.session_state.current_query:
        query_to_process = st.session_state.current_query
        st.session_state.current_query = None
        process_query(query_to_process)
    
    # Query input
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
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 💬 Recent Conversations")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
            with st.expander(f"Query {len(st.session_state.chat_history) - i + 1}: {chat['query'][:60]}..."):
                st.markdown(f"**Question:** {chat['query']}")
                st.markdown(f"**Answer:** {chat['response']}")
                
                if st.session_state.show_metadata and 'metadata' in chat:
                    st.markdown("**Metadata:**")
                    st.json(chat['metadata'])

def main():
    """Main application"""
    # Header
    st.markdown('<h1 class="main-header">🏥 Insurance Claims Query Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Claims Analysis with Advanced RAG</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    mode = display_sidebar()
    
    # Main content based on mode
    if mode == "💬 Ask Questions":
        if not st.session_state.initialized:
            st.info("👋 Welcome! Please initialize the system from the sidebar to get started.")
        else:
            show_ask_questions_mode()
    
    elif mode == "📊 Analytics Dashboard":
        show_analytics_dashboard()
    
    elif mode == "🔍 Search Claims":
        show_claim_search()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.9rem;">
        RAG-Powered Claims Query Assistant | Built with Streamlit, FAISS, Sentence Transformers, and Groq LLM
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
