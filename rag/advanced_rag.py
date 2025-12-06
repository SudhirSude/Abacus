"""
Advanced RAG Components
Implements query construction, translation, ranking, corrective RAG, and routing
"""

import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import pandas as pd
from enum import Enum

class QueryType(Enum):
    """Types of queries for routing"""
    STATISTICAL = "statistical"  # Aggregate queries, summaries
    SPECIFIC = "specific"  # Specific claim lookups
    POLICY = "policy"  # Policy and guideline questions
    GENERAL = "general"  # General questions


class QueryRouter:
    """Routes queries to appropriate data sources (CSV vs PDF)"""
    
    def __init__(self):
        # Keywords for different query types
        self.statistical_keywords = [
            'total', 'count', 'average', 'sum', 'how many', 'statistics',
            'summary', 'aggregate', 'distribution', 'percentage', 'rate'
        ]
        
        self.specific_keywords = [
            'claim id', 'patient id', 'show me claims', 'list claims',
            'specific claim', 'denied claims', 'approved claims', 'find claims',
            'claim details', 'claim information', 'specific', 'individual claims',
            'which claims', 'what claims', 'claims for', 'claims with',
            'denial reason', 'missing documentation', 'missing information',
            'claim amount', 'claim date', 'patient name', 'doctor name'
        ]
        
        self.policy_keywords = [
            'policy', 'guideline', 'coverage', 'procedure code', 'pre-authorization',
            'what is covered', 'how to', 'process', 'requirement',
            'medical necessity', 'exclusion', 'appeal', 'pre-auth',
            'authorization requirement', 'covered service', 'benefits'
        ]
    
    def determine_query_type(self, query: str) -> QueryType:
        """Determine the type of query"""
        query_lower = query.lower()
        
        # Check for exact claim ID - HIGHEST PRIORITY
        claim_id_match = re.search(r'\b(CLM\d+)\b', query, re.IGNORECASE)
        if claim_id_match:
            return QueryType.SPECIFIC
        
        # Check for specific claims query FIRST (higher priority)
        # This includes queries asking for lists, details, or specific information
        specific_score = sum(1 for keyword in self.specific_keywords if keyword in query_lower)
        
        # Check for statistical query
        statistical_score = sum(1 for keyword in self.statistical_keywords if keyword in query_lower)
        
        # Check for policy query
        policy_score = sum(1 for keyword in self.policy_keywords if keyword in query_lower)
        
        # If asking for specific claims/details, prioritize that even if other keywords present
        if specific_score > 0:
            # Exception: if ONLY asking about policy documentation requirements
            if policy_score > specific_score and not any(word in query_lower for word in ['list', 'show', 'claims', 'denied', 'approved']):
                return QueryType.POLICY
            return QueryType.SPECIFIC
        
        # Check for statistical query
        if statistical_score > 0:
            return QueryType.STATISTICAL
        
        # Check for policy query
        if policy_score > 0:
            return QueryType.POLICY
        
        return QueryType.GENERAL
    
    def route_query(self, query: str) -> Dict[str, any]:
        """
        Route query to appropriate data sources
        
        Returns:
            Dict with routing information
        """
        query_type = self.determine_query_type(query)
        
        routing = {
            'query_type': query_type.value,
            'use_csv': False,
            'use_pdf': False,
            'priority': 'csv'  # Default priority
        }
        
        if query_type == QueryType.STATISTICAL:
            # Statistical queries may benefit from both CSV data and PDF summaries
            routing['use_csv'] = True
            routing['use_pdf'] = True
            routing['priority'] = 'csv'
        elif query_type == QueryType.SPECIFIC:
            # Specific queries need detailed CSV data
            routing['use_csv'] = True
            routing['priority'] = 'csv'
            # Only add PDF if asking about documentation requirements context
            if 'documentation' in query.lower() or 'requirement' in query.lower():
                routing['use_pdf'] = True
        elif query_type == QueryType.POLICY:
            routing['use_pdf'] = True
            routing['priority'] = 'pdf'
        else:  # GENERAL
            routing['use_csv'] = True
            routing['use_pdf'] = True
            routing['priority'] = 'csv'
        
        return routing


