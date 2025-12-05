"""
ETL Pipeline for Insurance Claims Data
Handles data preprocessing, cleaning, and preparation for RAG indexing
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import re

class ClaimsDataProcessor:
    """ETL processor for insurance claims data"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.processed_dir = os.path.join(data_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
        
    def extract(self):
        """Extract data from CSV files"""
        print("Extracting data from CSV files...")
        
        try:
            self.claims_df = pd.read_csv(os.path.join(self.data_dir, 'claims.csv'))
            self.patients_df = pd.read_csv(os.path.join(self.data_dir, 'patients.csv'))
            self.doctors_df = pd.read_csv(os.path.join(self.data_dir, 'doctors.csv'))
            
            print(f"Loaded {len(self.claims_df)} claims")
            print(f"Loaded {len(self.patients_df)} patients")
            print(f"Loaded {len(self.doctors_df)} doctors")
            
            return True
        except Exception as e:
            print(f"Error extracting data: {e}")
            return False
    
    def transform(self):
        """Transform and enrich data"""
        print("\nTransforming data...")
        
        # Create enriched claims dataset
        self.enriched_claims = self.claims_df.copy()
        
        # Add derived fields
        self.enriched_claims['claim_year'] = pd.to_datetime(
            self.enriched_claims['claim_date']
        ).dt.year
        
        self.enriched_claims['claim_month'] = pd.to_datetime(
            self.enriched_claims['claim_date']
        ).dt.month
        
        self.enriched_claims['claim_month_name'] = pd.to_datetime(
            self.enriched_claims['claim_date']
        ).dt.strftime('%B')
        
        # Calculate approval rate
        self.enriched_claims['was_approved'] = self.enriched_claims['claim_status'].apply(
            lambda x: 1 if x == 'Approved' else 0
        )
        
        # Calculate denial indicator
        self.enriched_claims['was_denied'] = self.enriched_claims['claim_status'].apply(
            lambda x: 1 if x == 'Denied' else 0
        )
        
        # Calculate amount difference
        self.enriched_claims['denied_amount'] = (
            self.enriched_claims['claim_amount'] - 
            self.enriched_claims['approved_amount']
        )
        
        # Age group categorization
        self.enriched_claims['age_group'] = pd.cut(
            self.enriched_claims['patient_age'],
            bins=[0, 25, 40, 55, 65, 100],
            labels=['18-25', '26-40', '41-55', '56-65', '65+']
        )
        
        # Claim amount category
        self.enriched_claims['claim_amount_category'] = pd.cut(
            self.enriched_claims['claim_amount'],
            bins=[0, 1000, 5000, 20000, 50000, float('inf')],
            labels=['Low (<$1K)', 'Medium ($1K-$5K)', 'High ($5K-$20K)', 
                   'Very High ($20K-$50K)', 'Extreme (>$50K)']
        )
        
        print(f"Transformed {len(self.enriched_claims)} claim records")
        
        # Create aggregated summaries
        self._create_aggregations()
        
        return True
    
    def _create_aggregations(self):
        """Create aggregated datasets for faster querying"""
        print("Creating aggregated datasets...")
        
        # Disease-wise aggregations
        self.disease_summary = self.enriched_claims.groupby('disease').agg({
            'claim_id': 'count',
            'claim_amount': ['sum', 'mean'],
            'approved_amount': ['sum', 'mean'],
            'was_denied': 'sum',
            'was_approved': 'sum'
        }).reset_index()
        
        self.disease_summary.columns = [
            'disease', 'total_claims', 'total_claim_amount', 'avg_claim_amount',
            'total_approved_amount', 'avg_approved_amount', 'denied_claims', 'approved_claims'
        ]
        
        # Quarterly aggregations
        self.quarterly_summary = self.enriched_claims.groupby(['year', 'quarter']).agg({
            'claim_id': 'count',
            'claim_amount': ['sum', 'mean'],
            'approved_amount': ['sum', 'mean'],
            'was_denied': 'sum',
            'was_approved': 'sum'
        }).reset_index()
        
        self.quarterly_summary.columns = [
            'year', 'quarter', 'total_claims', 'total_claim_amount', 'avg_claim_amount',
            'total_approved_amount', 'avg_approved_amount', 'denied_claims', 'approved_claims'
        ]
        
        # Doctor specialty aggregations
        self.specialty_summary = self.enriched_claims.groupby('doctor_specialty').agg({
            'claim_id': 'count',
            'claim_amount': ['sum', 'mean'],
            'was_denied': 'sum',
            'was_approved': 'sum'
        }).reset_index()
        
        self.specialty_summary.columns = [
            'specialty', 'total_claims', 'total_claim_amount', 'avg_claim_amount',
            'denied_claims', 'approved_claims'
        ]
        
        print("Aggregations created successfully")
    
    def create_text_documents(self):
        """Create text documents for RAG indexing"""
        print("\nCreating text documents for RAG...")
        
        documents = []
        
        # Create individual claim documents
        for idx, row in self.enriched_claims.iterrows():
            doc = {
                'id': f"claim_{row['claim_id']}",
                'type': 'claim',
                'text': self._create_claim_text(row),
                'metadata': {
                    'claim_id': row['claim_id'],
                    'patient_id': row['patient_id'],
                    'doctor_id': row['doctor_id'],
                    'disease': row['disease'],
                    'procedure': row['procedure'],
                    'claim_status': row['claim_status'],
                    'claim_date': row['claim_date'],
                    'quarter': row['quarter'],
                    'year': int(row['year']),
                    'claim_amount': float(row['claim_amount']),
                    'approved_amount': float(row['approved_amount']),
                    'denial_reason': row['denial_reason']
                }
            }
            documents.append(doc)
        
        # Create disease summary documents
        for idx, row in self.disease_summary.iterrows():
            doc = {
                'id': f"disease_summary_{idx}",
                'type': 'disease_summary',
                'text': self._create_disease_summary_text(row),
                'metadata': {
                    'disease': row['disease'],
                    'total_claims': int(row['total_claims']),
                    'total_claim_amount': float(row['total_claim_amount']),
                    'avg_claim_amount': float(row['avg_claim_amount']),
                    'denied_claims': int(row['denied_claims']),
                    'approved_claims': int(row['approved_claims'])
                }
            }
            documents.append(doc)
        
        # Create quarterly summary documents
        for idx, row in self.quarterly_summary.iterrows():
            doc = {
                'id': f"quarterly_summary_{row['year']}_{row['quarter']}",
                'type': 'quarterly_summary',
                'text': self._create_quarterly_summary_text(row),
                'metadata': {
                    'year': int(row['year']),
                    'quarter': row['quarter'],
                    'total_claims': int(row['total_claims']),
                    'total_claim_amount': float(row['total_claim_amount']),
                    'denied_claims': int(row['denied_claims']),
                    'approved_claims': int(row['approved_claims'])
                }
            }
            documents.append(doc)
        
        print(f"Created {len(documents)} text documents for indexing")
        self.documents = documents
        
        return documents
    
    def _create_claim_text(self, row):
        """Create natural language text for a single claim"""
        text = f"""
Claim ID: {row['claim_id']}
Patient: {row['patient_name']}, {row['patient_age']} years old, {row['patient_gender']}, residing in {row['patient_state']}
Insurance Plan: {row['insurance_plan']}
Doctor: {row['doctor_name']}, Specialty: {row['doctor_specialty']}
Network Status: {row['network_status']}
Hospital: {row['hospital']}
Disease/Condition: {row['disease']}
Procedure: {row['procedure']}
Service Date: {row['service_date']}
Claim Date: {row['claim_date']}
Processed Date: {row['processed_date']}
Claim Amount: ${row['claim_amount']:,.2f}
Approved Amount: ${row['approved_amount']:,.2f}
Claim Status: {row['claim_status']}
Denial Reason: {row['denial_reason']}
Processing Time: {row['processing_days']} days
Quarter: {row['quarter']} {row['year']}
"""
        return text.strip()
    
    def _create_disease_summary_text(self, row):
        """Create summary text for disease aggregation"""
        approval_rate = (row['approved_claims'] / row['total_claims'] * 100) if row['total_claims'] > 0 else 0
        denial_rate = (row['denied_claims'] / row['total_claims'] * 100) if row['total_claims'] > 0 else 0
        
        text = f"""
Disease Summary: {row['disease']}
Total Claims: {int(row['total_claims'])}
Total Claim Amount: ${row['total_claim_amount']:,.2f}
Average Claim Amount: ${row['avg_claim_amount']:,.2f}
Total Approved Amount: ${row['total_approved_amount']:,.2f}
Average Approved Amount: ${row['avg_approved_amount']:,.2f}
Approved Claims: {int(row['approved_claims'])} ({approval_rate:.1f}%)
Denied Claims: {int(row['denied_claims'])} ({denial_rate:.1f}%)
"""
        return text.strip()
    
    def _create_quarterly_summary_text(self, row):
        """Create summary text for quarterly aggregation"""
        approval_rate = (row['approved_claims'] / row['total_claims'] * 100) if row['total_claims'] > 0 else 0
        denial_rate = (row['denied_claims'] / row['total_claims'] * 100) if row['total_claims'] > 0 else 0
        
        text = f"""
Quarterly Claims Summary: {row['quarter']} {int(row['year'])}
Total Claims: {int(row['total_claims'])}
Total Claim Amount: ${row['total_claim_amount']:,.2f}
Average Claim Amount: ${row['avg_claim_amount']:,.2f}
Total Approved Amount: ${row['total_approved_amount']:,.2f}
Average Approved Amount: ${row['avg_approved_amount']:,.2f}
Approved Claims: {int(row['approved_claims'])} ({approval_rate:.1f}%)
Denied Claims: {int(row['denied_claims'])} ({denial_rate:.1f}%)
"""
        return text.strip()
    
    def load(self):
        """Load processed data to storage"""
        print("\nSaving processed data...")
        
        # Save enriched claims
        self.enriched_claims.to_csv(
            os.path.join(self.processed_dir, 'enriched_claims.csv'),
            index=False
        )
        
        # Save aggregations
        self.disease_summary.to_csv(
            os.path.join(self.processed_dir, 'disease_summary.csv'),
            index=False
        )
        
        self.quarterly_summary.to_csv(
            os.path.join(self.processed_dir, 'quarterly_summary.csv'),
            index=False
        )
        
        self.specialty_summary.to_csv(
            os.path.join(self.processed_dir, 'specialty_summary.csv'),
            index=False
        )
        
        # Save documents as JSON
        with open(os.path.join(self.processed_dir, 'documents.json'), 'w') as f:
            json.dump(self.documents, f, indent=2)
        
        print(f"Saved processed data to {self.processed_dir}")
        print(f"Total documents: {len(self.documents)}")
        
        return True
    
    def run_etl(self):
        """Run complete ETL pipeline"""
        print("="*60)
        print("STARTING ETL PIPELINE")
        print("="*60)
        
        if not self.extract():
            print("ETL pipeline failed at extraction stage")
            return False
        
        if not self.transform():
            print("ETL pipeline failed at transformation stage")
            return False
        
        self.create_text_documents()
        
        if not self.load():
            print("ETL pipeline failed at loading stage")
            return False
        
        print("="*60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("="*60)
        
        return True

if __name__ == "__main__":
    processor = ClaimsDataProcessor()
    processor.run_etl()
