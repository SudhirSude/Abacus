"""
LLM Integration using Groq API
Handles answer generation with chat history context
"""

import os
from typing import List, Dict, Optional
from groq import Groq
import json

class GroqLLM:
    """Groq LLM client for answer generation"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq client
        
        Args:
            api_key: Groq API key (or set GROQ_API_KEY env variable)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key not provided. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = model
        
        # Available models (updated as of Dec 2025)
        self.available_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it"
        ]
    
    def generate_response(
        self,
        query: str,
        context_documents: List[str],
        chat_history: Optional[List[Dict]] = None,
        max_tokens: int = 1024,
        temperature: float = 0.3
    ) -> str:
        """
        Generate response using Groq LLM
        
        Args:
            query: User query
            context_documents: Retrieved documents for context
            chat_history: Previous chat messages
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated response text
        """
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Build context
        context = self._build_context(context_documents)
        
        # Build user prompt
        user_prompt = self._build_user_prompt(query, context)
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            for msg in chat_history[-6:]:  # Keep last 6 messages (3 exchanges)
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current query
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the assistant"""
        return """You are an expert insurance claims assistant helping payer staff analyze and query insurance claims data.

Your responsibilities:
1. Answer questions about insurance claims accurately using the provided context
2. Provide specific data when asked (claim IDs, amounts, dates, patient names, denial reasons, etc.)
3. Extract and present detailed claim information from the context documents
4. Explain denial reasons and approval patterns
5. Reference policy guidelines when relevant
6. Be concise but comprehensive in your responses
7. If the context doesn't contain enough information, acknowledge this clearly

Guidelines:
- Always base your answers on the provided context documents
- When asked to "list" or "show" claims, extract ALL relevant claims from the context with their details
- For each claim, include: Claim ID, Patient Name, Disease/Condition, Claim Amount, Status, and Denial Reason (if denied)
- Format monetary values with currency symbols (e.g., $12,345.67)
- Use bullet points or numbered lists for multiple items
- If asked about specific denial reasons, search the context for matching "denial_reason" fields
- When discussing denials, always mention the specific denial reason from the data
- If context contains claim-level data (CSV), prioritize showing specific claims over just summary statistics
- Be professional and helpful in tone

Remember: You are assisting insurance payer staff, so use appropriate medical and insurance terminology. When claim details are available in the context, always provide them rather than just saying data is not available."""
    
    def _build_context(self, documents: List[str]) -> str:
        """Build context from retrieved documents"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(documents[:10], 1):  # Limit to top 10 documents
            context_parts.append(f"Document {i}:\n{doc}\n")
        
        return "\n".join(context_parts)
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """Build user prompt with query and context"""
        return f"""Based on the following context documents, please answer the user's question.

Context Documents:
{context}

User Question: {query}

Please provide a clear, accurate, and helpful answer based on the context provided. If you need to reference specific claims or data, include the relevant details."""
    
    def generate_summary(
        self,
        documents: List[str],
        summary_type: str = "general"
    ) -> str:
        """
        Generate summary of documents
        
        Args:
            documents: List of document texts
            summary_type: Type of summary (general, statistical, etc.)
            
        Returns:
            Summary text
        """
        if not documents:
            return "No documents to summarize."
        
        context = self._build_context(documents)
        
        if summary_type == "statistical":
            prompt = f"""Please provide a statistical summary of the following insurance claims data:

{context}

Include:
- Total number of claims
- Approval/denial rates
- Common denial reasons
- Amount ranges
- Any notable patterns or trends"""
        else:
            prompt = f"""Please provide a concise summary of the following insurance claims information:

{context}

