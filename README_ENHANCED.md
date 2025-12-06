# 🏥 RAG-Powered Insurance Claims Query Assistant

**AI-Powered Claims Analysis System with Advanced Retrieval-Augmented Generation**

A sophisticated insurance claims query assistant that combines advanced RAG techniques, semantic search, LLM integration, and interactive analytics dashboards to help payer staff efficiently analyze and query insurance claims data.

---

## 🌟 Key Features

### 1. **Advanced RAG Pipeline**
- **Query Routing**: Intelligent routing between CSV (structured data) and PDF (policy documents)
- **Query Translation**: Extract entities, temporal info, and filters from natural language
- **Query Construction**: Generate multiple query variations with synonym expansion
- **Document Ranking**: Metadata-based reranking for improved relevance
- **Corrective RAG**: Automatic quality control and retrieval correction

### 2. **Three Operational Modes**

#### 💬 Ask Questions Mode
- Natural language query interface
- Context-aware responses with chat history
- Configurable document retrieval (5-20 documents)
- Example queries for quick starts
- Retrieved documents preview
- Query metadata inspection

#### 📊 Analytics Dashboard
- **Key Metrics**: Total claims, approval/denial rates, financial summaries
- **Interactive Visualizations**:
  - Status distribution pie chart
  - Top diseases by claim volume
  - Network status distribution
  - Average claim amounts by status
  - Denial reasons analysis
  - Claims trends over time
  - Top procedures and doctors
- **Export Capabilities**: Download filtered data as CSV

#### 🔍 Advanced Claim Search
- **Search by Claim ID**: Direct lookup with detailed claim cards
- **Multi-Filter Search**: Status, Year, Disease, Network Status
- **Dual View Modes**: Table view or Card view
- **Bulk Export**: Download filtered results with timestamp

### 3. **Data Generation & Processing**
- **Synthetic Data**: 3,000 claims with realistic distributions
- **PDF Documents**: 5 policy and reference documents
- **ETL Pipeline**: Data enrichment and text document creation
- **Vector Indexing**: Separate FAISS indices for CSV and PDF data

### 4. **LLM Integration**
- **Groq API**: Fast inference with Llama 3.3 70B model
- **Conversation Memory**: Multi-turn dialogue support
- **System Prompts**: Optimized for insurance domain
- **Error Handling**: Graceful fallbacks and informative messages

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend (app_enhanced.py)         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │Ask Questions │  │  Analytics   │  │Search Claims │        │
│  │    Mode      │  │  Dashboard   │  │     Mode     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│              Advanced RAG Pipeline (rag/advanced_rag.py)        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Query   │→ │  Query   │→ │  Query   │→ │Document  │      │
│  │ Routing  │  │Translation│  │Constructor│  │ Ranking  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│          Vector Store Manager (rag/vector_store.py)             │
│  ┌─────────────────────┐       ┌─────────────────────┐        │
│  │  CSV Index (FAISS)  │       │  PDF Index (FAISS)  │        │
│  │  3,037 documents    │       │  12 documents       │        │
│  └─────────────────────┘       └─────────────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│           LLM Integration (llm/groq_integration.py)             │
│  ┌─────────────────┐       ┌─────────────────┐                │
│  │  Groq LLM       │       │  Conversation   │                │
│  │  (Llama 3.3)    │       │  Manager        │                │
│  └─────────────────┘       └─────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Conda (recommended) or virtualenv
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the Repository**
```powershell
git clone <repository-url>
cd Abacus
```

2. **Create Conda Environment**
```powershell
conda create -n abacus python=3.10 -y
conda activate abacus
```

3. **Install Dependencies**
```powershell
pip install -r requirements.txt
```

4. **Set Environment Variables**
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

5. **Run Setup (One-Time)**
```powershell
python setup.py
```
This will:
- Generate 3,000 synthetic claims
- Create 5 PDF policy documents
- Process data through ETL pipeline
- Build FAISS vector indices

6. **Launch Application**
```powershell
streamlit run app_enhanced.py
```

7. **Access Application**
Open browser to: http://localhost:8501

---

## 📁 Project Structure

