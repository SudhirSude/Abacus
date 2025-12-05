"""
PDF Document Processor for RAG
Extracts text from PDF files and creates indexed documents
"""

import os
import json
from typing import List, Dict
from PyPDF2 import PdfReader

class PDFProcessor:
    """Process PDF documents for RAG indexing"""
    
    def __init__(self, pdf_dir='data/pdf_documents', output_dir='data/processed'):
        self.pdf_dir = pdf_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better retrieval
        
        Args:
            text: Input text to chunk
            chunk_size: Target size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            
            # If not at the end, try to break at a sentence or paragraph
            if end < text_length:
                # Look for sentence end
                sentence_end = text.rfind('.', start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for paragraph break
                    para_end = text.rfind('\n', start, end)
                    if para_end != -1 and para_end > start + chunk_size // 2:
                        end = para_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap if end < text_length else text_length
        
        return chunks
    
    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDFs in the directory"""
        print("Processing PDF documents...")
        
        if not os.path.exists(self.pdf_dir):
            print(f"PDF directory not found: {self.pdf_dir}")
            return []
        
        pdf_documents = []
        pdf_files = [f for f in os.listdir(self.pdf_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_dir, pdf_file)
            print(f"Processing: {pdf_file}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                print(f"  Warning: No text extracted from {pdf_file}")
                continue
            
            # Create chunks
            chunks = self.chunk_text(text, chunk_size=1000, overlap=200)
            print(f"  Created {len(chunks)} chunks")
            
            # Create document entries for each chunk
            for i, chunk in enumerate(chunks):
                doc = {
                    'id': f"pdf_{pdf_file.replace('.pdf', '')}_{i}",
                    'type': 'pdf_document',
                    'text': chunk,
                    'metadata': {
                        'source': pdf_file,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'document_type': self._infer_document_type(pdf_file)
                    }
                }
                pdf_documents.append(doc)
        
        print(f"Total PDF document chunks created: {len(pdf_documents)}")
        
        # Save to JSON
        output_file = os.path.join(self.output_dir, 'pdf_documents.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pdf_documents, f, indent=2, ensure_ascii=False)
        
        print(f"Saved PDF documents to: {output_file}")
        
        return pdf_documents
    
    def _infer_document_type(self, filename: str) -> str:
        """Infer document type from filename"""
        filename_lower = filename.lower()
        
        if 'policy' in filename_lower or 'guideline' in filename_lower:
            return 'policy'
        elif 'claim' in filename_lower or 'processing' in filename_lower:
            return 'claims_guide'
        elif 'procedure' in filename_lower or 'medical' in filename_lower:
            return 'medical_reference'
        elif 'disease' in filename_lower or 'coverage' in filename_lower:
            return 'coverage_info'
        elif 'report' in filename_lower or 'quarterly' in filename_lower:
            return 'report'
        else:
            return 'general'

if __name__ == "__main__":
    processor = PDFProcessor()
    processor.process_all_pdfs()