class QueryTranslator:
    """Translates natural language queries into structured formats"""
    
    def __init__(self):
        self.diseases = [
            'diabetes', 'hypertension', 'cancer', 'heart disease', 'asthma',
            'copd', 'arthritis', 'depression', 'anxiety', 'stroke'
        ]
        
        self.statuses = ['approved', 'denied', 'pending', 'partially approved']
        
        self.quarters = ['q1', 'q2', 'q3', 'q4']
        
    def extract_temporal_info(self, query: str) -> Optional[Dict]:
        """Extract temporal information from query"""
        query_lower = query.lower()
        temporal_info = {}
        
        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', query)
        if year_match:
            temporal_info['year'] = int(year_match.group(1))
        
        # Extract quarter
        quarter_match = re.search(r'\b(q[1-4]|quarter [1-4]|Q[1-4])\b', query, re.IGNORECASE)
        if quarter_match:
            q = quarter_match.group(1).upper()
            if 'Q' in q:
                temporal_info['quarter'] = q if q.startswith('Q') else f"Q{q[-1]}"
            else:
                temporal_info['quarter'] = f"Q{q[-1]}"
        
        # Extract relative time
        if 'last quarter' in query_lower:
            current_date = datetime.now()
            current_quarter = (current_date.month - 1) // 3 + 1
            last_quarter = current_quarter - 1 if current_quarter > 1 else 4
            last_quarter_year = current_date.year if current_quarter > 1 else current_date.year - 1
            temporal_info['quarter'] = f"Q{last_quarter}"
            temporal_info['year'] = last_quarter_year
        
        if 'this quarter' in query_lower:
            current_date = datetime.now()
            current_quarter = (current_date.month - 1) // 3 + 1
            temporal_info['quarter'] = f"Q{current_quarter}"
            temporal_info['year'] = current_date.year
        
        if 'last year' in query_lower:
            temporal_info['year'] = datetime.now().year - 1
        
        if 'this year' in query_lower:
            temporal_info['year'] = datetime.now().year
        
        return temporal_info if temporal_info else None
    
    def extract_disease_info(self, query: str) -> Optional[str]:
        """Extract disease/condition from query"""
        query_lower = query.lower()
        
        for disease in self.diseases:
            if disease in query_lower:
                return disease
        
        return None
    
    def extract_status_info(self, query: str) -> Optional[str]:
        """Extract claim status from query"""
        query_lower = query.lower()
        
        for status in self.statuses:
            if status in query_lower:
                return status.title()
        
        return None
    
    def extract_claim_id(self, query: str) -> Optional[str]:
        """Extract claim ID from query (e.g., CLM0000001, CLM0000002)"""
        # Match patterns like CLM followed by digits
        claim_id_match = re.search(r'\b(CLM\d+)\b', query, re.IGNORECASE)
        if claim_id_match:
            return claim_id_match.group(1).upper()
        return None
    
    def translate(self, query: str) -> Dict:
        """
        Translate natural language query into structured format
        
        Returns:
            Dict with extracted entities and filters
        """
        translation = {
            'original_query': query,
            'filters': {},
            'entities': {}
        }
        
        # Extract temporal information
        temporal = self.extract_temporal_info(query)
        if temporal:
            translation['entities']['temporal'] = temporal
            translation['filters'].update(temporal)
        
        # Extract disease
        disease = self.extract_disease_info(query)
        if disease:
            translation['entities']['disease'] = disease
            translation['filters']['disease'] = disease
        
        # Extract status
        status = self.extract_status_info(query)
        if status:
            translation['entities']['status'] = status
            translation['filters']['claim_status'] = status
        
        # Extract claim ID
        claim_id = self.extract_claim_id(query)
        if claim_id:
            translation['entities']['claim_id'] = claim_id
            translation['filters']['claim_id'] = claim_id
        
        return translation


class QueryConstructor:
    """Constructs optimized queries for retrieval"""
    
    def __init__(self):
        # Denial reason synonyms for better matching
        self.denial_synonyms = {
            'missing documentation': ['Missing information', 'Documentation insufficient', 'Incomplete documentation'],
            'missing information': ['Missing documentation', 'Documentation insufficient', 'Incomplete information'],
            'not covered': ['Service not covered', 'Not a covered service', 'Coverage exclusion'],
            'pre-authorization': ['Pre-authorization required', 'Prior authorization needed', 'Authorization missing'],
            'pre-existing': ['Pre-existing condition', 'Pre-existing condition exclusion'],
            'experimental': ['Experimental treatment', 'Investigational treatment'],
            'out of network': ['Out-of-network provider', 'Non-network provider'],
            'not medically necessary': ['Not medically necessary', 'Medical necessity not established'],
        }
    
    def construct_queries(self, original_query: str, translation: Dict) -> List[str]:
        """
        Generate multiple query variations for better retrieval
        
        Args:
            original_query: Original user query
            translation: Translated query with entities
            
        Returns:
            List of query variations
        """
        queries = [original_query]
        query_lower = original_query.lower()
        
        # Add denial reason synonym variations
        for key, synonyms in self.denial_synonyms.items():
            if key in query_lower:
                for synonym in synonyms:
                    synonym_query = original_query.replace(key, synonym)
                    if synonym_query not in queries:
                        queries.append(synonym_query)
                    # Also add just the denial reason phrase
                    denial_query = f"denied claims {synonym}"
                    if denial_query not in queries:
                        queries.append(denial_query)
        
        # Add query with explicit entities
        if translation['entities']:
            entity_query = original_query
            
            if 'disease' in translation['entities']:
                entity_query = f"{translation['entities']['disease']} {entity_query}"
            
            if 'temporal' in translation['entities']:
                temporal = translation['entities']['temporal']
                if 'quarter' in temporal and 'year' in temporal:
                    entity_query = f"{entity_query} {temporal['quarter']} {temporal['year']}"
                elif 'year' in temporal:
                    entity_query = f"{entity_query} {temporal['year']}"
            
            if entity_query != original_query:
                queries.append(entity_query)
        
        # Add query focused on action
        if 'show' in query_lower or 'find' in query_lower or 'list' in query_lower:
            action_query = re.sub(r'\b(show me|list|find|get|retrieve)\b', '', original_query, flags=re.IGNORECASE).strip()
            if action_query and action_query not in queries:
                queries.append(action_query)
        
        # Add query without question words
        no_question_query = re.sub(
            r'\b(what|when|where|who|why|how|which|show|tell|find|list)\b',
            '',
            original_query,
            flags=re.IGNORECASE
        ).strip()
        if no_question_query and no_question_query not in queries:
            queries.append(no_question_query)
        
        return queries