```
Abacus/
├── app_enhanced.py              # Enhanced Streamlit frontend (NEW)
├── app.py                        # Original frontend
├── search_claim.py              # Standalone claim search utility (NEW)
├── setup.py                     # Automated setup script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
│
├── data/                        # Data directory
│   ├── claims.csv               # Generated claims data
│   ├── patients.csv             # Patient information
│   ├── doctors.csv              # Doctor information
│   ├── processed/               # Processed data
│   │   ├── enriched_claims.csv
│   │   ├── documents.json
│   │   └── pdf_documents.json
│   ├── pdf_documents/           # Generated PDFs
│   └── vector_store/            # FAISS indices
│       ├── csv/
│       └── pdf/
│
├── data_generation/             # Data generation modules
│   ├── generate_mock_data.py
│   └── generate_pdf_documents.py
│
├── etl/                         # ETL pipeline
│   ├── data_processor.py
│   └── pdf_processor.py
│
├── rag/                         # RAG components
│   ├── vector_store.py
│   └── advanced_rag.py
│
└── llm/                         # LLM integration
    └── groq_integration.py
```

---

## 💡 Usage Examples

### Ask Questions Mode

**Example Queries:**
```
1. "Show me denied claims for diabetes patients last quarter"
   → Returns: Specific denied diabetes claims with details

2. "List claims denied due to missing documentation"
   → Returns: Claims with denial reason "Missing information"

3. "What are the pre-authorization requirements?"
   → Returns: Policy guidelines from PDF documents

4. "Find high-cost claims over $100,000"
   → Returns: Claims with amount > $100k

5. "Show pending claims for hypertension in 2024"
   → Returns: Filtered pending claims for specific condition
```

### Analytics Dashboard

View comprehensive analytics:
- **Overview Metrics**: Total claims, approval rates, financial totals
- **Visual Analytics**: Interactive charts and graphs
- **Denial Analysis**: Breakdown of denial reasons
- **Temporal Trends**: Claims volume over time
- **Top Categories**: Diseases, procedures, doctors

### Search Claims Mode

**Search Options:**
1. **By Claim ID**: Direct lookup (e.g., CLM0000001)
2. **By Filters**: Combine status, year, disease, network
3. **View Modes**: Table or detailed cards
4. **Export**: Download filtered results

---

## 🔧 Configuration

### Environment Variables (.env)
```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
GROQ_MODEL=llama-3.3-70b-versatile
DATA_DIR=data
VECTOR_STORE_DIR=data/vector_store
```

### Query Settings (In-App)
- **Show Retrieved Documents**: Enable/disable document preview
- **Show Query Metadata**: Display routing and entity extraction
- **Documents to Retrieve**: Set retrieval limit (5-20)

---

## 📊 Data Schema

### Claims Data
```python
{
    'claim_id': str,           # Unique claim identifier
    'patient_id': str,         # Patient identifier
    'patient_name': str,       # Patient full name
    'patient_age': int,        # Patient age
    'patient_gender': str,     # Gender (Male/Female/Other)
    'patient_state': str,      # US state (2-letter code)
    'insurance_plan': str,     # Plan type
    'doctor_id': str,          # Doctor identifier
    'doctor_name': str,        # Doctor full name
    'doctor_specialty': str,   # Medical specialty
    'network_status': str,     # In-Network/Out-of-Network
    'hospital': str,           # Hospital name
    'disease': str,            # Disease/diagnosis
    'procedure': str,          # Procedure performed
    'service_date': date,      # Date of service
    'claim_date': date,        # Claim submission date
    'processed_date': date,    # Processing completion date
    'claim_amount': float,     # Claimed amount ($)
    'approved_amount': float,  # Approved amount ($)
    'claim_status': str,       # Approved/Denied/Pending/Partially Approved
    'denial_reason': str,      # Reason if denied
    'processing_days': int,    # Days to process
    'quarter': str,            # Quarter (Q1-Q4)
    'year': int                # Year
}
```

---

## 🎯 Advanced Features