Focus on the key points and important details."""
        
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=512,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating summary: {str(e)}"


class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, max_history: int = 20):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
        self.history: List[Dict] = []
        self.session_metadata = {}
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add message to conversation history
        
        Args:
            role: Message role (user/assistant)
            content: Message content
            metadata: Optional metadata (documents used, query type, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": None  # Could add timestamp if needed
        }
        
        if metadata:
            message["metadata"] = metadata
        
        self.history.append(message)
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_history(self, include_metadata: bool = False) -> List[Dict]:
        """Get conversation history"""
        if include_metadata:
            return self.history
        else:
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in self.history
            ]
    
    def get_context_summary(self) -> str:
        """Get summary of conversation context"""
        if not self.history:
            return "No conversation history."
        
        summary_parts = []
        for msg in self.history[-6:]:  # Last 3 exchanges
            role = "User" if msg["role"] == "user" else "Assistant"
            content_preview = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_parts.append(f"{role}: {content_preview}")
        
        return "\n".join(summary_parts)
    
    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        self.session_metadata = {}
    
    def save_history(self, filepath: str):
        """Save conversation history to file"""
        with open(filepath, 'w') as f:
            json.dump({
                'history': self.history,
                'metadata': self.session_metadata
            }, f, indent=2)
    
    def load_history(self, filepath: str):
        """Load conversation history from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.history = data.get('history', [])
            self.session_metadata = data.get('metadata', {})


class RAGResponseGenerator:
    """Combines RAG pipeline with LLM for complete response generation"""
    
    def __init__(self, rag_pipeline, groq_llm: GroqLLM):
        """
        Initialize response generator
        
        Args:
            rag_pipeline: AdvancedRAGPipeline instance
            groq_llm: GroqLLM instance
        """
        self.rag_pipeline = rag_pipeline
        self.llm = groq_llm
        self.conversation = ConversationManager()
    
    def generate_response(
        self,
        query: str,
        top_k: int = 10,
        use_history: bool = True
    ) -> Dict:
        """
        Generate complete response for query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            use_history: Whether to use conversation history
            
        Returns:
            Dict with response and metadata
        """
        # Process query through RAG pipeline
        rag_results = self.rag_pipeline.process_query(query, top_k=top_k)
        
        # Prepare context documents
        context_docs = []
        
        # Prioritize based on routing
        priority = rag_results['routing']['priority']
        other = 'pdf' if priority == 'csv' else 'csv'
        query_type = rag_results['routing']['query_type']
        
        # For specific queries, use MORE CSV documents and skip PDF
        if query_type == 'specific':
            # Get up to 15 documents from CSV for specific queries
            for text, metadata, score in rag_results['documents'].get('csv', [])[:15]:
                context_docs.append(text)
        else:
            # Get documents from priority source
            for text, metadata, score in rag_results['documents'].get(priority, [])[:7]:
                context_docs.append(text)
            
            # Add some from other source if available
            for text, metadata, score in rag_results['documents'].get(other, [])[:3]:
                context_docs.append(text)
        
        # Get chat history if needed
        chat_history = self.conversation.get_history() if use_history else None
        
        # Generate response
        response = self.llm.generate_response(
            query=query,
            context_documents=context_docs,
            chat_history=chat_history
        )
        
        # Update conversation history
        self.conversation.add_message("user", query, {
            'query_type': rag_results['routing']['query_type'],
            'num_documents': len(context_docs)
        })
        self.conversation.add_message("assistant", response)
        
        # Prepare result
        result = {
            'query': query,
            'response': response,
            'routing_info': rag_results['routing'],
            'entities_extracted': rag_results['translation']['entities'],
            'num_documents_used': len(context_docs),
            'documents_preview': [
                {
                    'text': doc[:200] + "..." if len(doc) > 200 else doc,
                    'metadata': rag_results['documents'][priority][i][1] if i < len(rag_results['documents'][priority]) else {}
                }
                for i, doc in enumerate(context_docs[:3])
            ]
        }
        
        return result
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation.get_history()
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation.clear_history()


if __name__ == "__main__":
    # Test LLM (requires GROQ_API_KEY environment variable)
    print("Testing Groq LLM Integration")
    print("="*60)
    
    try:
        llm = GroqLLM()
        print(f"✓ Successfully initialized Groq LLM with model: {llm.model}")
        
        # Test simple generation
        test_context = [
            """Claim ID: CLM0001234
Patient: John Doe, 45 years old
Disease: Diabetes Type 2
Claim Status: Denied
Denial Reason: Pre-authorization required
Claim Amount: $5,000"""
        ]
        
        test_query = "Why was claim CLM0001234 denied?"
        
        print(f"\nTest Query: {test_query}")
        print("\nGenerating response...")
        
        response = llm.generate_response(
            query=test_query,
            context_documents=test_context,
            chat_history=None
        )
        
        print(f"\nResponse:\n{response}")
        print("\n" + "="*60)
        print("✓ LLM integration test successful!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure to set GROQ_API_KEY environment variable")