class DocumentRanker:
    """Ranks and reranks retrieved documents"""
    
    def __init__(self):
        pass
    
    def rank_by_relevance(
        self,
        documents: List[Tuple[str, Dict, float]],
        query_translation: Dict
    ) -> List[Tuple[str, Dict, float]]:
        """
        Rerank documents based on metadata matching
        
        Args:
            documents: List of (text, metadata, score) tuples
            query_translation: Translated query with filters
            
        Returns:
            Reranked documents
        """
        filters = query_translation.get('filters', {})
        
        if not filters:
            return documents
        
        scored_docs = []
        
        for text, metadata, original_score in documents:
            boost_score = 0
            
            # Boost based on metadata matches
            for key, value in filters.items():
                if key in metadata:
                    meta_value = metadata[key]
                    
                    # Handle different types of matching
                    if isinstance(meta_value, str) and isinstance(value, str):
                        if value.lower() in meta_value.lower():
                            boost_score += 0.2
                    elif meta_value == value:
                        boost_score += 0.3
            
            # Calculate final score
            final_score = original_score * (1 + boost_score)
            scored_docs.append((text, metadata, final_score))
        
        # Sort by final score
        scored_docs.sort(key=lambda x: x[2], reverse=True)
        
        return scored_docs
    
    def deduplicate(
        self,
        documents: List[Tuple[str, Dict, float]],
        similarity_threshold: float = 0.9
    ) -> List[Tuple[str, Dict, float]]:
        """Remove duplicate or very similar documents"""
        if not documents:
            return documents
        
        unique_docs = [documents[0]]
        
        for doc in documents[1:]:
            is_unique = True
            for unique_doc in unique_docs:
                # Simple similarity check based on metadata
                if doc[1].get('id') == unique_doc[1].get('id'):
                    is_unique = False
                    break
            
            if is_unique:
                unique_docs.append(doc)
        
        return unique_docs


class CorrectiveRAG:
    """Implements corrective retrieval-augmented generation"""
    
    def __init__(self, relevance_threshold: float = 0.3):
        self.relevance_threshold = relevance_threshold
    
    def evaluate_retrieval_quality(
        self,
        documents: List[Tuple[str, Dict, float]],
        query: str
    ) -> Dict:
        """
        Evaluate quality of retrieved documents
        
        Returns:
            Dict with quality metrics and recommendations
        """
        if not documents:
            return {
                'quality': 'poor',
                'avg_score': 0,
                'action': 'expand_query'
            }
        
        scores = [score for _, _, score in documents]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        
        if avg_score >= self.relevance_threshold and max_score > 0.5:
            return {
                'quality': 'good',
                'avg_score': avg_score,
                'action': 'proceed'
            }
        elif max_score > self.relevance_threshold:
            return {
                'quality': 'moderate',
                'avg_score': avg_score,
                'action': 'filter_low_scores'
            }
        else:
            return {
                'quality': 'poor',
                'avg_score': avg_score,
                'action': 'expand_query'
            }
    
    def correct_retrieval(
        self,
        documents: List[Tuple[str, Dict, float]],
        query: str,
        query_translation: Dict
    ) -> Tuple[List[Tuple[str, Dict, float]], str]:
        """
        Apply corrective actions based on retrieval quality
        
        Returns:
            Tuple of (corrected_documents, action_taken)
        """
        quality = self.evaluate_retrieval_quality(documents, query)
        
        if quality['action'] == 'proceed':
            return documents, 'no_correction_needed'
        
        elif quality['action'] == 'filter_low_scores':
            # Filter out low-scoring documents
            filtered = [
                (text, meta, score)
                for text, meta, score in documents
                if score >= self.relevance_threshold
            ]
            return filtered, 'filtered_low_scores'
        
        elif quality['action'] == 'expand_query':
            # In a real implementation, this would trigger a new search
            # For now, return original documents with a flag
            return documents, 'needs_query_expansion'
        
        return documents, 'no_action'