### 1. Query Routing Logic
```python
Query Type          | Data Source | Priority
--------------------|-------------|----------
SPECIFIC            | CSV         | CSV only
STATISTICAL         | CSV + PDF   | CSV first
POLICY              | PDF         | PDF only
GENERAL             | CSV + PDF   | CSV first
```

### 2. Denial Reason Synonyms
The system automatically expands queries with synonyms:
- "missing documentation" → "Missing information", "Documentation insufficient"
- "not covered" → "Service not covered", "Coverage exclusion"
- "pre-authorization" → "Prior authorization needed", "Authorization missing"

### 3. Entity Extraction
Automatically extracts:
- **Temporal**: Years (2023-2025), Quarters (Q1-Q4)
- **Medical**: Diseases, procedures
- **Status**: Approved, Denied, Pending
- **Financial**: Amount thresholds

### 4. Corrective RAG Actions
- **Filter Low Scores**: Remove poor matches
- **Expand Search**: Retrieve more documents if needed
- **Verify Quality**: Check relevance scores
- **No Correction**: Accept high-quality results

---

## 🔍 Search Capabilities

### Semantic Search
- **Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Index**: FAISS IndexFlatL2 (exact L2 distance)
- **Speed**: ~1ms per query on 3K documents
- **Accuracy**: Similarity-based ranking with metadata filters

### Filter Combinations
```python
Examples:
1. Status + Disease: "denied claims for diabetes"
2. Year + Quarter: "claims in Q3 2024"
3. Network + Amount: "out-of-network claims over $50k"
4. Multiple filters: "pending diabetes claims in-network 2024"
```

---

## 📈 Performance Metrics

### System Performance
- **Embedding Generation**: ~30 seconds for 3K claims
- **Query Processing**: <1 second end-to-end
- **LLM Response**: 1-3 seconds (Groq API)
- **Dashboard Load**: <2 seconds

### Resource Usage
- **Memory**: ~2GB (with embeddings loaded)
- **Storage**: ~500MB (data + indices)
- **CPU**: Low (inference handled by Groq API)

---

## 🛡️ Error Handling

### System Robustness
1. **Missing Dependencies**: Clear error messages with installation instructions
2. **API Failures**: Graceful degradation, informative error messages
3. **Data Issues**: Validation and filling of missing values
4. **Query Errors**: Helpful suggestions for reformulation

### Logging
- Query routing decisions
- Entity extraction results
- Document retrieval counts
- Corrective RAG actions

---

## 🔐 Security Considerations

1. **API Keys**: Stored in `.env` file (not in git)
2. **Data Privacy**: Synthetic data only (no real PHI)
3. **Input Validation**: Query sanitization
4. **Error Messages**: No sensitive data in errors

---

## 🚧 Troubleshooting

### Common Issues

**1. "Vector store not found"**
```powershell
# Solution: Run setup
python setup.py
```

**2. "GROQ_API_KEY not found"**
```powershell
# Solution: Create .env file with API key
echo "GROQ_API_KEY=your_key_here" > .env
```

**3. "sentence_transformers not found"**
```powershell
# Solution: Reinstall with compatible versions
pip install --force-reinstall sentence-transformers==2.2.2
pip install "transformers>=4.6.0,<4.35.0"
pip install "huggingface_hub>=0.4.0,<0.20.0"
```

**4. "Model decommissioned" error**
```powershell
# Solution: Update to latest model (already fixed)
# The system now uses llama-3.3-70b-versatile
```

---

## 📝 Future Enhancements

### Planned Features
- [ ] Multi-user authentication
- [ ] Real-time claim updates
- [ ] Custom report generation
- [ ] Email notifications for claim status changes
- [ ] Integration with external EHR systems
- [ ] Advanced ML predictions (claim approval probability)
- [ ] Audit trail and compliance tracking
- [ ] Mobile-responsive design

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Consult the documentation files (WORKFLOW.md, QUICKSTART.md)

---

## 🙏 Acknowledgments

- **Groq**: For fast LLM inference
- **Sentence Transformers**: For semantic embeddings
- **FAISS**: For efficient vector search
- **Streamlit**: For interactive UI framework
- **Plotly**: For interactive visualizations

---

**Built with ❤️ for Healthcare Technology**