class AdvancedRAGPipeline:
    """Complete advanced RAG pipeline"""
    
    def __init__(self, vector_store_manager):
        self.vector_store = vector_store_manager
        self.router = QueryRouter()
        self.translator = QueryTranslator()
        self.constructor = QueryConstructor()
        self.ranker = DocumentRanker()
        self.corrective_rag = CorrectiveRAG()
    
    def process_query(
        self,
        query: str,
        top_k: int = 10
    ) -> Dict:
        """
        Process query through complete advanced RAG pipeline
        
        Returns:
            Dict with results and metadata
        """
        print(f"\n{'='*60}")
        print(f"Processing Query: {query}")
        print(f"{'='*60}")
        
        # Step 1: Route query
        routing = self.router.route_query(query)
        print(f"\n1. Query Routing:")
        print(f"   Type: {routing['query_type']}")
        print(f"   Use CSV: {routing['use_csv']}")
        print(f"   Use PDF: {routing['use_pdf']}")
        print(f"   Priority: {routing['priority']}")
        
        # Step 2: Translate query
        translation = self.translator.translate(query)
        print(f"\n2. Query Translation:")
        print(f"   Entities: {translation['entities']}")
        print(f"   Filters: {translation['filters']}")
        
        # Step 3: Construct query variations
        query_variations = self.constructor.construct_queries(query, translation)
        print(f"\n3. Query Construction:")
        print(f"   Generated {len(query_variations)} query variations")
        
        # Step 4: Retrieve documents
        all_documents = {'csv': [], 'pdf': []}
        
        if routing['use_csv']:
            print(f"\n4a. Retrieving from CSV index...")
            for q_var in query_variations:
                results = self.vector_store.search_csv(q_var, top_k=top_k)
                all_documents['csv'].extend(results)
            
            # Deduplicate CSV results
            all_documents['csv'] = self.ranker.deduplicate(all_documents['csv'])
            print(f"    Retrieved {len(all_documents['csv'])} unique CSV documents")
        
        if routing['use_pdf']:
            print(f"\n4b. Retrieving from PDF index...")
            for q_var in query_variations:
                results = self.vector_store.search_pdf(q_var, top_k=top_k)
                all_documents['pdf'].extend(results)
            
            # Deduplicate PDF results
            all_documents['pdf'] = self.ranker.deduplicate(all_documents['pdf'])
            print(f"    Retrieved {len(all_documents['pdf'])} unique PDF documents")
        
        # Step 5: Rank documents
        print(f"\n5. Ranking documents...")
        if all_documents['csv']:
            all_documents['csv'] = self.ranker.rank_by_relevance(
                all_documents['csv'],
                translation
            )
        
        if all_documents['pdf']:
            all_documents['pdf'] = self.ranker.rank_by_relevance(
                all_documents['pdf'],
                translation
            )
        
        # Step 6: Apply corrective RAG
        print(f"\n6. Applying Corrective RAG...")
        priority_docs = all_documents[routing['priority']]
        corrected_docs, action = self.corrective_rag.correct_retrieval(
            priority_docs,
            query,
            translation
        )
        print(f"   Action taken: {action}")
        
        # Update with corrected docs
        all_documents[routing['priority']] = corrected_docs[:top_k]
        
        # Prepare final results
        results = {
            'query': query,
            'routing': routing,
            'translation': translation,
            'query_variations': query_variations,
            'documents': all_documents,
            'corrective_action': action
        }
        
        print(f"\n{'='*60}")
        print(f"Pipeline Complete")
        print(f"{'='*60}\n")
        
        return results


if __name__ == "__main__":
    # Test components
    router = QueryRouter()
    translator = QueryTranslator()
    constructor = QueryConstructor()
    
    test_queries = [
        "Show me denied claims for diabetes patients last quarter",
        "What is the pre-authorization requirement for MRI scans?",
        "How many claims were processed in Q3 2024?",
        "Tell me about coverage for cancer treatment"
    ]
    
    print("Testing Advanced RAG Components\n")
    print("="*60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Test routing
        routing = router.route_query(query)
        print(f"  Routing: {routing['query_type']}")
        
        # Test translation
        translation = translator.translate(query)
        print(f"  Entities: {translation['entities']}")
        
        # Test construction
        variations = constructor.construct_queries(query, translation)
        print(f"  Variations: {len(variations)}")
        
        print("-"*60)
